from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zkauth-sdk",
    version="1.3.0",
    author="ZKAuth Team",
    author_email="support@zkauth.com",
    description="Zero-knowledge proof authentication SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zkauth/zkauth-developer-platform",
    project_urls={
        "Bug Tracker": "https://github.com/zkauth/zkauth-developer-platform/issues",
        "Documentation": "https://docs.zkauth.com",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "cryptography>=41.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "django": ["django>=3.2"],
        "fastapi": ["fastapi>=0.100.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
    },
    keywords="zkauth zero-knowledge authentication cryptography privacy zk-snarks",
    include_package_data=True,
    zip_safe=False,
)
