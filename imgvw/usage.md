# Image Viewer

Ferramenta para visualizar e "marcar" imagens.

Essa feramenta escreve na tela informações no formato ```json``` para alimentar
```FastSAM``` e segmentar imagens.

## Uso:

```
usage: Annotate Images [-h] [-p P | -l L]

options:
  -h, --help  show this help message and exit
  -p P        path to images
  -l L        load annotations
```

- ```left-double-click``` desenha ponto
- ```1-9``` seleciona classes
- ```n``` próxima imagem
- ```p``` imagem anterior
- ```q``` sai
