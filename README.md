# CORTE V2.1

Snipping Tool pelo terminal — agora com extração de texto que escolhe a melhor leitura sozinha.

Print da tela, recorte com lupa, anotações, moldura, gravação com pausa e OCR em PT+EN com confiança. Painel visual no Windows Terminal.

```text
 ██████╗ ██████╗ ██████╗ ████████╗███████╗
██╔═════██╔═══██╗██╔══██╗╚══██╔══██╔═════
██║     ██║   ██║██████╔╝   ██║   █████╗
██║     ██║   ██║██╔══██╗   ██║   ██╔══╝
╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝
                 v 2 . 1 . 0
```

[![Python](https://img.shields.io/badge/python-3.11+-7CFFB2?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F6A43?style=flat-square)](LICENSE)
[![Senai Valinhos](https://img.shields.io/badge/SENAI-Valinhos-0B0F0C?style=flat-square)](https://github.com/Thales971)

## Extração de texto (o pulo do 2.1)

`O` no painel ou `python -m corte ocr`.

O CORTE não manda o PNG cru pro Tesseract. Ele:

1. detecta se o print é **fundo escuro** (terminal, slide, o próprio painel) e inverte
2. sobe contraste, tira ruído e dobra a resolução se o recorte for pequeno
3. tenta mais de um modo de página (bloco, coluna, automático)
4. escolhe a leitura com **maior confiança**
5. copia o texto e grava um `.txt` ao lado da imagem

```powershell
python -m corte ocr
python -m corte ocr .\Pictures\CORTE\recorte_2026-08-30.png
python -m corte ocr .\slide.png --json --save
```

`--json` mostra confiança, idioma e quantidade de palavras. `--save` força o `.txt`. `--no-prep` manda a imagem crua.

Precisa do [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) com **Portuguese + English** e PATH. Sem o motor, o resto do CORTE segue normal.

Funciona bem em slide, enunciado, terminal e código. Foto torta de caderno ainda é loteria.

## Visual

Painel escuro floresta + menta (`#07110C` / `#7CFFB2`). Status com borda viva, botões com borda alta, log com scroll na mesma paleta. Overlay de recorte com lupa 8× e hex. Editor com barra no mesmo verde.

Abre no [Windows Terminal](https://aka.ms/terminal). O cmd antigo quebra o desenho.

## Tutorial de 60 segundos

1. Dois cliques em `run.bat` (ou `python -m corte`).
2. **F** tela cheia ou **R** recorte (lupa + hex, `ENTER` confirma).
3. **A** editor: seta no erro, blur no nome, número nos passos.
4. **Moldura** se for mandar pra alguém. **C** cola a imagem.
5. **O** extrai o texto, copia e grava o `.txt`. **G** grava a tela. **?** abre o guia.

Arquivos: `%USERPROFILE%\Pictures\CORTE`.

Guia completo: [TUTORIAL.md](TUTORIAL.md).

## CLI

```powershell
python -m corte ocr .\foto.png --json --save
python -m corte shot --delay 3
python -m corte tutorial
```

## Testes

```powershell
python -m pytest -q
```

## Licença

MIT © Thales Vitor Boehm
