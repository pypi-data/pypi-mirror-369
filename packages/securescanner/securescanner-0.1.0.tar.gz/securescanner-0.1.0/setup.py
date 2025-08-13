from setuptools import setup, find_packages
from securescanner.version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="securescanner",
    version=__version__,
    author="Breye Foka",
    author_email="breyefokalagloire@gmail.com",
    description="Advanced Security Port Scanner and Vulnerability Assessment Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BreyeFoka/securescanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "securescanner=securescanner.cli:main",
        ],
    },
    install_requires=[
        "ipaddress",
    ],
)
