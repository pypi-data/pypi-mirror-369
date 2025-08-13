from setuptools import setup, find_packages
from pathlib import Path

# Garante que os caminhos sejam relativos ao setup.py
BASE_DIR = Path(__file__).resolve().parent

# Lê README.md
with open(BASE_DIR / 'README.md', 'r', encoding='utf-8') as f:
    page_description = f.read()

# Lê requirements.txt se existir
requirements_path = BASE_DIR / 'requirements.txt'
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = f.read().splitlines()
else:
    requirements = []

setup(
    name='image_processing_thaiza_dantas_tools',  # nome do pacote no PyPI
    version='0.0.1',  # versão do pacote
    author='Thaiza',
    description='Image Processing Package using Skimage',
    long_description=page_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thaiza-d/image_processing_thaiza_dantas_tools',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.5',
)
