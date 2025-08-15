from setuptools import setup, find_packages

setup(
    name='themes_dark_cyan',
    version='1.2.0',
    author='IA (Sistema de Intres)',
    author_email='system.ai.of.interest@gmail.com',
    description='esta libreria fue creada por IA Sistema de Intres',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.youtube.com/@IA.Sistema.de.Interes',  # Opcional, pero recomendado
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'tqdm',
        'Pillow',
        'IPython',
    ],
)