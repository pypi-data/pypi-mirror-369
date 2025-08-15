from setuptools import setup, find_packages

setup(
    name="pmg1",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pmg1=pmg1.cli:main"
        ]
    },
    install_requires=[],
)
