from os import getcwd
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension


ext_modules = [
    CUDAExtension(
        name="phi_torch_cuda",
        sources=["./phi/torch/cuda/src/phi_torch_cuda.cpp"],
        libraries=["cusparse"],
    ),
]

setup(
    name="phi_torch_cuda",
    packages=[],
    ext_modules=ext_modules,
    include_dirs=["./phi/torch/cuda/include"],
    cmdclass={"build_ext": BuildExtension}
)
