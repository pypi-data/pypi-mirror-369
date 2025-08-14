from setuptools import setup, find_packages

setup(
    name="grad_watch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch>=1.7.0",
        "matplotlib>=3.0.0",
        "numpy>=1.19.0"
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown"
)
