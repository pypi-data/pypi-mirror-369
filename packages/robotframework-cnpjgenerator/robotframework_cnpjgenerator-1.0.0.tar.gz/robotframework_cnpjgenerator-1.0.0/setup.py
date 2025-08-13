from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robotframework-cnpjgenerator",
    version="1.0.0",
    author="Seu Nome",
    author_email="seu.email@example.com",
    description="Biblioteca Robot Framework para geração e validação de CNPJs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/robotframework-cnpjgenerator",
    packages=find_packages(),
    install_requires=[
        "robotframework >= 4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
    ],
    python_requires='>=3.8',
    keywords='robotframework testing brazil cnpj generator',
    project_urls={
        "Documentation": "https://seu-usuario.github.io/robotframework-cnpjgenerator/",
        "Source": "https://github.com/seu-usuario/robotframework-cnpjgenerator",
    },
)