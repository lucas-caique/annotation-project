# Street View Downloader

Uma ferramenta para baixar panoramas do Google Streetview

Baseado na API (streetview)[https://github.com/robolyst/streetview/tree/master/streetview].

## Uso:

```
	usage: stvw_dwld.py [-h] -k API_KEY [-r coord coord coord coord]
						[-d DIRECTORY] [-n N] [-q {1,2,3,4,5}] [-y YEAR]

	options:
	  -h, --help            show this help message and exit
	  -k API_KEY, --api_key API_KEY
							your GOOGLE API key
	  -r coord coord coord coord
							defines the boundery rectangle for search
	  -d DIRECTORY          directory to save images
	  -n N                  number of panoramas to download
	  -q {1,2,3,4,5}, --quality {1,2,3,4,5}
							quality of panoramas (highest = 5)
	  -y YEAR, --year YEAR  only allows panoramas taken in 'year' or later
```

## Notas:

- Script faz uma busca aleatória por panoramas
- Opção ```-r``` toma duas 2 coordenadas (latitude e longitude) que define um retângulo onde será feita as buscas
- Por padrão, a busca é feita na região metropolitana de Porto Alegre
- É necessário ter um conta no Google Cloud e uma chave da Street View Static API
- Além das imagens, é gerado um arquivo ```.csv``` com metadados dos panoramas
- Recomendado salvar imagens em pastas diferentes a cada uso
