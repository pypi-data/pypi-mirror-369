from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension

ext_modules = [
    Pybind11Extension(
        "ansnp",
        ["src/rans_interface.cpp"],
        cxx_std=17,
    ),
]

setup(
    ext_modules=ext_modules,
    author="Zhihao Duan",
    author_email="duan90@purdue.edu",
    maintainer="Wei Jiang",
    maintainer_email="jiangwei@stu.pku.edu.cn",
    version="0.1.0.post3",
    description="A Python package with C++ extensions using pybind11 developed by Zhihao Duan"
)