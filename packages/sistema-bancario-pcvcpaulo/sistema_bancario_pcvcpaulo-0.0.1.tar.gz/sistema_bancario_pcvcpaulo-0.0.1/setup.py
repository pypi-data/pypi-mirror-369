from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read() 

setup(
    # Metadados básicos
    name="sistema_bancario_pcvcpaulo",
    version="0.0.1",
    author="PCVCPAULO",
    author_email="pcvcpaulo@gmail.com",

    # Descrição do projeto
    description="Simula um sistema bancário.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Configuração de pacotes
    packages=['sistema_bancario_pcvcpaulo'], # Nome do pacote Python
    python_dir={'': '.'}, # Procura o pacote no diretório raiz
    python_requires='>=3.8',

    # URLs do projeto
    url="https://github.com/PCVCPAULO/project_SistemaBancario_Python",

    keywords="banco financeiro simulador",

    entry_points={
        'console_scripts': [
            'sistema-banario=sistema_bancario_pcvcpaulo.sistema_bancario:main',
        ],
    }

)
