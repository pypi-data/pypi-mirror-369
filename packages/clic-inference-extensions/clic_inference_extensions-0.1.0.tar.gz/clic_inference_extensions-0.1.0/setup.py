# setup.py
import os
import glob
import sys
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

cxx_flags = ["-O3"]
nvcc_flags = ["-O3", "--use_fast_math", "--extra-device-vectorization", "-arch=native"]  # 按显卡架构改
if sys.platform == 'win32':
    cxx_flags = ["/O2"]

setup(
    name='clic_inference_extensions',
    version='0.1.0',
    author="Zhaoyang Jia, Bin Li, Jiahao Li, Wenxuan Xie, Linfeng Qi, Houqiang Li, Yan Lu",
    author_email="jzy_ustc@mail.ustc.edu.cn, qlf324@mail.ustc.edu.cn, libin@microsoft.com, li.jiahao@microsoft.com, wenxie@microsoft.com, lihq@ustc.edu.cn, yanlu@microsoft.com",
    maintainer="Wei Jiang",
    maintainer_email="jiangwei@stu.pku.edu.cn",
    description='PyTorch CUDA extension for fast inference of DCVC-RT',
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["clic_inference_extensions"],  # 你的 Python 包目录名
    ext_modules=[
        CUDAExtension(
            name='clic_inference_extensions._C',  # _C 常用于 C++/CUDA 扩展模块
            sources=glob.glob('clic_inference_extensions/*.cpp') + glob.glob('clic_inference_extensions/*.cu'),
            include_dirs=['clic_inference_extensions'],
            extra_compile_args={
                "cxx": cxx_flags,
                "nvcc": nvcc_flags,
            },
        ),
    ],
    cmdclass={
        'build_ext': BuildExtension
    },
    python_requires=">=3.11",
    install_requires=[
        "torch>=1.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
