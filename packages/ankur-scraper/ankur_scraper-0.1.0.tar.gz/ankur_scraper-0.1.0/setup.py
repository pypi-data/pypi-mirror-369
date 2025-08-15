from setuptools import setup, find_packages
import os

def get_version():
    """Dynamically fetch version from ankur_scraper/__init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), "ankur_scraper", "__init__.py")
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[-1].strip().strip('"\'')
    return "0.1.0"  # Fallback version

def get_long_description():
    """Read README.md with proper encoding handling"""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    try:
        with open(readme_path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "A web scraping library focused on extracting website sections with standardized output format"
    except UnicodeDecodeError:
        # Fallback if UTF-8 doesn't work
        try:
            with open(readme_path, encoding='utf-8-sig') as f:
                return f.read()
        except:
            return "A web scraping library focused on extracting website sections with standardized output format"

setup(
    name="ankur-scraper",
    version="0.1.0",
    author="Ankur Dev",
    author_email="Dev@ankursolutions.com",
    description="A web scraping library focused on extracting website sections with standardized output format",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnkurSolutions/ankur-scraper.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "playwright",
        "tldextract",
        "rich",
        "httpx"
    ],
    entry_points={
        "console_scripts": [
            "ankur-scraper=ankur_scraper.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
)