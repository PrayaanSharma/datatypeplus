from setuptools import setup, find_packages

setup(
    name="datatypeplus",
    version="1.1.1",
    author="Prayaan Sharma",
    author_email="prayaansharma@gmail.com",
    description="A lightweight Python library for flexible data structures and reactive lists.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
