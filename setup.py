import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()
version = os.environ.get("ARGOS_SDK_VERSION")

if version is None:
    raise ValueError("Missing version")

setuptools.setup(
    name="ArgosSDK",
    version=version,
    author="Vinicius Schettino",
    python_requires=">=3.6",
    author_email="vinicius.schettino@ice.ufjf.br",
    license="MIT",
    description="A SDK to handle Henry Argos Fingerprint/Card readers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/engenharia-ufjf/biometria/argos-sdk",
    packages=["argos"],
    install_requires=["daiquiri", "parse"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
