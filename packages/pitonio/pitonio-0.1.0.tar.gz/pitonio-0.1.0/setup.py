from setuptools import setup, find_packages

setup(
    name='pitonio',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.7',
    author='Decaptado',
    description="Python 'traduzido' pra PT-BR com o Tkinter incluido pra simplificar",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/aaaa560/Pitonio",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
