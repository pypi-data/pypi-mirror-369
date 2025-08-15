from setuptools import setup, find_packages

setup(
    name="nhlang",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nhlang = nhlang_pkg.interpreter:main"
        ]
    },
    python_requires=">=3.8",
    description="NH Language interpreter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="QHuyIDK",
    license="MIT",
)
