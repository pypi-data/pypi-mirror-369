from setuptools import setup, find_packages

setup(
    name="godl",
    version="0.1.2",  # bumped from 0.1.0
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "godl=godl.cli:main",
            "r1=godl.r1:main",
            "r2=godl.r2:main",
            "r3=godl.r3:main",
            "r4=godl.r4:main",
            "r5=godl.r5:main",
        ]
    },
    install_requires=[],
)
