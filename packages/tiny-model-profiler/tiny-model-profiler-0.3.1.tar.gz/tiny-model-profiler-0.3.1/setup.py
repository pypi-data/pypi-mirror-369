from setuptools import setup, find_packages
import os
 
# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="tiny-model-profiler",
    version="0.3.1",
    description="Lightweight PyTorch/TensorFlow model profiler",
    author="Mahika Shah",
    author_email="mahikasha1@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch>=1.7.0",
        "torchinfo>=1.7.0"
    ],
    python_requires=">=3.7",
)