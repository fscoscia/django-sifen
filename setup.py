"""
Setup configuration for django-sifen package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

# Read version from __init__.py
version = "0.1.0"

setup(
    name="django-sifen",
    version=version,
    author="Girolabs",
    author_email="info@girolabs.com",
    description="Librería Python para Facturación Electrónica de Paraguay (SIFEN)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/girolabs/django-sifen",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "lxml>=4.9.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "django": [
            "django>=3.2",
            "djangorestframework>=3.14",
            "django-filter>=23.0",
            "django-cors-headers>=4.0",
            "drf-spectacular>=0.26.0",
            "Pillow>=10.0.0",
            "qrcode>=7.4.0",
            "openpyxl>=3.1.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-django>=4.5.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    keywords="sifen paraguay facturacion electronica electronic invoicing",
    project_urls={
        "Bug Reports": "https://github.com/girolabs/django-sifen/issues",
        "Source": "https://github.com/girolabs/django-sifen",
        "Documentation": "https://github.com/girolabs/django-sifen/blob/main/docs/",
    },
)
