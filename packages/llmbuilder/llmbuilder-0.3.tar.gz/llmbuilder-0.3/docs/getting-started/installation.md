# Installation

This guide will help you install LLMBuilder and set up your environment for training and deploying language models.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB+ recommended)
- **Storage**: 2GB free space
- **OS**: Windows, macOS, or Linux

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 16GB or more
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- **Storage**: 10GB+ free space for models and data

## Installation Methods

### Method 1: PyPI Installation (Recommended)

The easiest way to install LLMBuilder is via PyPI:

```bash
pip install llmbuilder
```

### Method 2: Development Installation

For the latest features or if you want to contribute:

```bash
# Clone the repository
git clone https://github.com/Qubasehq/llmbuilder-package.git
cd llmbuilder-package

# Install in development mode
pip install -e .
```

### Method 3: CPU-Only Installation

If you don't have a GPU or want to use CPU-only PyTorch:

```bash
# Install CPU-only PyTorch first
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install LLMBuilder
pip install llmbuilder
```

## Verify Installation

Test your installation by running:

```bash
# Check if LLMBuilder is installed
python -c "import llmbuilder; print(f'LLMBuilder {llmbuilder.__version__} installed successfully!')"

# Test the CLI
llmbuilder --version
llmbuilder info
```

You should see output similar to:

```
LLMBuilder 0.2.1 installed successfully!
🤖 LLMBuilder version 0.2.1
A comprehensive toolkit for building, training, and deploying language models.
```

## Optional Dependencies

### For GPU Training

If you have an NVIDIA GPU and want to use CUDA:

```bash
# Install CUDA-enabled PyTorch (adjust version as needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### For Advanced Data Processing

For processing various document formats:

```bash
pip install llmbuilder[data]
```

This includes:
- `pandas` - For data manipulation
- `pymupdf` - For PDF processing
- `docx2txt` - For DOCX files
- `python-pptx` - For PowerPoint files
- `beautifulsoup4` - For HTML processing

### For Development

If you're contributing to LLMBuilder:

```bash
pip install llmbuilder[dev]
```

This includes:
- `pytest` - For running tests
- `black` - For code formatting
- `ruff` - For linting
- `mypy` - For type checking

### For Model Export

For exporting models to different formats:

```bash
pip install llmbuilder[export]
```

This includes:
- `onnx` - For ONNX export
- `onnxruntime` - For ONNX inference

## Environment Setup

### Virtual Environment (Recommended)

Create a dedicated virtual environment for LLMBuilder:

=== "Using venv"
    ```bash
    # Create virtual environment
    python -m venv llmbuilder-env
    
    # Activate it
    # On Windows:
    llmbuilder-env\Scripts\activate
    # On macOS/Linux:
    source llmbuilder-env/bin/activate
    
    # Install LLMBuilder
    pip install llmbuilder
    ```

=== "Using conda"
    ```bash
    # Create conda environment
    conda create -n llmbuilder python=3.9
    conda activate llmbuilder
    
    # Install LLMBuilder
    pip install llmbuilder
    ```

### Environment Variables

You can set these optional environment variables:

```bash
# Enable slow tests (for development)
export RUN_SLOW=1

# Enable performance tests (for development)
export RUN_PERF=1

# Set default device
export LLMBUILDER_DEVICE=cuda  # or 'cpu'

# Set cache directory
export LLMBUILDER_CACHE_DIR=/path/to/cache
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'torch'

**Solution**: Install PyTorch first:
```bash
pip install torch
```

#### CUDA out of memory

**Solution**: Use CPU-only installation or reduce batch size:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### Permission denied errors

**Solution**: Use `--user` flag or virtual environment:
```bash
pip install --user llmbuilder
```

#### Package conflicts

**Solution**: Create a fresh virtual environment:
```bash
python -m venv fresh-env
source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows
pip install llmbuilder
```

### Getting Help

If you encounter issues:

1. **Check the logs**: LLMBuilder provides detailed error messages
2. **Search existing issues**: [GitHub Issues](https://github.com/Qubasehq/llmbuilder-package/issues)
3. **Create a new issue**: Include your system info and error messages
4. **Join discussions**: [GitHub Discussions](https://github.com/Qubasehq/llmbuilder-package/discussions)

### System Information

To help with troubleshooting, you can gather system information:

```python
import llmbuilder
import torch
import sys
import platform

print(f"LLMBuilder version: {llmbuilder.__version__}")
print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
print(f"Platform: {platform.platform()}")
```

## Next Steps

Once you have LLMBuilder installed:

1. **[Quick Start](quickstart.md)** - Get up and running in 5 minutes
2. **[First Model](first-model.md)** - Train your first language model
3. **[User Guide](../user-guide/configuration.md)** - Learn about all features

---

!!! tip "Pro Tip"
    For the best experience, we recommend using a virtual environment and installing the GPU version of PyTorch if you have a compatible NVIDIA GPU.