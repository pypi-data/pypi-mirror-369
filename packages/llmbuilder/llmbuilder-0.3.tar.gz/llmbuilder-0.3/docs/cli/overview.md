# CLI Overview

LLMBuilder provides a comprehensive command-line interface (CLI) that makes it easy to train, fine-tune, and deploy language models without writing code. This guide covers all CLI commands and their usage.

## 🚀 Getting Started

### Installation Verification

First, verify that LLMBuilder is properly installed:

```bash
llmbuilder --version
llmbuilder --help
```

### Welcome Command

For first-time users, start with the welcome command:

```bash
llmbuilder welcome
```

This interactive command guides you through:
- Learning about LLMBuilder
- Creating configuration files
- Processing data
- Training models
- Generating text

## 📋 Command Structure

LLMBuilder CLI follows a hierarchical command structure:

```
llmbuilder [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS]
```

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--verbose`, `-v` | Enable verbose output |
| `--help` | Show help message |

### Main Commands

| Command | Description |
|---------|-------------|
| `welcome` | Interactive getting started guide |
| `info` | Display package information |
| `config` | Configuration management |
| `data` | Data processing and loading |
| `train` | Model training |
| `finetune` | Model fine-tuning |
| `generate` | Text generation |
| `model` | Model management |
| `export` | Model export utilities |

## 🎯 Command Categories

### Information Commands

#### `welcome`
Interactive getting started experience:

```bash
llmbuilder welcome
```

Features:
- Guided setup process
- Learn about LLMBuilder capabilities
- Quick access to common tasks
- Beginner-friendly explanations

#### `info`
Display package information and credits:

```bash
llmbuilder info
```

Shows:
- Package version and description
- Available modules and their purposes
- Quick command examples
- Links to documentation and support

### Configuration Commands

#### `config create`
Create configuration files with presets:

```bash
# Interactive configuration creation
llmbuilder config create --interactive

# Create from preset
llmbuilder config create --preset cpu_small --output config.json

# Available presets: cpu_small, gpu_medium, gpu_large, inference
```

#### `config validate`
Validate configuration files:

```bash
llmbuilder config validate config.json
```

#### `config list`
List available configuration presets:

```bash
llmbuilder config list
```

### Data Processing Commands

#### `data load`
Load and preprocess text data from various formats:

```bash
# Interactive data loading
llmbuilder data load --interactive

# Process specific directory
llmbuilder data load \
  --input ./documents \
  --output clean_text.txt \
  --format all \
  --clean \
  --min-length 100
```

#### `data tokenizer`
Train tokenizers on text data:

```bash
llmbuilder data tokenizer \
  --input training_data.txt \
  --output ./tokenizer \
  --vocab-size 16000 \
  --model-type bpe
```

### Training Commands

#### `train model`
Train language models from scratch:

```bash
# Interactive training setup
llmbuilder train model --interactive

# Direct training
llmbuilder train model \
  --config config.json \
  --data training_data.txt \
  --tokenizer ./tokenizer \
  --output ./model \
  --epochs 10 \
  --batch-size 16
```

#### `train resume`
Resume training from checkpoints:

```bash
llmbuilder train resume \
  --checkpoint ./model/checkpoint_1000.pt \
  --data training_data.txt \
  --output ./continued_model
```

### Fine-tuning Commands

#### `finetune model`
Fine-tune pre-trained models:

```bash
llmbuilder finetune model \
  --model ./pretrained_model/model.pt \
  --dataset domain_data.txt \
  --output ./finetuned_model \
  --epochs 5 \
  --lr 5e-5 \
  --use-lora
```

### Generation Commands

#### `generate text`
Generate text with trained models:

```bash
# Interactive generation
llmbuilder generate text --setup

# Direct generation
llmbuilder generate text \
  --model ./model/model.pt \
  --tokenizer ./tokenizer \
  --prompt "The future of AI is" \
  --max-tokens 100 \
  --temperature 0.8

# Interactive chat mode
llmbuilder generate text \
  --model ./model/model.pt \
  --tokenizer ./tokenizer \
  --interactive
```

### Model Management Commands

#### `model create`
Create new model architectures:

```bash
llmbuilder model create \
  --vocab-size 16000 \
  --layers 12 \
  --heads 12 \
  --dim 768 \
  --output ./new_model
```

#### `model info`
Display model information:

```bash
llmbuilder model info ./model/model.pt
```

#### `model evaluate`
Evaluate model performance:

```bash
llmbuilder model evaluate \
  ./model/model.pt \
  --dataset test_data.txt \
  --batch-size 32
```

### Export Commands

#### `export gguf`
Export models to GGUF format:

```bash
llmbuilder export gguf \
  ./model/model.pt \
  --output model.gguf \
  --quantization q4_0
```

#### `export onnx`
Export models to ONNX format:

```bash
llmbuilder export onnx \
  ./model/model.pt \
  --output model.onnx \
  --opset 11
```

#### `export quantize`
Quantize models for deployment:

```bash
llmbuilder export quantize \
  ./model/model.pt \
  --output quantized_model.pt \
  --method dynamic \
  --bits 8
```

## 🎨 Interactive Features

### Guided Setup

Many commands support `--interactive` or `--setup` flags for guided experiences:

```bash
# Interactive data loading
llmbuilder data load --interactive

# Interactive model training
llmbuilder train model --interactive

# Interactive text generation setup
llmbuilder generate text --setup
```

### Progress Indicators

LLMBuilder provides rich progress indicators:

```bash
# Training progress with real-time metrics
llmbuilder train model --data data.txt --output model/ --verbose

