from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="smile-id-core",
    version='0.0.3',
    description="The official Smile Identity package exposes four classes namely; the WebApi class, the IDApi class, the Signature class and the Utilities class.",
    py_modules=["IdApi", "Signature", "Utilities", "WebApi"],
    package_dir={"": "src"},
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
    author="Japhet Ndhlovu",
    author_email="japhet@smileidentity.com",

    install_requires=[
        "requests ~= 2.24.0",
        "pycryptodome ~= 3.9.8",

    ],
)
