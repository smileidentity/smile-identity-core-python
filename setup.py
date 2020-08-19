from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="smile_id_core",
    version='0.0.12',
    description="The official Smile Identity package exposes four classes namely; the WebApi class, the IDApi class, the Signature class and the Utilities class.",
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/smileidentity/smile-identity-core-python",
    author="Smile Identity",
    author_email="support@smileidentity.com",
    install_requires=[
        "requests ~= 2.24.0",
        "pycryptodome ~= 3.9.8",

    ],
)
