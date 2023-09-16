#### Instalando FastSAM

As seguintes intruções foram adaptadas do [repositório oficial](https://github.com/CASIA-IVA-Lab/FastSAM.git) Eles recomendam o conda pra gerenciar projeto mas não consegui rodar nada fora da pasta do ```FastSAM/```. Seguintes passos resolveram isso.


1. Numa pasta qualquer crie um ambiente virtual

```
python3 -m venv venv
```

2. Clone e instale requisitos do FastSAM

```
git clone https://github.com/CASIA-IVA-Lab/FastSAM.git
cd FastSAM
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git
```

3. Adicione fastsam às bibliotecas do ambiente virtual

```
pip install git+https://github.com/CASIA-IVA-Lab/FastSAM.git
cp -r fastsam ../venv/lib/python3.11/site-packages/
```


Após, baixe um dos [modelos](https://drive.google.com/file/d/1m1sjY4ihXBU1fZXdQ-Xdj-mDltW-2Rqv/view?usp=sharing). De preferência, salve em ```./weights/``` (script buscará nessa pasta por padrão).


#### Exemplo de uso:

Supondo que imagens de entrada e anotação feita pelo imgvw.py estão em ```images/```

```
python3 anntt.py -i images/ -o images/output/ -p images/ann
```