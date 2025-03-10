"""
Setup script for GabeGardener.
"""
from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from steamtime/__init__.py
about = {}
with open(os.path.join("steamtime", "__init__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="GabeGardener",
    version=about["__version__"],
    author="Sashank Bhamidi",
    author_email="hello@sashank.wiki",
    description="A modern, efficient utility for managing Steam game sessions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shankypedia/GabeGardener",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "steam>=1.4.4",
        "pyotp>=2.8.0",
        "pyjwt>=2.6.0",
        "pydantic>=1.10.8",
        "click>=8.1.3",
        "cryptography>=39.0.1",
        "flask>=2.2.3",
        "apscheduler>=3.10.1",
        "tabulate>=0.9.0",
        "requests>=2.28.2",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gabegardener=steamtime.cli.commands:cli",
        ],
    },
    package_data={
        "steamtime": [
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
            "i18n/translations/*.json",
        ],
    },
    keywords="steam, gaming, automation, hour-booster, game-time",
)
