#!/usr/bin/env python3

from setuptools import setup, find_packages

# Read requirements from requirements.txt - convert exact pins to flexible ranges
def parse_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Convert exact pins to flexible ranges for production
    requirements = []
    for line in lines:
        if "git+" in line:
            requirements.append(line)  # Keep git dependencies as-is
        elif "==" in line:
            # Convert exact pins to compatible ranges
            name, version = line.split("==")
            major_version = version.split(".")[0]
            requirements.append(f"{name}>={version},<{int(major_version)+1}")
        else:
            requirements.append(line)
    
    return requirements

# Read constraints from constraints.txt
def parse_constraints(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

requirements = parse_requirements("requirements.txt")
constraints = parse_constraints("constraints.txt")

# Read the README for long description
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A production-ready transcription and diarization pipeline with parallel processing."

setup(
    name="whisperx-nemo-pipeline",
    version="1.0.0",
    author="Paul Borie",
    author_email="paul.borie1@gmail.com",
    description="Production-ready transcription and diarization pipeline with parallel processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PaulBorie/whisperx-nemo-parallel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    # Apply constraints during installation
    extras_require={
        "constraints": constraints,
    },
    include_package_data=True,
    package_data={
        "whisperx_nemo_pipeline": ["nemo_msdd_configs/*.yaml", "vendor/**/*"],
    },
)