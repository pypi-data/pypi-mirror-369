#!/usr/bin/env python3
import sys
from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pathlib

# ---------- Utilities ----------
def parse_requirements(filename):
    """Read requirements.txt and convert exact pins to flexible ranges."""
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    requirements = []
    for line in lines:
        if "git+" in line:
            requirements.append(line)
        elif "==" in line:
            name, version = line.split("==")
            major_version = version.split(".")[0]
            requirements.append(f"{name}>={version},<{int(major_version)+1}")
        else:
            requirements.append(line)
    return requirements

def parse_constraints(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

# ---------- Requirements ----------
requirements = parse_requirements("requirements.txt")
constraints = parse_constraints("constraints.txt")

# ---------- Long description ----------
try:
    long_description = pathlib.Path("README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "A production-ready transcription and diarization pipeline with parallel processing."

# ---------- Extension module for ctc_forced_aligner ----------
ext_modules = [
    Pybind11Extension(
        "whisperx_nemo_pipeline.vendor.ctc-forced-aligner.ctc_forced_aligner.ctc_forced_aligner",
        [
            "whisperx_nemo_pipeline/vendor/ctc-forced-aligner/ctc_forced_aligner/forced_align_impl.cpp"
        ],
        extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3"],
    )
]

# ---------- Setup ----------
setup(
    name="whisperx-nemo-pipeline",
    version="1.0.1",
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
    extras_require={"constraints": constraints},
    include_package_data=True,
    package_data={
        "whisperx_nemo_pipeline": [
            "nemo_msdd_configs/*.yaml",
            "vendor/ctc-forced-aligner/ctc_forced_aligner/*.cpp",
            "vendor/ctc-forced-aligner/ctc_forced_aligner/*.h",
        ],
    },
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
