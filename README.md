# CORTE

Snipping Tool pelo terminal.

Print da tela, recorte com overlay, gravação e OCR — painel visual no Windows Terminal.

```text
 ██████╗ ██████╗ ██████╗ ████████╗███████╗
██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝
██║     ██║   ██║██████╔╝   ██║   █████╗
██║     ██║   ██║██╔══██╗   ██║   ██╔══╝
╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
```

[![Python](https://img.shields.io/badge/python-3.11+-7CFFB2?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F6A43?style=flat-square)](LICENSE)
[![Senai Valinhos](https://img.shields.io/badge/SENAI-Valinhos-0B0F0C?style=flat-square)](https://github.com/Thales971)

## O que faz

| Atalho | Ação |
| --- | --- |
| `F` | print da tela inteira |
| `R` | overlay fullscreen — arrasta a região, `ENTER` confirma, `ESC` cancela |
| `G` | começa / para gravação MP4 |
| `O` | OCR da última imagem (português + inglês) |
| `P` | abre a pasta de saídas |
| `C` | copia o caminho |
| `Q` | sai |

Arquivos vão para `%USERPROFILE%\Pictures\CORTE`.

## Requisitos

- Windows 10/11
- Python 3.11+ (oficial, com Tcl/Tk marcado no instalador)
- [Windows Terminal](https://aka.ms/terminal) — o cmd antigo deixa o visual quebrado
- Tesseract OCR **só se for usar extração de texto**
  - [instalador UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - marque Portuguese + English
  - deixe “Add to PATH” marcado

## Instalação

```powershell
git clone https://github.com/Thales971/corte.git
cd corte
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m corte
```

Atalho preguiçoso: dois cliques em `run.bat`.

## CLI

Sem abrir o painel:

```powershell
python -m corte shot
python -m corte region
python -m corte record --seconds 10
python -m corte ocr
python -m corte ocr .\foto.png
python -m corte pasta
```

## Stack

- [Textual](https://textual.textualize.io/) — painel no terminal
- [mss](https://github.com/BoboTiG/python-mss) + Pillow — captura
- OpenCV — gravação
- Tesseract via pytesseract — OCR
- Tkinter — overlay de recorte

## Observações

- A gravação é ~20 fps (`mp4v`). Serve para aula, bug e tutorial curto — não substitui OBS.
- Print `F` e gravação usam o monitor virtual 0 (todos juntos). O recorte `R` cobre a área virtual inteira.
- Feito para o seu PC. Não altera política, HOSTS, antivírus nem software de laboratório.

## Licença

MIT © Thales Torsatto
