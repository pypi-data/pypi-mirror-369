from setuptools import setup, find_packages

setup(
    name="jupyflow",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    author="MikanNyan",
    author_email="nyan_mikan@outlook.com",
    description="Extract code cells from Jupyter Notebook as a list of strings.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown"
)