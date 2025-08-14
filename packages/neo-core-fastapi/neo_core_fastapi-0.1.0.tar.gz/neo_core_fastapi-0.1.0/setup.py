from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neo-core-fastapi",
    version="0.1.0",
    author="Neo Core Team",
    author_email="team@neocore.dev",
    description="A comprehensive FastAPI-based core library providing essential services for modern web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neo-core/neo-core-fastapi",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocstrings[python]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neo-core=neo_core.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="fastapi, web, api, authentication, authorization, orm, sqlalchemy, redis, cache, email, security, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/neo-core/neo-core-fastapi/issues",
        "Source": "https://github.com/neo-core/neo-core-fastapi",
        "Documentation": "https://neo-core-fastapi.readthedocs.io/",
    },
)