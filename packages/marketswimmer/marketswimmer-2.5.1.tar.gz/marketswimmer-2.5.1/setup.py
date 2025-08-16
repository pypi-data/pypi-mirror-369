from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "MarketSwimmer - Warren Buffett's Owner Earnings Analysis Tool"

# Read requirements from requirements.txt if it exists
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="marketswimmer",
    version="2.5.1",
    author="Jeremy Evans",
    author_email="jeremyevans@hey.com",
    description="Warren Buffett's Owner Earnings Analysis Tool - Calculate true economic earnings for any stock",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jeremevans/MarketSwimmer",  # Update with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
        "PyQt6>=6.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "requests>=2.25.0",
        "click>=8.0.0",
        "shellingham>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "gui": [
            "PyQt6>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "marketswimmer=marketswimmer.cli:main",
            "ms=marketswimmer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "marketswimmer": [
            "*.md",
            "*.txt",
            "*.bat",
            "*.ps1",
        ],
    },
    keywords="finance, warren buffett, owner earnings, stocks, investment, financial analysis",
    project_urls={
        "Bug Reports": "https://github.com/jeremevans/MarketSwimmer/issues",
        "Source": "https://github.com/jeremevans/MarketSwimmer",
        "Documentation": "https://github.com/jeremevans/MarketSwimmer/blob/main/README.md",
    },
)
