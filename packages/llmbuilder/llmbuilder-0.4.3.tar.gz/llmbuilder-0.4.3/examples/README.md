# LLMBuilder Examples

This directory contains **working code examples** that you can run directly.

## 🚀 Quick Start

```bash
# Run the basic training example
python basic_training.py

# Install all optional dependencies for full functionality
pip install llmbuilder[all]
```

## 📁 Available Examples

- **`basic_training.py`** - Complete training pipeline demonstrating all major features

## 📚 Documentation

For detailed documentation, tutorials, and more examples, see:

**[📖 Examples Documentation](../docs/examples/README.md)**

The documentation includes:
- Step-by-step tutorials
- Configuration examples
- Troubleshooting guides
- Advanced workflows
- Performance optimization tips

## 🔧 Requirements

Some examples require optional dependencies:

```bash
# Install all features
pip install llmbuilder[all]

# Or install specific features
pip install llmbuilder[pdf]        # PDF processing
pip install llmbuilder[semantic]   # Semantic deduplication
pip install llmbuilder[conversion] # GGUF conversion
```

## 🐛 Issues?

If you encounter problems:

1. **Check dependencies**: `pip install llmbuilder[all]`
2. **Enable debug logging**: `export LLMBUILDER_LOG_LEVEL=DEBUG`
3. **See troubleshooting**: [Documentation](../docs/examples/README.md)
4. **Report issues**: [GitHub Issues](https://github.com/Qubasehq/llmbuilder-package/issues)

---

💡 **Tip**: Start with `basic_training.py` to see all features in action!