# Data processing with progress bars
llmbuilder data load --input docs/ --output data.txt --verbose
```

### Colorful Output

The CLI uses colors and emojis for better user experience:

- 🟢 **Green**: Success messages
- 🔵 **Blue**: Information and headers
- 🟡 **Yellow**: Warnings and prompts
- 🔴 **Red**: Errors
- 🎯 **Emojis**: Visual indicators for different operations

## 🔧 Advanced Usage

### Configuration Files

Use configuration files for complex setups:

```bash
# Create configuration
llmbuilder config create --preset gpu_medium --output training_config.json

# Use configuration in training
llmbuilder train model --config training_config.json --data data.txt --output model/
```

### Environment Variables

Set environment variables for default behavior:

```bash
# Set default device
export LLMBUILDER_DEVICE=cuda

# Set cache directory
export LLMBUILDER_CACHE_DIR=/path/to/cache

# Enable debug logging
export LLMBUILDER_LOG_LEVEL=DEBUG
```

### Batch Processing

Process multiple files or configurations:

```bash
# Process multiple data directories
llmbuilder data load \
  --input "dir1,dir2,dir3" \
  --output combined_data.txt

# Train multiple model variants
for preset in cpu_small gpu_medium gpu_large; do
  llmbuilder config create --preset $preset --output ${preset}_config.json
  llmbuilder train model --config ${preset}_config.json --data data.txt --output ${preset}_model/
done
```

### Pipeline Automation

Chain commands for complete workflows:

```bash
#!/bin/bash
# Complete training pipeline

# 1. Process data
llmbuilder data load \
  --input ./raw_documents \
  --output training_data.txt \
  --clean --min-length 100

# 2. Train tokenizer
llmbuilder data tokenizer \
  --input training_data.txt \
  --output ./tokenizer \
  --vocab-size 16000

# 3. Create configuration
llmbuilder config create \
  --preset gpu_medium \
  --output model_config.json

# 4. Train model
llmbuilder train model \
  --config model_config.json \
  --data training_data.txt \
  --tokenizer ./tokenizer \
  --output ./trained_model

# 5. Test generation
llmbuilder generate text \
  --model ./trained_model/model.pt \
  --tokenizer ./tokenizer \
  --prompt "Test generation" \
  --max-tokens 50

echo "Training pipeline completed!"
```

## 🚨 Error Handling

### Common Error Messages

#### Configuration Errors
```bash
❌ Configuration validation failed: num_heads (8) must divide embedding_dim (512)
💡 Try: Set num_heads to 4, 8, or 16
```

#### Data Errors
```bash
❌ No supported files found in directory: ./documents
💡 Supported formats: .txt, .pdf, .docx, .html, .md
```

#### Memory Errors
```bash
❌ CUDA out of memory
💡 Try: Reduce batch size with --batch-size 4 or use CPU with --device cpu
```

#### Model Errors
```bash
❌ Model file not found: ./model/model.pt
💡 Check the model path or train a model first with: llmbuilder train model
```

### Debugging Tips

Enable verbose output for detailed information:

```bash
llmbuilder --verbose train model --data data.txt --output model/
```

Check system information:

```bash
llmbuilder info --system
```

Validate configurations before use:

```bash
llmbuilder config validate config.json --strict
```

## 📊 Output and Logging

### Standard Output

LLMBuilder provides structured output:

```bash
🚀 Starting model training...
📊 Dataset: 10,000 samples
🧠 Model: 12.5M parameters
📈 Training progress:
  Epoch 1/10: loss=3.45, lr=0.0003, time=2m 15s
  Epoch 2/10: loss=2.87, lr=0.0003, time=2m 12s
  ...
✅ Training completed successfully!
💾 Model saved to: ./model/model.pt
```

### Log Files

Training and processing logs are automatically saved:

```
./model/
├── model.pt              # Trained model
├── config.json           # Training configuration
├── training.log          # Detailed training logs
├── metrics.json          # Training metrics
└── checkpoints/          # Training checkpoints
    ├── checkpoint_1000.pt
    ├── checkpoint_2000.pt
    └── ...
```

### JSON Output

Use `--json` flag for machine-readable output:

```bash
llmbuilder model info ./model/model.pt --json
```

```json
{
  "model_path": "./model/model.pt",
  "parameters": 12500000,
  "architecture": {
    "num_layers": 12,
    "num_heads": 12,
    "embedding_dim": 768,
    "vocab_size": 16000
  },
  "training_info": {
    "final_loss": 2.45,
    "training_time": "45m 23s",
    "epochs": 10
  }
}
```

## 🎯 Best Practices

### 1. Start Interactive

For new users, always start with interactive modes:

```bash
llmbuilder welcome
llmbuilder data load --interactive
llmbuilder train model --interactive
```

### 2. Use Configurations

Save and reuse configurations for consistency:

```bash
# Create and save configuration
llmbuilder config create --preset gpu_medium --output my_config.json

# Reuse configuration
llmbuilder train model --config my_config.json --data data.txt --output model/
```

### 3. Validate Before Training

Always validate configurations and data:

```bash
llmbuilder config validate config.json
llmbuilder data load --input data/ --output test.txt --dry-run
```

### 4. Monitor Progress

Use verbose mode for long-running operations:

```bash
llmbuilder --verbose train model --config config.json --data data.txt --output model/
```

### 5. Save Intermediate Results

Use checkpointing and intermediate saves:

```bash
llmbuilder train model \
  --config config.json \
  --data data.txt \
  --output model/ \
  --save-every 1000 \
  --eval-every 500
```

---

!!! tip "CLI Tips"
    - Use tab completion if available in your shell
    - Combine `--help` with any command to see all options
    - Use `--dry-run` flags when available to test commands
    - Save successful command combinations as shell scripts
    - Use configuration files for complex setups