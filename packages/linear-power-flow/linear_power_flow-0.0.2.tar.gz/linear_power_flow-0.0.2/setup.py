from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="linear-power-flow",
    version="0.0.2",
    author="Tianqi Hong",
    author_email="tianqi.hong@uga.edu",
    description="A Python package for linear power flow analysis in electrical power systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/th1275/linear_power_flow",
    project_urls={
        "Bug Tracker": "https://github.com/th1275/linear_power_flow/issues",
        "Documentation": "https://github.com/th1275/linear_power_flow#readme",
        "Source Code": "https://github.com/th1275/linear_power_flow",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
            "build>=0.7.0",
            "twine>=4.0.0",
        ],
        "examples": [
            "pypower>=5.1.0",
            "pandapower>=2.10.0",
            "matplotlib>=3.3.0",
            "plotly>=5.0.0",
        ],
    },
    keywords="power flow, linear power flow, power systems, electrical engineering, grid analysis",
)