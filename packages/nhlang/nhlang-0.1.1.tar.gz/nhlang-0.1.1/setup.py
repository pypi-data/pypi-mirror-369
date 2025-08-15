from setuptools import setup, find_packages

setup(
    name="nhlang",
    version="1.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nhlang=nhlang.interpreter:main",  # main() phải có trong interpreter.py
        ],
    },
)
