"""Setup configuration for Banking Transactions API package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="banking-transactions-api",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A REST API for banking transaction data with fraud detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/banking-transactions-api",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "pandas>=2.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pandas-stubs>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "banking-api=banking_api.main:run_server",
        ],
    },
)
