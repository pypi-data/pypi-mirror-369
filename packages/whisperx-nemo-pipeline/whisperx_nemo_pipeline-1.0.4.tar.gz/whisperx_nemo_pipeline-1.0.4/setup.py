from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys

ext_modules = [
    Pybind11Extension(
        "whisperx_nemo_pipeline.vendor.ctc-forced-aligner.ctc_forced_aligner.ctc_forced_aligner",
        ["whisperx_nemo_pipeline/vendor/ctc-forced-aligner/ctc_forced_aligner/forced_align_impl.cpp"],
        extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3"],
    )
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
