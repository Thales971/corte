# Tutorial CORTE V2

Guia pra usar o CORTE do zero até o print “parece produto”.

## 1. Subir o painel

```powershell
cd corte
.\.venv\Scripts\Activate.ps1
python -m corte
```

Ou dois cliques em `run.bat`.

Você vai ver o banner verde, o status e o log. Se o visual quebrar, abre no Windows Terminal, não no cmd.

## 2. Print da tela inteira

1. Aperte `F`.
2. O arquivo cai em `Pictures\CORTE` com nome `tela_AAAA-MM-DD_HH-MM-SS.png`.
3. A imagem já vai pra área de transferência. Cola com `Ctrl+V` no Discord, no Word, no grupo.

Quer pegar um menu que some quando o CORTE ganha foco? Aperte `D` até o delay ficar 3s ou 5s, depois `F`.

## 3. Recorte com overlay

1. Aperte `R`. A tela escurece.
2. Move o mouse: a lupa mostra o pixel e o hex.
3. Arrasta a região. O pedaço escolhido fica nítido, o resto continua escuro.
4. Segura `SHIFT` se quiser quadrado (ícone, avatar, thumb).
5. `ENTER` ou duplo clique confirma. `ESC` cancela.

O arquivo nasce como `recorte_…`.

## 4. Editor (a parte que o V1 não tinha)

Aperte `A` com uma imagem recente.

Ferramentas na barra:

- **Seta** — aponta o bug, o botão, o número da questão
- **Caixa / Elipse** — destaca área
- **Caneta** — rabisco livre
- **Marca** — marca-texto sem tapar o que está embaixo
- **Texto** — label curto
- **Blur / Pixel** — esconde nome, nota, foto, placa
- **Nº** — passos de tutorial (1, 2, 3…)
- **Cortar** — refina o recorte depois
- **Moldura** — padding + canto + sombra no fundo `#0B0F0C`
- **Copiar / Salvar**

Atalhos: `Ctrl+Z` desfaz, `Ctrl+S` salva, `Ctrl+C` copia, `ESC` fecha.

O save vira `editado_…` e também copia a imagem.

## 5. OCR

1. Tira o print (ou abre um já existente).
2. Aperte `O`.
3. O texto aparece no log e vai pra área de transferência.

Funciona melhor em slide, enunciado, terminal e código. Foto torta de caderno ainda é loteria — o V2 pré-processa contraste, mas não faz milagre.

Precisa do Tesseract instalado com **Portuguese + English**.

## 6. Gravação

- `G` começa.
- `Espaço` pausa (bom pra pular a parte que você só fica procurando a janela).
- `G` ou `ESC` para.
- Sai `video_….mp4` na mesma pasta.

É captura de tela ~24 fps. Pra aula de 40 minutos, usa o OBS.

## 7. Histórico, monitor, pasta

- `H` lista as últimas capturas no log e marca a mais nova como “última”.
- `M` anda pelos monitores. O índice `0` costuma ser “todos juntos”.
- `P` abre o Explorer já na pasta do CORTE.
- `S` grava delay, monitor, fps e moldura em `corte.settings.json`.

## 8. CLI sem painel

Útil pra atalho do Windows ou script:

```powershell
python -m corte shot --delay 3
python -m corte region
python -m corte edit
python -m corte ocr
python -m corte record --seconds 8
python -m corte tutorial
```

Pode criar um atalho em `shell:startup` ou no desktop apontando pra `run.bat`.

## 9. Fluxo bom pra prova / aula / bug

1. `D` em 3s.
2. `R`, recorta o enunciado ou a tela do erro.
3. `A` → seta no ponto + blur em dado pessoal.
4. **Moldura** se for postar.
5. `Ctrl+V` no lugar que precisa.

Três teclas. Sem abrir o Snipping Tool da Microsoft, sem borda feia, sem copiar path de arquivo que ninguém consegue abrir.

## 10. Se der ruim

| Sintoma | O que olhar |
| --- | --- |
| Overlay não abre | Python instalado **com Tcl/Tk**. Reinstala o oficial e marca a opção. |
| Visual quebrado | Windows Terminal. |
| OCR explode | Tesseract no PATH + idiomas por e eng. |
| Não cola a imagem | O CORTE cai no path. Confere se não está colando num campo só-texto. |
| Gravação preta | Monitor certo com `M`. Fecha o game em fullscreen exclusivo. |
| Permissão de laboratório | O CORTE não mexe em política do PC. Se o lab bloqueia captura, nenhum app de print passa. |
