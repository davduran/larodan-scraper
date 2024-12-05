from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="larodan-scraper",
    version="1.0.0",
    author="David Duran",
    author_email="davduran@gmail.com",
    description="A web scraper for Larodan product information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/larodan-scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'larodan-scraper=larodan_scraper.main:main',
        ],
    },
)