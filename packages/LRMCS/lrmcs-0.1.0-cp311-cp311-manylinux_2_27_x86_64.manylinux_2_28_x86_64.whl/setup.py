# setup.py
import os
import sys
import platform
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# ----------------------------
# Config por variável de ambiente
# ----------------------------
ENABLE_OMP = 1
ENABLE_AVX512 = 1

# Fontes do seu projeto
cpp_sources = [
    "API.cpp",
    "simulation.cpp",
    "distributions.cpp",
    "simRunner.cpp",
    "cutsetTree.cpp",
    "SIMDUtils.cpp",
    "utils.cpp",
]

extra_compile_args = []
extra_link_args = []

include_dirs = [os.path.abspath(os.path.dirname(__file__))]

system = platform.system()

boost_inc = os.environ.get("BOOST_INCLUDEDIR")
if boost_inc and os.path.isdir(boost_inc):
    include_dirs.append(boost_inc)

# --------- Padrões de otimização portáveis ----------
if system == "Windows":
    # MSVC
    extra_compile_args += ["/O2", "/std:c++17"]
    if ENABLE_OMP:
        # VS2022: /openmp (v2) ou /openmp:llvm; /openmp:experimental era antigo
        extra_compile_args += ["/openmp"]
    if ENABLE_AVX512:
        # AVX-512: só ative se você quiser um wheel específico para isso
        # (não recomendado para wheels genéricos do PyPI)
        extra_compile_args += ["/arch:AVX512"]
else:
    # GCC/Clang
    extra_compile_args += ["-O3", "-std=c++17", "-fvisibility=hidden"]
    if ENABLE_OMP:
        # macOS é chato com OpenMP; por padrão desabilitamos
        if system == "Linux":
            extra_compile_args += ["-fopenmp"]
            extra_link_args += ["-fopenmp"]
        elif system == "Darwin":
            # Desligado por padrão; se quiser muito:
            # extra_compile_args += ["-Xpreprocessor", "-fopenmp"]
            # extra_link_args += ["-lomp"]
            pass
    if ENABLE_AVX512:
        # Mesma observação: não use para wheels genéricos
        extra_compile_args += ["-mavx512f", "-march=skylake-avx512"]

# Dica: se usa Boost via vcpkg no Windows, deixe o include opcional:
vcpkg_root = os.environ.get("VCPKG_ROOT", r"C:\vcpkg") if system == "Windows" else None
if vcpkg_root:
    for triplet in ("x64-windows", "x86-windows"):
        cand = os.path.join(vcpkg_root, "installed", triplet, "include")
        if os.path.exists(cand):
            include_dirs.append(cand)
            break

ext_modules = [
    Pybind11Extension(
        "lrmcs",                      # nome do módulo importável
        sources=cpp_sources,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=17,
    )
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
