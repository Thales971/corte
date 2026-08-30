# Tutorial CORTE V2.1

Guia pra usar o CORTE do zero até o print “parece produto” e o texto extraído.

## 1. Subir o painel

```powershell
cd corte
.\.venv\Scripts\Activate.ps1
python -m corte
```

Ou dois cliques em `run.bat`. Abre no Windows Terminal.

## 2. Print / recorte / editor

- `F` tela cheia
- `R` overlay: lupa + hex, SHIFT quadrado, ENTER confirma
- `A` editor: seta, caixa, marca, blur, pixel, número, moldura
- `C` copia a imagem

## 3. Extração de texto

1. Tira o print.
2. Aperte `O`.
3. O painel mostra o texto + a % de certeza.
4. O texto vai pra área de transferência e nasce um `.txt` ao lado do PNG.

```powershell
python -m corte ocr
python -m corte ocr .\slide.png --json --save
```

O motor inverte UI escura, sobe contraste e escolhe o melhor modo de página. Precisa do Tesseract com Portuguese + English.

## 4. Gravação

`G` começa, Espaço pausa, `G` ou ESC para.

## 5. Pasta e settings

Arquivos em `Pictures\CORTE`. `S` grava `corte.settings.json`.
