"""
Tests for smart_gpu._gpu_utils module.
"""

import os
import platform
import pytest
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd

from smart_gpu._gpu_utils import (
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


class TestGPUDetection:
    """Test GPU detection functions."""
    
    def test_detect_gpu_hardware_macos(self):
        """Test GPU detection on macOS."""
        with patch('platform.system', return_value='Darwin'):
            result = detect_gpu_hardware()
            assert result is False
    
    def test_detect_gpu_hardware_windows(self):
        """Test GPU detection on Windows."""
        with patch('platform.system', return_value='Windows'):
            result = detect_gpu_hardware()
            assert result is False
    
    def test_detect_gpu_hardware_linux_no_gpu(self):
        """Test GPU detection on Linux without GPU."""
        with patch('platform.system', return_value='Linux'), \
             patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = detect_gpu_hardware()
            assert result is False
    
    def test_detect_gpu_hardware_linux_with_gpu(self):
        """Test GPU detection on Linux with GPU."""
        with patch('platform.system', return_value='Linux'), \
             patch('subprocess.run') as mock_run:
            # Mock nvidia-smi success
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "NVIDIA GPU detected"
            
            result = detect_gpu_hardware()
            assert result is True
    
    def test_is_gpu_available_macos(self):
        """Test GPU availability check on macOS."""
        with patch('platform.system', return_value='Darwin'):
            result = is_gpu_available()
            assert result is False
    
    def test_is_gpu_available_linux_no_libs(self):
        """Test GPU availability check on Linux without libraries."""
        with patch('platform.system', return_value='Linux'), \
             patch('builtins.__import__', side_effect=ImportError()):
            result = is_gpu_available()
            assert result is False
    
    def test_is_gpu_available_linux_with_libs(self):
        """Test GPU availability check on Linux with libraries."""
        with patch('platform.system', return_value='Linux'), \
             patch('builtins.__import__', return_value=MagicMock()):
            result = is_gpu_available()
            assert result is True


class TestAutoDetection:
    """Test automatic GPU mode detection."""
    
    def test_auto_detect_force_cpu_env(self):
        """Test environment variable forcing CPU mode."""
        with patch.dict(os.environ, {'SMART_GPU_FORCE_CPU': 'true'}):
            result = auto_detect_gpu_mode()
            assert result is False
    
    def test_auto_detect_force_gpu_env(self):
        """Test environment variable forcing GPU mode."""
        with patch.dict(os.environ, {'USE_GPU': 'true'}), \
             patch('smart_gpu._gpu_utils.is_gpu_available', return_value=True):
            result = auto_detect_gpu_mode()
            assert result is True
    
    def test_auto_detect_disable_gpu_env(self):
        """Test environment variable disabling GPU mode."""
        with patch.dict(os.environ, {'USE_GPU': 'false'}):
            result = auto_detect_gpu_mode()
            assert result is False
    
    def test_auto_detect_no_env_gpu_available(self):
        """Test auto-detection when GPU is available."""
        with patch('smart_gpu._gpu_utils.detect_gpu_hardware', return_value=True), \
             patch('smart_gpu._gpu_utils.is_gpu_available', return_value=True):
            result = auto_detect_gpu_mode()
            assert result is True
    
    def test_auto_detect_no_env_gpu_not_available(self):
        """Test auto-detection when GPU is not available."""
        with patch('smart_gpu._gpu_utils.detect_gpu_hardware', return_value=False), \
             patch('smart_gpu._gpu_utils.is_gpu_available', return_value=False):
            result = auto_detect_gpu_mode()
            assert result is False


class TestGPUModeControl:
    """Test GPU mode control functions."""
    
    def test_set_get_gpu_mode(self):
        """Test setting and getting GPU mode."""
        # Reset global state
        import smart_gpu._gpu_utils as gpu_module
        gpu_module._GPU_MODE = None
        
        set_gpu_mode(True)
        assert get_gpu_mode() is True
        
        set_gpu_mode(False)
        assert get_gpu_mode() is False
    
    def test_get_gpu_mode_auto_detect(self):
        """Test auto-detection when getting GPU mode."""
        # Reset global state
        import smart_gpu._gpu_utils as gpu_module
        gpu_module._GPU_MODE = None
        
        with patch('smart_gpu._gpu_utils.auto_detect_gpu_mode', return_value=True):
            result = get_gpu_mode()
            assert result is True


class TestGPUUtils:
    """Test GPUUtils class."""
    
    def test_gpu_utils_init_cpu_mode(self):
        """Test GPUUtils initialization in CPU mode."""
        utils = GPUUtils(gpu_mode=False)
        assert utils.is_gpu_mode is False
        assert utils.np is np
        assert utils.pd is pd
    
    def test_gpu_utils_init_gpu_mode_available(self):
        """Test GPUUtils initialization in GPU mode with libraries available."""
        with patch('smart_gpu._gpu_utils.is_gpu_available', return_value=True), \
             patch('builtins.__import__') as mock_import:
            mock_cupy = MagicMock()
            mock_cudf = MagicMock()
            
            def mock_import_side_effect(name, *args, **kwargs):
                if 'cupy' in name:
                    return mock_cupy
                elif 'cudf' in name:
                    return mock_cudf
                else:
                    return MagicMock()
            
            mock_import.side_effect = mock_import_side_effect
            
            utils = GPUUtils(gpu_mode=True)
            assert utils.is_gpu_mode is True
            assert utils.np is mock_cupy
            assert utils.pd is mock_cudf
    
    def test_gpu_utils_init_gpu_mode_not_available(self):
        """Test GPUUtils initialization in GPU mode without libraries."""
        with patch('smart_gpu._gpu_utils.is_gpu_available', return_value=False):
            utils = GPUUtils(gpu_mode=True)
            assert utils.is_gpu_mode is False
            assert utils.np is np
            assert utils.pd is pd
    
    def test_gpu_utils_array_cpu(self):
        """Test array creation in CPU mode."""
        utils = GPUUtils(gpu_mode=False)
        data = [1, 2, 3, 4, 5]
        result = utils.array(data)
        assert isinstance(result, np.ndarray)
        assert result.tolist() == data
    
    def test_gpu_utils_dataframe_cpu(self):
        """Test DataFrame creation in CPU mode."""
        utils = GPUUtils(gpu_mode=False)
        data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        result = utils.DataFrame(data)
        assert isinstance(result, pd.DataFrame)
        assert result.to_dict('list') == data
    
    def test_gpu_utils_to_cpu_cpu_mode(self):
        """Test to_cpu in CPU mode."""
        utils = GPUUtils(gpu_mode=False)
        data = np.array([1, 2, 3])
        result = utils.to_cpu(data)
        assert result is data  # Should return unchanged
    
    def test_gpu_utils_synchronize_cpu_mode(self):
        """Test synchronize in CPU mode."""
        utils = GPUUtils(gpu_mode=False)
        # Should not raise any exception
        utils.synchronize()


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_array_function(self):
        """Test array convenience function."""
        data = [1, 2, 3, 4, 5]
        result = array(data)
        assert isinstance(result, np.ndarray)
        assert result.tolist() == data
    
    def test_dataframe_function(self):
        """Test DataFrame convenience function."""
        data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        result = DataFrame(data)
        assert isinstance(result, pd.DataFrame)
        assert result.to_dict('list') == data
    
    def test_to_cpu_function(self):
        """Test to_cpu convenience function."""
        data = np.array([1, 2, 3])
        result = to_cpu(data)
        assert result is data  # Should return unchanged
    
    def test_synchronize_function(self):
        """Test synchronize convenience function."""
        # Should not raise any exception
        synchronize()


class TestGlobalInstance:
    """Test global gpu_utils instance."""
    
    def test_global_gpu_utils(self):
        """Test global gpu_utils instance."""
        assert hasattr(gpu_utils, 'is_gpu_mode')
        assert hasattr(gpu_utils, 'np')
        assert hasattr(gpu_utils, 'pd')
        assert hasattr(gpu_utils, 'array')
        assert hasattr(gpu_utils, 'DataFrame')
        assert hasattr(gpu_utils, 'to_cpu')
        assert hasattr(gpu_utils, 'synchronize')


if __name__ == "__main__":
    pytest.main([__file__])
