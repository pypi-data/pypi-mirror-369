from setuptools import setup, find_packages

setup(
    # El nombre de mi paquete en PyPI.
    name="gestion_banco_taipe",
    # Versión del paquete. 
    version="1.0.0",
    # Mi nombre y correo electrónico.    
    author="Ángel Taipe",
    author_email="angeltaipe364@gmail.com",
    # Descripción del paquete.
    description="Paquete para gestión bancaria con POO en Python",
    # La descripción extraída de mi README.md.
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    # Esto encuentra automáticamente el paquete que cree.
    packages=find_packages(),
    # Versión de Python.
    python_requires=">=3.7",
)
