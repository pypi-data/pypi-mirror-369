#!/usr/bin/env python3
"""
Setup script for smart-gpu package.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smart-gpu",
    version="0.1.0",
    author="Smart GPU Team",
    author_email="team@smart-gpu.com",
    description="Simple GPU/CPU mode switching utilities with automatic detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ardydedase/smart-gpu",
    project_urls={
        "Bug Tracker": "https://github.com/ardydedase/smart-gpu/issues",
        "Documentation": "https://smart-gpu.readthedocs.io",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "gpu": [
            "cupy-cuda12x>=12.0.0; platform_system == 'Linux'",
            "cudf-cu12>=23.0.0; platform_system == 'Linux'",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
