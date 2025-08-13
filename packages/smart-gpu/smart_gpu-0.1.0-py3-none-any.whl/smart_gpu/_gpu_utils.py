"""
Simple GPU/CPU mode switching utilities.
"""

import os
import platform
import subprocess
from typing import Optional, Any, Union, TYPE_CHECKING
import logging

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import cupy
    import cudf

from ._logging import get_logger

logger = get_logger()

# Global mode setting
_GPU_MODE = None


def detect_gpu_hardware() -> bool:
    """
    Automatically detect if GPU hardware is available and supported.
    
    Returns:
        True if GPU hardware is detected and supported, False otherwise
    """
    # Check platform first
    system = platform.system()
    if system == "Darwin":  # macOS
        logger.info("GPU acceleration not supported on macOS")
        return False
    elif system != "Linux":
        logger.info(f"GPU acceleration support unknown on {system}")
        return False
    
    # Check for NVIDIA GPU on Linux
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("NVIDIA GPU detected")
            
            # Check if CUDA is available
            try:
                result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info("CUDA toolkit detected")
                    return True
                else:
                    logger.info("NVIDIA GPU found but CUDA toolkit not detected")
                    return False
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.info("NVIDIA GPU found but CUDA toolkit not available")
                return False
        else:
            logger.info("No NVIDIA GPU detected")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.info("nvidia-smi not available - no GPU detected")
        return False


def is_gpu_available() -> bool:
    """Check if GPU libraries are available."""
    # Check platform first
    system = platform.system()
    if system == "Darwin":  # macOS
        logger.info("CuPy and CuDF are not supported on macOS")
        return False
    elif system != "Linux":
        logger.info(f"CuPy and CuDF support unknown on {system}")
        return False
    
    # Try to import GPU libraries
    try:
        import cupy as cp
        import cudf
        return True
    except ImportError:
        return False


def auto_detect_gpu_mode() -> bool:
    """
    Automatically detect and set the optimal GPU mode based on hardware and software availability.
    
    Returns:
        True if GPU mode should be enabled, False for CPU mode
    """
    # Check environment variable override
    force_cpu = os.environ.get("SMART_GPU_FORCE_CPU", "false").lower() == "true"
    if force_cpu:
        logger.info("CPU mode forced by SMART_GPU_FORCE_CPU environment variable")
        return False
    
    # Check explicit GPU setting
    use_gpu = os.environ.get("USE_GPU", "").lower()
    if use_gpu == "true":
        logger.info("GPU mode explicitly enabled by USE_GPU environment variable")
        return is_gpu_available()
    elif use_gpu == "false":
        logger.info("GPU mode explicitly disabled by USE_GPU environment variable")
        return False
    
    # Auto-detect based on hardware and software
    if detect_gpu_hardware() and is_gpu_available():
        logger.info("Auto-detected: GPU hardware and software available - enabling GPU mode")
        return True
    else:
        logger.info("Auto-detected: GPU not available - using CPU mode")
        return False


def set_gpu_mode(enabled: bool) -> None:
    """Set the global GPU mode."""
    global _GPU_MODE
    _GPU_MODE = enabled
    logger.info(f"GPU mode {'enabled' if enabled else 'disabled'}")


def get_gpu_mode() -> bool:
    """Get the current GPU mode setting."""
    global _GPU_MODE
    if _GPU_MODE is None:
        # Auto-detect the optimal mode
        _GPU_MODE = auto_detect_gpu_mode()
        logger.info(f"Auto-detected GPU mode: {'enabled' if _GPU_MODE else 'disabled'}")
    return _GPU_MODE


class GPUUtils:
    """Simple utility class for GPU/CPU operations."""
    
    def __init__(self, gpu_mode: Optional[bool] = None):
        self._gpu_mode = gpu_mode if gpu_mode is not None else get_gpu_mode()
        self._cupy = None
        self._cudf = None
        
        if self._gpu_mode:
            if not is_gpu_available():
                logger.warning("GPU mode requested but CuPy/CuDF not available. Falling back to CPU mode.")
                self._gpu_mode = False
            else:
                try:
                    import cupy as cp
                    import cudf
                    self._cupy = cp
                    self._cudf = cudf
                    logger.info("GPU libraries loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load GPU libraries: {e}. Falling back to CPU mode.")
                    self._gpu_mode = False
    
    @property
    def is_gpu_mode(self) -> bool:
        """Check if currently in GPU mode."""
        return self._gpu_mode
    
    @property
    def np(self):
        """Get NumPy or CuPy based on mode."""
        return self._cupy if self._gpu_mode else np
    
    @property
    def pd(self):
        """Get Pandas or CuDF based on mode."""
        return self._cudf if self._gpu_mode else pd
    
    def array(self, data: Any, **kwargs) -> Any:
        """Create array using appropriate library."""
        if self._gpu_mode:
            return self._cupy.array(data, **kwargs)
        else:
            return np.array(data, **kwargs)
    
    def DataFrame(self, data=None, **kwargs) -> Any:
        """Create DataFrame using appropriate library."""
        if self._gpu_mode:
            return self._cudf.DataFrame(data, **kwargs)
        else:
            return pd.DataFrame(data, **kwargs)
    
    def to_cpu(self, data: Any) -> Any:
        """Convert GPU data to CPU if needed."""
        if not self._gpu_mode:
            return data
        
        if hasattr(data, 'get'):
            # CuPy array
            return data.get()
        elif hasattr(data, 'to_pandas'):
            # CuDF DataFrame/Series
            return data.to_pandas()
        else:
            return data
    
    def synchronize(self) -> None:
        """Synchronize GPU operations if in GPU mode."""
        if self._gpu_mode and self._cupy:
            self._cupy.cuda.Stream.null.synchronize()


# Global instance for convenience
gpu_utils = GPUUtils()


# Simple convenience functions
def array(data: Any, **kwargs) -> Any:
    """Create array using current GPU mode."""
    return gpu_utils.array(data, **kwargs)


def DataFrame(data=None, **kwargs) -> Any:
    """Create DataFrame using current GPU mode."""
    return gpu_utils.DataFrame(data, **kwargs)


def to_cpu(data: Any) -> Any:
    """Convert data to CPU format."""
    return gpu_utils.to_cpu(data)


def synchronize() -> None:
    """Synchronize GPU operations if in GPU mode."""
    gpu_utils.synchronize()
