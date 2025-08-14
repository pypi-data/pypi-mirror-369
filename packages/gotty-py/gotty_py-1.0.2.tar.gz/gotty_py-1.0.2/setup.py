from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gotty-py",
    version="1.0.2",
    author="Thomas Wentworth",
    author_email="thomaswentworth@example.com",
    description="A generic Python client for interacting with gotty terminal interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twentworth/gotty-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websockets>=11.0.3",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "mypy>=1.5.1",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
        "test": [
            "pytest>=7.4.2",
            "pytest-cov>=4.1.0",
        ],
    },
)
