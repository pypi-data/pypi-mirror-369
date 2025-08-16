from setuptools import setup,find_packages

setup(
    name='word_search_generator_but_tweaked',
    version='0.1.0',
    description="Generates pdf of word search but has title and can do it for large number of pages",
    long_description=open('README.md').read(),
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires = ["fpdf2==2.7.8", "Pillow==11.0.0", "rich==13.6.0", "ordered-set>=4.0.0"]
)