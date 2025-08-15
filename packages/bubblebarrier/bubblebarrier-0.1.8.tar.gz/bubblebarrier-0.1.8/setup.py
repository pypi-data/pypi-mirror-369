#!/usr/bin/env python3
"""Setup script for massfunc package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bubblebarrier",
    version="0.1.8",
    author="Hajime Hinata",
    author_email="onmyojiflow@gmail.com",
    description="Barrier calculations for cosmic reionization models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SOYONAOC/BubbleBarrier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.18.0",
        "scipy>=1.5.0",
        "astropy>=4.0",
        "matplotlib>=3.0.0",
        "pandas>=1.0.0",
        "joblib>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "numpydoc>=1.1",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/SOYONAOC/BubbleBarrier/issues",
        "Source": "https://github.com/SOYONAOC/BubbleBarrier",
    },
)
