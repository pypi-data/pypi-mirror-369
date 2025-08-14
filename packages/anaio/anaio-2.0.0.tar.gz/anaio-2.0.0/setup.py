#!/usr/bin/env python
# encoding: utf-8
"""
setup.py -- setup file for the anaio module
"""
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig


class build_ext(build_ext_orig):
    def finalize_options(self):
        super().finalize_options()
        # Import numpy only when it's guaranteed to be present in the build env
        import numpy
        self.include_dirs.append(numpy.get_include())


extra_compile_args = ["-O2"]
if sys.platform != "win32":
    extra_compile_args.append("-ffast-math")

readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

module_anaio = Extension(
    name="_anaio",
    define_macros=[("MAJOR_VERSION", "1"), ("MINOR_VERSION", "1")],
    sources=[
        "src/_anaio.c",
        "src/anarw.c",
        "src/anacompress.c",
        "src/anadecompress.c",
    ],
    extra_compile_args=extra_compile_args,
)

setup(
    name="anaio",
    version="2.0.0",
    description="Python library for ANA f0 file I/O",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Johannes Hoelken",
    author_email="hoelken@mps.mpg.de",
    url="https://gitlab.gwdg.de/hoelken/anaio",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"anaio": "anaio"},
    packages=["anaio"],
    ext_package="anaio",
    ext_modules=[module_anaio],
    cmdclass={"build_ext": build_ext},
    install_requires=["numpy>=2.0"],
)
