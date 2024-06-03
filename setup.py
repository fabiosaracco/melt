import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='melt',
    version='0.1.0', 
    author='Fabio',
    author_email='f.sarawalk@gmail.com',
    description='??? based on https://www.mdpi.com/2143956',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/fabiosaracco/melt',
    license='MIT',
    packages=['melt'],
    install_requires=['numpy','nltk','pandas','tqdm','bicm'],
)
