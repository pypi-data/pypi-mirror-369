from setuptools import setup, find_packages

setup(
    name="godl",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "godl=godl.cli:main",  # Main godl command
            "r1=godl.r1:main",     # Extra command r1
        ]
    },
    install_requires=[],
)
