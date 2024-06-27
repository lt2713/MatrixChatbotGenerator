# Script to make the project installable with pip
# After running this script:
# build the package:
# python setup.py sdist bdist_wheel
# upload the package:
# twine upload dist/*
# done, installable with:
# pip install mci-dibse-lt2713-matrix-chatbot-generator==1.0.4
from setuptools import setup, find_packages

setup(
    name="mci_dibse_lt2713_matrix_chatbot_generator",
    version="1.0.4",
    author="Tobias Leiter",
    author_email="lt2713@mci4me.at",
    description="Package to create a Matrix Chatbot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
