from setuptools import setup, find_packages

setup(
    name="golang_experiments",
    version="0.1.0",
    author="TVK0305",
    author_email="gokultkg01@gmail.com",
    description="A collection of Go programs accessible via Python print calls",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/golang_experiments",
    packages=find_packages(),
    python_requires=">=3.6",
)
