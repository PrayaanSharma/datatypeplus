from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datatypeplus",
    version="2.0.0",
    author="Prayaan Sharma",
    description="Advanced Data Structures and Fine-Grained Reactive Containers for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prayaansharma/datatypeplus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)