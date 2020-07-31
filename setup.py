from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="smile-id-core",
    version='0.0.1',
    description="The official Smile Identity package exposes four classes namely; the WebApi class, the IDApi class, the Signature class and the Utilities class.",
    py_modules=["IdApi", "Signature", "Utilities", "WebApi"],
    package_dir={"": "src"},
    long_description=long_description,
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
