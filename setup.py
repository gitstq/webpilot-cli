"""Setup script for WebPilot-CLI."""
from setuptools import setup, find_packages

setup(
    name="webpilot-cli",
    version="1.0.0",
    description="Lightweight AI browser automation CLI tool",
    long_description=open("README.md", encoding="utf-8").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="WebPilot Team",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "webpilot=webpilot.cli:main",
        ],
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
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
    ],
)
