from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='Dapropy',  
    version='0.1.1',
    author='Amit Subhash Agrahari',
    author_email='agrahariamitindus45@gmail.com',  
    description='A Python library for automated preprocessing of mixed numeric, categorical, and text data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BlackIIIWhite/Dapropy',  
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=0.24.0",
        "emoji>=1.6.0",
        "nltk>=3.6.0",
        "textblob>=0.15.3",
        "joblib>=1.0.0",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    license='MIT',
)
