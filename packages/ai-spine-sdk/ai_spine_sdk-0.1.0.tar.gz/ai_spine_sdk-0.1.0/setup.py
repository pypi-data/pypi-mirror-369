from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __version__.py
version = {}
with open("ai_spine/__version__.py", "r") as f:
    exec(f.read(), version)

setup(
    name="ai-spine-sdk",
    version=version['__version__'],
    author="AI Spine Team",
    author_email="support@dataframeai.com",
    description="Python SDK for AI Spine - The Stripe for AI Agent Orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dataframe-Consulting/ai-spine-sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/Dataframe-Consulting/ai-spine-sdk-python/issues",
        "Documentation": "https://dataframeai.com/docs",
        "Source Code": "https://github.com/Dataframe-Consulting/ai-spine-sdk-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0,<3.0.0",
        "typing-extensions>=4.0.0;python_version<'3.8'",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.0.0",
            "responses>=0.22.0",
            "black>=22.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-spine=ai_spine.cli:main",
        ],
    },
)