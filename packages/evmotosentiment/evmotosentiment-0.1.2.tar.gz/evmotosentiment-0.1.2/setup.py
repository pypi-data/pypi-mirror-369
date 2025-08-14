from setuptools import setup,find_packages

setup(
    author="Ayikwei Richard",
    description="Custom sentiment package for analysing swap related messages",
    name="evmotosentiment",
    version="0.1.2",
    packages=find_packages(where='src',include=["evmotosentiment", "evmotosentiment.*"]),
    package_dir={"": "src"},
    install_requires=['pandas','re'],
)