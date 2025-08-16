from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sedql",
    version="1.0.9",  # Match npm package version
    author="SED Team",
    description="Python SDK for SED (Semantic Entities Designs) - Full TypeScript CLI Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/holy182/sed-cli",
    project_urls={
        "Bug Tracker": "https://github.com/holy182/sed-cli/issues",
        "Documentation": "https://github.com/holy182/sed-cli#readme",
        "Source Code": "https://github.com/holy182/sed-cli",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",

        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Drivers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses subprocess to call sedql CLI
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "sedql-python=sedql.cli:main",
        ],
    },
    keywords="semantic, database, ai, dsl, data-modeling, automation, sed, cli",
    include_package_data=True,
    zip_safe=False,
)
