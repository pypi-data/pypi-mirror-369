from setuptools import setup,find_packages

setup(
    author="Ayikwei Richard",
    description="Custom sentiment package for analysing swap related messages",
    name="sentiment",
    version="0.2.3",
    packages=find_packages(where='src',include=["motoevsentiment", "motoevsentiment.*"]),
    package_dir={"": "src"},
    install_requires=['pandas','re'],
)