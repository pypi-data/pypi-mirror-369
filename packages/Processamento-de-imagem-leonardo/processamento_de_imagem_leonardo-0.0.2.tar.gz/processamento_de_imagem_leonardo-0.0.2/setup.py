from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_dedscription = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Processamento_de_imagem_leonardo",
    version="0.0.2",
    author="Leonardo_José",
    description="Image processing package using skimage",
    long_description=page_dedscription,
    long_description_content_type="text/markdown",
    url="https://github.com/Leonardojnss/Pacote-de-Python.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)