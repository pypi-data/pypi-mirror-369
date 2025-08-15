"""
Setup configuration for SWE Agent - Headless Agentic IDE
"""

from setuptools import setup, find_packages
import os

# Read version from version file
def read_version():
    with open("swe_agent/version.py", "r") as f:
        local_vars = {}
        exec(f.read(), {}, local_vars)
        return local_vars["__version__"]

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="swe-ai-agent",
    version=read_version(),
    author="SWE Agent Team",
    author_email="contact@sweagent.dev",
    description="Headless Agentic IDE with reasoning mode and in built Browser",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/sweagent/swe-agent",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
            "twine",
            "build",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
    },
    entry_points={
        "console_scripts": [
            "swe-agent=swe_agent.main:main",
            "swe=swe_agent.main:main",
            "sweagent=swe_agent.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "swe_agent": [
            "rules/*.md",
            "prompts/*.md",
            "config/*.json",
            "templates/*.py",
            "templates/*.md",
        ],
    },
    keywords=[
        "ai", "agent", "code", "software-engineering", "reinforcement-learning",
        "o1-reasoning", "iterative-improvement", "langraph", "claude", "anthropic",
        "ide", "headless", "automation", "development", "programming-assistant"
    ],
    project_urls={
        "Bug Tracker": "https://github.com/sweagent/swe-agent/issues",
        "Documentation": "https://docs.sweagent.dev",
        "Source Code": "https://github.com/sweagent/swe-agent",
        "Homepage": "https://sweagent.dev",
    },
)