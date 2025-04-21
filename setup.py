import setuptools
import os
import re

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setuptools.setup(
    name="agentic-framework",
    version=re.search(r"__version__ = ['\"]([^'\"]+)['\"]",(open("agentic_library/__init__.py").read())).group(1),
    author="Mehul Srivastava",
    author_email="mehul@fivelabs.co",
    description="A domain-agnostic framework for adding emotion, memory, and learning capabilities to LLM-based agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/five-research/agentic-framework",
    project_urls={
        "Bug Tracker": "https://github.com/five-research/agentic-framework/issues",
        "Documentation": "https://github.com/five-research/agentic-framework/docs",
        "Source Code": "https://github.com/five-research/agentic-framework",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai, llm, agent, emotion, memory, learning, personality",
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "agentic_library": ["py.typed"],
    },
)