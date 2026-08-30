# CORTE V2

Snipping Tool pelo terminal — agora com editor, lupa, moldura e OCR que não passa vergonha.

Print da tela, recorte com overlay de verdade, anotações, gravação com pausa e OCR em PT+EN. Painel visual no Windows Terminal.

```text
 ██████╗ ██████╗ ██████╗ ████████╗███████╗
██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝
██║     ██║   ██║██████╔╝   ██║   █████╗
██║     ██║   ██║██╔══██╗   ██║   ██╔══╝
╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
                 v 2 . 0 . 0
```

[![Python](https://img.shields.io/badge/python-3.11+-7CFFB2?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F6A43?style=flat-square)](LICENSE)
[![Senai Valinhos](https://img.shields.io/badge/SENAI-Valinhos-0B0F0C?style=flat-square)](https://github.com/Thales971)

## Por que V2

O V1 já tirava print, recortava, gravava e lia texto. O V2 trata o print como peça final, não como arquivo cru.

| V1 | V2 |
| --- | --- |
| Overlay só arrasta retângulo | Lupa 8×, hex do pixel, tamanho ao vivo, Shift = quadrado, duplo clique confirma |
| Copia o caminho do arquivo | Copia a **imagem** pra colar no Discord, Word, WhatsApp Web |
| Sem editor | Editor com seta, caixa, elipse, caneta, marca-texto, texto, blur, pixel, passos numerados, corte |
| PNG cru | Moldura com padding, canto arredondado e sombra (o “print bonito” do CleanShot) |
| OCR cru no Tesseract | Pré-processa contraste + upscale + limpeza antes de ler |
| Grava ou para | Pausa com Espaço, FPS 24, monitor escolhido |
| Sem memória | Delay 0/3/5/10, histórico, settings em JSON, tutorial no próprio painel |

Não é OBS. Não é Photoshop. É a ferramenta que você abre em 1 segundo quando o professor passou o slide, o bug apareceu, ou o grupo pediu o print da tela.

## Tutorial de 60 segundos

1. Dois cliques em `run.bat` (ou `python -m corte`).
2. Aperte **F** pra tela cheia ou **R** pra recortar.
3. No recorte: arrasta, olha a lupa, `ENTER` confirma.
4. Aperte **A** e marca o que importa (seta no erro, blur no nome, número nos passos).
5. **Moldura** se for mandar pra alguém. **Copiar** cola a imagem direto.
6. **O** lê o texto da última imagem. **G** grava. **?** abre este guia no painel.

Arquivos vão para `%USERPROFILE%\\Pictures\\CORTE`.

Guia completo: [TUTORIAL.md](TUTORIAL.md).

## Atalhos

| Tecla | Ação |
| --- | --- |
| `F` | print da tela do monitor atual |
| `R` | overlay de recorte |
| `A` | editor de anotações da última imagem |
| `G` | começa / para gravação MP4 |
| `Espaço` | pausa / retoma a gravação |
| `O` | OCR da última imagem (português + inglês) |
| `C` | copia a imagem (cai no path se o SO recusar) |
| `P` | abre a pasta de saídas |
| `D` | cicla delay 0 → 3 → 5 → 10 s |
| `M` | cicla o monitor |
| `H` | lista o histórico no log |
| `S` | salva `corte.settings.json` |
| `?` | tutorial no painel |
| `Q` | sai |
| `ESC` | para a gravação ou sai |

### Dentro do overlay

| Tecla / gesto | Ação |
| --- | --- |
| Arrastar | escolhe a região (preview nítido, resto escurecido) |
| `SHIFT` | trava quadrado |
| Mover o mouse | lupa 8× + hex + coordenada |
| `ENTER` ou duplo clique | confirma |
| `ESC` | cancela |

### Dentro do editor

| Atalho | Ação |
| --- | --- |
| `Ctrl+Z` / `Ctrl+Y` | desfaz / refaz |
| `Ctrl+S` | salva |
| `Ctrl+C` | copia a imagem |
| `ESC` | fecha |

## Requisitos

- Windows 10/11 (o alvo). Linux/macOS rodam o painel; captura e overlay dependem de display.
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
python -m corte shot --delay 3 --monitor 1
python -m corte region
python -m corte edit
python -m corte edit .\foto.png
python -m corte record --seconds 10
python -m corte ocr
python -m corte ocr .\foto.png
python -m corte historico
python -m corte pasta
python -m corte tutorial
```

## Settings

Na primeira saída o CORTE grava `Pictures\\CORTE\\corte.settings.json`:

```json
{
  "delay_seconds": 0,
  "monitor_index": 0,
  "fps": 24,
  "image_format": "png",
  "jpeg_quality": 92,
  "copy_image": true,
  "open_editor_after_shot": true,
  "frame_padding": 48,
  "frame_radius": 18,
  "frame_shadow": 28,
  "frame_background": "#0B0F0C",
  "ocr_lang": "por+eng"
}
```

`D` e `M` no painel mudam delay e monitor na hora. `S` persiste.

## Stack

- [Textual](https://textual.textualize.io/) — painel no terminal
- [mss](https://github.com/BoboTiG/python-mss) + Pillow — captura e editor
- OpenCV — gravação
- Tesseract via pytesseract — OCR
- Tkinter — overlay de recorte + editor de anotações
- ctypes / wl-copy / osascript — clipboard de imagem sem pywin32

## Testes

```powershell
pip install -r requirements.txt pytest
python -m pytest -q
```

Os testes cobrem paths, settings, moldura, blur, pixel e o preparo do OCR. Overlay e captura pedem display real — isso se testa no seu PC, não em CI cego.

## Observações

- A gravação é ~24 fps (`mp4v`). Serve para aula, bug e tutorial curto — não substitui OBS.
- Print `F` e gravação usam o monitor escolhido com `M`. Recorte `R` cobre a área virtual inteira.
- Feito para o seu PC. Não altera política, HOSTS, antivírus nem software de laboratório.

## Licença

MIT © Thales Vitor Boehm
