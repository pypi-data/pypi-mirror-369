from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gestion_banco_vega_canarejo',
    version='0.1.1',
    author='Alfonso Eduardo Vega Canarejo',
    author_email='aovega.1b@gmail.com',
    description='Paquete para gestión de operaciones bancarias básicas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
