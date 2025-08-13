# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-08-11

### Added
- Initial release of smart-gpu package
- Automatic GPU hardware detection using `nvidia-smi` and CUDA toolkit
- Automatic GPU library availability detection (CuPy/CuDF)
- Smart mode switching between CPU (NumPy/Pandas) and GPU (CuPy/CuDF) modes
- Environment variable controls (`SMART_GPU_FORCE_CPU`, `USE_GPU`)
- `GPUUtils` class for unified CPU/GPU operations
- Convenience functions (`array`, `DataFrame`, `to_cpu`, `synchronize`)
- Global `gpu_utils` instance for easy access
- Direct import support for `np` and `pd` from `gpu_utils`
- Comprehensive test suite with 87% code coverage
- Cross-platform support (Linux with GPU, macOS/Windows CPU-only)
- Graceful fallback to CPU mode when GPU is unavailable
- Detailed logging for debugging and monitoring

### Features
- **Automatic Detection**: Detects NVIDIA GPU hardware and CUDA availability
- **Smart Switching**: Seamlessly switches between CPU and GPU modes
- **Easy Integration**: Drop-in replacement for NumPy and Pandas operations
- **Environment Control**: Override detection with environment variables
- **Cross-Platform**: Works on Linux (with GPU support) and other platforms (CPU-only)

### Technical Details
- Python 3.8+ support
- NumPy 1.20+ and Pandas 1.3+ as core dependencies
- Optional CuPy and CuDF dependencies for GPU support
- MIT license
- Comprehensive documentation and examples
