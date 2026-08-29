from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import mss
import numpy as np

from corte.paths import stamp


@dataclass
class RecorderStatus:
    running: bool
    path: Path | None
    frames: int
    elapsed: float
    fps: float


class ScreenRecorder:
    def __init__(self, monitor_index: int = 0, fps: int = 20) -> None:
        self.monitor_index = monitor_index
        self.fps = max(8, min(fps, 30))
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self.status = RecorderStatus(False, None, 0, 0.0, float(self.fps))

    def start(self) -> Path:
        if self.status.running:
            raise RuntimeError("Já existe uma gravação em andamento.")
        path = stamp("video", "mp4")
        self._stop.clear()
        with self._lock:
            self.status = RecorderStatus(True, path, 0, 0.0, float(self.fps))
        self._thread = threading.Thread(target=self._loop, args=(path,), daemon=True)
        self._thread.start()
        return path

    def stop(self) -> RecorderStatus:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=8)
        with self._lock:
            self.status.running = False
            return self.status

    def snapshot(self) -> RecorderStatus:
        with self._lock:
            return RecorderStatus(
                self.status.running,
                self.status.path,
                self.status.frames,
                self.status.elapsed,
                self.status.fps,
            )

    def _fail(self) -> None:
        with self._lock:
            self.status.running = False

    def _loop(self, path: Path) -> None:
        try:
            sct_cm = mss.mss()
        except Exception:
            self._fail()
            return
        with sct_cm as sct:
            monitors = sct.monitors
            index = self.monitor_index if 0 <= self.monitor_index < len(monitors) else 0
            monitor = monitors[index]
            width, height = monitor["width"], monitor["height"]
            if width % 2:
                width -= 1
            if height % 2:
                height -= 1

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(path), fourcc, float(self.fps), (width, height))
            interval = 1.0 / self.fps
            started = time.perf_counter()
            frames = 0
            try:
                while not self._stop.is_set():
                    tick = time.perf_counter()
                    raw = sct.grab(monitor)
                    frame = np.frombuffer(raw.bgra, dtype=np.uint8)
                    frame = frame.reshape((raw.height, raw.width, 4))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    frame = frame[:height, :width]
                    writer.write(frame)
                    frames += 1
                    elapsed = time.perf_counter() - started
                    with self._lock:
                        self.status.frames = frames
                        self.status.elapsed = elapsed
                    sleep_for = interval - (time.perf_counter() - tick)
                    if sleep_for > 0:
                        time.sleep(sleep_for)
            finally:
                writer.release()
                elapsed = time.perf_counter() - started
                with self._lock:
                    self.status.frames = frames
                    self.status.elapsed = elapsed
                    self.status.running = False
                    if elapsed > 0:
                        self.status.fps = frames / elapsed
