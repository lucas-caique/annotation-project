#### Instalando FastSAM

As seguintes intruções estão presentes no [repositório oficial](https://github.com/CASIA-IVA-Lab/FastSAM.git)

```
git clone https://github.com/CASIA-IVA-Lab/FastSAM.git
cd FastSAM
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git
python3 -m venv venv
pip install git+https://github.com/CASIA-IVA-Lab/FastSAM.git
cp -r FastSAM/fastsam venv/lib/python3.11/site-packages/
```

Após, baixe um dos [modelos](https://drive.google.com/file/d/1m1sjY4ihXBU1fZXdQ-Xdj-mDltW-2Rqv/view?usp=sharing). De preferência, salve em ```./weights/``` (script buscará nessa pasta por padrão).
