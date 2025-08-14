# setup.py
from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8")

setup(
    name="hl_gaming_official_ff_data",
    version="2.3.8",
    author="Haroon Brokha",
    author_email="developers@hlgamingofficial.com",
    description="Python client for HL Gaming Official Free Fire API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://www.hlgamingofficial.com/p/api.html",
    project_urls={
        "Documentation": "https://www.hlgamingofficial.com/p/free-fire-account-information-python.html",
        "Homepage": "https://www.hlgamingofficial.com",
        "Contact": "https://www.hlgamingofficial.com/p/contact-us.html",
        "Feedback": "https://www.hlgamingofficial.com/p/feedback.html",
    },
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0"
    ],
    extras_require={
        "cache": ["cachetools>=5.0.0"]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
