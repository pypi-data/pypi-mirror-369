"""
Smart GPU - Simple GPU/CPU mode switching utilities.

This package provides automatic detection and switching between CPU (NumPy/Pandas)
and GPU (CuPy/CuDF) modes based on hardware availability.
"""

from ._logging import get_logger
from ._gpu_utils import (
    detect_gpu_hardware,
    is_gpu_available,
    auto_detect_gpu_mode,
    set_gpu_mode,
    get_gpu_mode,
    GPUUtils,
    gpu_utils,
    array,
    DataFrame,
    to_cpu,
    synchronize,
)

__version__ = "0.1.0"
__author__ = "Ardy Dedase"
__email__ = "ardy.dedase@gmail.com"

__all__ = [
    "detect_gpu_hardware",
    "is_gpu_available", 
    "auto_detect_gpu_mode",
    "set_gpu_mode",
    "get_gpu_mode",
    "GPUUtils",
    "gpu_utils",
    "array",
    "DataFrame", 
    "to_cpu",
    "synchronize",
    "get_logger",
]
