from setuptools import setup, find_packages

setup(
    name="vigilante",
    version="0.0.2",
    author="Mr.Sxturn",
    description="Desktop-based, modular, and extensible multi-toolkit powered by PyQt5, designed for diverse tasks and future expandability.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
)