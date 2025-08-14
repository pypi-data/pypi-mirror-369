from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11

ext_modules = [
    Pybind11Extension(
        "mathutils.mathutils_backend",
        [
            "src/cpp/bindings.cpp",
        ],
        include_dirs=[
            "include",  # MathUtils header files
            "/usr/include/eigen3",  # Eigen headers
        ],
        cxx_std=20,  # Use C++20 standard for coroutines
        define_macros=[("VERSION_INFO", '"dev"')],
    ),
]

setup(
    name="mathutils",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
