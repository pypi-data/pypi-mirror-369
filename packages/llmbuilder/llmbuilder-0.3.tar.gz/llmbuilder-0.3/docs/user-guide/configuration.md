# Configuration

LLMBuilder uses a hierarchical configuration system that makes it easy to customize every aspect of your model training and inference. This guide covers all configuration options and best practices.

## 🎯 Configuration Overview

LLMBuilder configurations are organized into logical sections:

```mermaid
graph TB
    A[Configuration] --> B[Model Config]
    A --> C[Training Config]
    A --> D[Data Config]
    A --> E[System Config]
    
    B --> B1[Architecture]
    B --> B2[Vocabulary]
    B --> B3[Sequence Length]
    
    C --> C1[Learning Rate]
    C --> C2[Batch Size]
    C --> C3[Optimization]
    
    D --> D1[Preprocessing]
    D --> D2[Tokenization]
    D --> D3[Validation Split]
    
    E --> E1[Device]
    E --> E2[Memory]
    E --> E3[Logging]
```

## 📋 Configuration Methods

### Method 1: Using Templates (Recommended)

LLMBuilder provides pre-configured templates for common use cases:

```bash
# List available templates
llmbuilder config templates

# Create configuration from template
llmbuilder config from-template basic_config --output my_config.json

# Create with custom overrides
llmbuilder config from-template basic_config --output my_config.json \
  --override model.vocab_size=24000 \
  --override training.batch_size=32
```

Available templates:

| Template | Use Case | Vocab Size | Layers | Device | Best For |
|----------|----------|------------|--------|---------|----------|
| `basic_config` | General purpose | 16,000 | 8 | auto | Balanced training |
| `cpu_optimized_config` | CPU training | 8,000 | 4 | cpu | Limited resources |
| `advanced_processing_config` | Full features | 32,000 | 12 | cuda | Large datasets |
| `inference_optimized_config` | Inference only | 16,000 | 8 | auto | Production deployment |
| `large_scale_config` | Large models | 50,000 | 24 | cuda | High-end hardware |

### Method 2: Using Code Presets

```python
from llmbuilder.config.defaults import DefaultConfigs

# Load a preset configuration
config = DefaultConfigs.get_preset("cpu_small")
config = DefaultConfigs.get_preset("gpu_medium")
config = DefaultConfigs.get_preset("gpu_large")
config = DefaultConfigs.get_preset("inference")
```

### Method 3: From Configuration File

```python
from llmbuilder.config.manager import load_config

# Load from JSON file
config = load_config("my_config.json")

# Using the configuration manager directly
from llmbuilder.config.manager import config_manager
config = config_manager.load_config_file("my_config.json")
```

### Method 4: Programmatic Configuration

```python
from llmbuilder.config import Config, ModelConfig, TrainingConfig

config = Config(
    model=ModelConfig(
        vocab_size=16000,
        num_layers=12,
        num_heads=12,
        embedding_dim=768,
        max_seq_length=1024,
        dropout=0.1
    ),
    training=TrainingConfig(
        batch_size=16,
        num_epochs=10,
        learning_rate=3e-4,
        warmup_steps=1000
    )
)
```

## 🧠 Model Configuration

### Core Architecture Settings

```json
{
  "model": {
    "vocab_size": 16000,
    "num_layers": 12,
    "num_heads": 12,
    "embedding_dim": 768,
    "max_seq_length": 1024,
    "dropout": 0.1,
    "bias": true,
    "model_type": "gpt"
  }
}
```

#### Parameter Explanations

**`vocab_size`** (int, default: 16000)
: Size of the vocabulary. Must match your tokenizer's vocabulary size.

**`num_layers`** (int, default: 12)
: Number of transformer layers. More layers = more capacity but slower training.

**`num_heads`** (int, default: 12)
: Number of attention heads per layer. Should divide `embedding_dim` evenly.

**`embedding_dim`** (int, default: 768)
: Dimension of token embeddings and hidden states. Larger = more capacity.

**`max_seq_length`** (int, default: 1024)
: Maximum sequence length the model can process. Affects memory usage quadratically.

**`dropout`** (float, default: 0.1)
: Dropout rate for regularization. Higher values prevent overfitting.

### Advanced Model Settings

```json
{
  "model": {
    "activation": "gelu",
    "layer_norm_eps": 1e-5,
    "initializer_range": 0.02,
    "use_cache": true,
    "gradient_checkpointing": false,
    "tie_word_embeddings": true
  }
}
```

**`activation`** (str, default: "gelu")
: Activation function. Options: "gelu", "relu", "swish", "silu".

**`gradient_checkpointing`** (bool, default: false)
: Trade compute for memory. Enables training larger models with less GPU memory.

**`tie_word_embeddings`** (bool, default: true)
: Share input and output embedding weights. Reduces parameters by ~vocab_size * embedding_dim.

## 🏋️ Training Configuration

### Basic Training Settings

```json
{
  "training": {
    "batch_size": 16,
    "num_epochs": 10,
    "learning_rate": 3e-4,
    "weight_decay": 0.01,
    "max_grad_norm": 1.0,
    "warmup_steps": 1000,
    "save_every": 1000,
    "eval_every": 500,
    "log_every": 100
  }
}
```

#### Parameter Explanations

**`batch_size`** (int, default: 16)
: Number of samples per training step. Larger batches are more stable but use more memory.

**`learning_rate`** (float, default: 3e-4)
: Step size for parameter updates. Too high = unstable, too low = slow convergence.

**`weight_decay`** (float, default: 0.01)
: L2 regularization strength. Helps prevent overfitting.

**`max_grad_norm`** (float, default: 1.0)
: Gradient clipping threshold. Prevents exploding gradients.

**`warmup_steps`** (int, default: 1000)
: Number of steps to linearly increase learning rate from 0 to target value.

### Advanced Training Settings

```json
{
  "training": {
    "optimizer": "adamw",
    "scheduler": "cosine",
    "beta1": 0.9,
    "beta2": 0.999,
    "eps": 1e-8,
    "gradient_accumulation_steps": 1,
    "mixed_precision": "fp16",
    "dataloader_num_workers": 4,
    "pin_memory": true
  }
}
```

**`optimizer`** (str, default: "adamw")
: Optimization algorithm. Options: "adamw", "adam", "sgd", "adafactor".

**`scheduler`** (str, default: "cosine")
: Learning rate schedule. Options: "cosine", "linear", "constant", "polynomial".

**`mixed_precision`** (str, default: "fp16")
: Use mixed precision training. Options: "fp16", "bf16", "fp32".

**`gradient_accumulation_steps`** (int, default: 1)
: Accumulate gradients over multiple steps. Effective batch size = batch_size * gradient_accumulation_steps.

## 📊 Data Configuration

### Basic Data Settings

```json
{
  "data": {
    "max_length": 1024,
    "stride": 512,
    "min_length": 10,
    "clean_text": true,
    "remove_duplicates": true,
    "shuffle": true,
    "validation_split": 0.1,
    "test_split": 0.1
  }
}
```

### Advanced Data Processing

LLMBuilder includes sophisticated data processing capabilities:

```json
{
  "data": {
    "ingestion": {
      "supported_formats": ["html", "markdown", "epub", "pdf", "txt"],
      "batch_size": 100,
      "num_workers": 4,
      "output_format": "txt",
      "preserve_structure": false,
      "extract_metadata": true,
      
      "html_parser": "lxml",
      "remove_scripts": true,
      "remove_styles": true,
      
      "enable_ocr": true,
      "ocr_quality_threshold": 0.5,
      "ocr_language": "eng",
      "pdf_extraction_method": "auto",
      
      "extract_toc": true,
      "chapter_separator": "\n\n---\n\n"
    },
    "deduplication": {
      "enable_exact_deduplication": true,
      "enable_semantic_deduplication": true,
      "similarity_threshold": 0.85,
      "embedding_model": "all-MiniLM-L6-v2",
      "batch_size": 1000,
      "chunk_size": 512,
      "min_text_length": 50,
      "normalize_text": true,
      "use_gpu_for_embeddings": true,
      "embedding_cache_size": 10000,
      "similarity_metric": "cosine"
    }
  }
}
```

### Data Processing Options

**`max_length`** (int, default: 1024)
: Maximum sequence length. Should match model's `max_seq_length`.

**`stride`** (int, default: 512)
: Overlap between consecutive sequences. Larger stride = less overlap = more diverse samples.

**`min_length`** (int, default: 10)
: Minimum sequence length to keep. Filters out very short sequences.

### Document Ingestion Settings

**`supported_formats`** (list, default: ["html", "markdown", "epub", "pdf", "txt"])
: File formats to process during ingestion.

**`enable_ocr`** (bool, default: true)
: Enable OCR fallback for scanned PDFs.

**`ocr_quality_threshold`** (float, default: 0.5)
: Quality threshold to trigger OCR (0.0-1.0).

### Deduplication Settings

**`enable_exact_deduplication`** (bool, default: true)
: Remove exact duplicate texts using normalized hashing.

**`enable_semantic_deduplication`** (bool, default: true)
: Remove semantically similar texts using embeddings.

**`similarity_threshold`** (float, default: 0.85)
: Similarity threshold for semantic deduplication (0.0-1.0).

**`use_gpu_for_embeddings`** (bool, default: true)
: Use GPU acceleration for embedding computation.

## 🔤 Tokenizer Training Configuration

LLMBuilder supports advanced tokenizer training with multiple algorithms:

```json
{
  "tokenizer_training": {
    "vocab_size": 16000,
    "algorithm": "bpe",
    "min_frequency": 2,
    "special_tokens": ["<pad>", "<unk>", "<s>", "</s>"],
    "character_coverage": 0.9995,
    "max_sentence_length": 4192,
    "shuffle_input_sentence": true,
    "normalization_rule_name": "nmt_nfkc_cf",
    "remove_extra_whitespaces": true,
    "add_dummy_prefix": true,
    "continuing_subword_prefix": "##",
    "end_of_word_suffix": "",
    "num_threads": 4,
    "max_training_time": 3600,
    "validation_split": 0.1
  }
}
```

### Tokenizer Algorithm Options

**`algorithm`** (str, default: "bpe")
: Tokenization algorithm. Options: "bpe", "unigram", "wordpiece", "sentencepiece".

**`vocab_size`** (int, default: 16000)
: Target vocabulary size. Must match model's vocab_size.

**`min_frequency`** (int, default: 2)
: Minimum frequency for subword units to be included.

**`character_coverage`** (float, default: 0.9995)
: Character coverage for SentencePiece (0.0-1.0).

### Algorithm-Specific Settings

For **BPE and WordPiece**:
- `continuing_subword_prefix`: Prefix for continuing subwords (e.g., "##")
- `end_of_word_suffix`: Suffix for end-of-word tokens

For **SentencePiece**:
- `normalization_rule_name`: Text normalization rule
- `add_dummy_prefix`: Add dummy prefix for better tokenization
- `shuffle_input_sentence`: Shuffle input during training

## 🔄 GGUF Conversion Configuration

Configure model conversion to GGUF format for inference:

```json
{
  "gguf_conversion": {
    "quantization_level": "Q8_0",
    "validate_output": true,
    "conversion_timeout": 3600,
    "preferred_script": "auto",
    "script_paths": {},
    "output_naming": "auto",
    "custom_suffix": "",
    "preserve_metadata": true
  }
}
```

### Quantization Options

**`quantization_level`** (str, default: "Q8_0")
: Quantization level. Options: "F32", "F16", "Q8_0", "Q5_1", "Q5_0", "Q4_1", "Q4_0".

| Level | Precision | Size | Quality | Use Case |
|-------|-----------|------|---------|----------|
| F32 | 32-bit | Largest | Highest | Research, debugging |
| F16 | 16-bit | Large | High | High-quality inference |
| Q8_0 | 8-bit | Medium | Good | Balanced quality/size |
| Q5_1 | 5-bit | Small | Fair | Mobile deployment |
| Q4_0 | 4-bit | Smallest | Lower | Edge devices |

### Conversion Settings

**`validate_output`** (bool, default: true)
: Validate converted GGUF files for integrity.

**`preferred_script`** (str, default: "auto")
: Preferred conversion script. Options: "auto", "llama_cpp", "convert_hf_to_gguf".

**`conversion_timeout`** (int, default: 3600)
: Maximum time (seconds) to wait for conversion.

**`output_naming`** (str, default: "auto")
: Output file naming strategy. Options: "auto", "quantization_suffix", "custom".

## 🖥️ System Configuration

```json
{
  "system": {
    "device": "auto",
    "num_gpus": 1,
    "distributed": false,
    "compile": false,
    "seed": 42,
    "deterministic": false,
    "benchmark": true,
    "cache_dir": "./cache",
    "output_dir": "./output",
    "logging_level": "INFO"
  }
}
```

### Device and Performance Settings

**`device`** (str, default: "auto")
: Device to use. Options: "auto", "cpu", "cuda", "cuda:0", etc.

**`compile`** (bool, default: false)
: Use PyTorch 2.0 compilation for faster training (experimental).

**`benchmark`** (bool, default: true)
: Enable cuDNN benchmarking for consistent input sizes.

## 🛠️ Creating Custom Configurations

### Using the CLI

```bash
# Interactive configuration creation
llmbuilder config create --interactive

# Create from preset and customize
llmbuilder config create --preset cpu_small --output my_config.json
```

### Programmatic Creation

```python
from llmbuilder.config import Config, ModelConfig, TrainingConfig

# Create custom configuration
config = Config(
    model=ModelConfig(
        vocab_size=32000,  # Larger vocabulary
        num_layers=24,     # Deeper model
        num_heads=16,      # More attention heads
        embedding_dim=1024, # Larger embeddings
        max_seq_length=2048, # Longer sequences
        dropout=0.1
    ),
    training=TrainingConfig(
        batch_size=8,      # Smaller batch for larger model
        num_epochs=20,     # More training
        learning_rate=1e-4, # Lower learning rate
        warmup_steps=2000,  # Longer warmup
        gradient_accumulation_steps=4  # Effective batch size = 32
    )
)

# Save configuration
config.save("custom_config.json")
```

### Configuration Inheritance

```python
# Start with a preset
base_config = lb.load_config(preset="gpu_medium")

# Modify specific settings
base_config.model.num_layers = 18
base_config.training.learning_rate = 1e-4
base_config.training.batch_size = 12

# Save modified configuration
base_config.save("modified_config.json")
```

## 🔧 Configuration Validation

### CLI Validation (Recommended)

```bash
# Basic validation
llmbuilder config validate my_config.json

# Detailed validation with summary
llmbuilder config validate my_config.json --detailed

# Show configuration summary
llmbuilder config summary my_config.json
```

### Programmatic Validation

```python
from llmbuilder.config.manager import validate_config, config_manager

# Simple validation
is_valid = validate_config("my_config.json")

# Detailed validation
result = config_manager.validate_config_file("my_config.json")
if result["valid"]:
    print("Configuration is valid!")
    print("Summary:", result["config_summary"])
else:
    print("Validation errors:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### Automatic Validation

LLMBuilder automatically validates configurations when loading:

```python
from llmbuilder.config.manager import load_config

try:
    config = load_config("my_config.json")
    print("Configuration loaded and validated successfully!")
except ValueError as e:
    print(f"Configuration validation failed: {e}")
```

### Common Validation Errors

!!! warning "Common Issues"
    - **`num_heads` doesn't divide `embedding_dim`**: embedding_dim must be divisible by num_heads
    - **`vocab_size` mismatch**: Must match tokenizer vocabulary size
    - **Memory constraints**: batch_size × max_seq_length × embedding_dim too large for available memory
    - **Invalid device**: Specified device not available

## 📈 Performance Tuning

### Memory Optimization

```json
{
  "model": {
    "gradient_checkpointing": true,
    "tie_word_embeddings": true
  },
  "training": {
    "mixed_precision": "fp16",
    "gradient_accumulation_steps": 4,
    "batch_size": 4
  }
}
```

### Speed Optimization

```json
{
  "system": {
    "compile": true,
    "benchmark": true
  },
  "training": {
    "dataloader_num_workers": 8,
    "pin_memory": true
  }
}
```

### Quality Optimization

```json
{
  "model": {
    "num_layers": 24,
    "embedding_dim": 1024,
    "dropout": 0.1
  },
  "training": {
    "learning_rate": 1e-4,
    "warmup_steps": 2000,
    "weight_decay": 0.01
  }
}
```

## 🎯 Configuration Best Practices

### 1. Start with Presets

Always start with a preset that matches your hardware:

```python
# For CPU development
config = lb.load_config(preset="cpu_small")

# For single GPU
config = lb.load_config(preset="gpu_medium")

# For multiple GPUs
config = lb.load_config(preset="gpu_large")
```

### 2. Scale Gradually

When increasing model size, scale parameters proportionally:

```python
# If doubling embedding_dim, consider:
config.model.embedding_dim *= 2
config.model.num_heads *= 2  # Keep head_dim constant
config.training.learning_rate *= 0.7  # Reduce LR for larger models
config.training.warmup_steps *= 2  # Longer warmup
```

### 3. Monitor Memory Usage

```python
# Check memory requirements before training
from llmbuilder.utils import estimate_memory_usage

memory_gb = estimate_memory_usage(config)
print(f"Estimated memory usage: {memory_gb:.1f} GB")
```

### 4. Use Configuration Templates

Create templates for common scenarios:

```python
# templates/research_config.py
def get_research_config(vocab_size, dataset_size):
    """Configuration optimized for research experiments."""
    return Config(
        model=ModelConfig(
            vocab_size=vocab_size,
            num_layers=12 if dataset_size < 1e6 else 24,
            embedding_dim=768,
            max_seq_length=1024,
            dropout=0.1
        ),
        training=TrainingConfig(
            batch_size=16,
            learning_rate=3e-4,
            num_epochs=10 if dataset_size < 1e6 else 20,
            warmup_steps=min(1000, dataset_size // 100)
        )
    )
```

## 🔍 Debugging Configuration Issues

### Enable Verbose Logging

```json
{
  "system": {
    "logging_level": "DEBUG"
  }
}
```

### Check Configuration Summary

```python
config = lb.load_config("my_config.json")
print(config.summary())
```

### Validate Against Hardware

```bash
llmbuilder config validate my_config.json --check-hardware
```

## 📚 Configuration Examples

### Minimal CPU Configuration

```json
{
  "model": {
    "vocab_size": 8000,
    "num_layers": 4,
    "num_heads": 4,
    "embedding_dim": 256,
    "max_seq_length": 512
  },
  "training": {
    "batch_size": 4,
    "num_epochs": 5,
    "learning_rate": 1e-3
  },
  "data": {
    "ingestion": {
      "supported_formats": ["txt"],
      "num_workers": 2,
      "enable_ocr": false
    },
    "deduplication": {
      "enable_semantic_deduplication": false,
      "use_gpu_for_embeddings": false
    }
  },
  "tokenizer_training": {
    "algorithm": "bpe",
    "vocab_size": 8000,
    "num_threads": 2
  },
  "system": {
    "device": "cpu"
  }
}
```

### High-Performance GPU Configuration

```json
{
  "model": {
    "vocab_size": 32000,
    "num_layers": 24,
    "num_heads": 16,
    "embedding_dim": 1024,
    "max_seq_length": 2048,
    "gradient_checkpointing": true
  },
  "training": {
    "batch_size": 8,
    "num_epochs": 20,
    "learning_rate": 1e-4,
    "mixed_precision": "fp16",
    "gradient_accumulation_steps": 4
  },
  "data": {
    "ingestion": {
      "supported_formats": ["html", "markdown", "epub", "pdf", "txt"],
      "batch_size": 200,
      "num_workers": 8,
      "enable_ocr": true,
      "ocr_quality_threshold": 0.7
    },
    "deduplication": {
      "enable_exact_deduplication": true,
      "enable_semantic_deduplication": true,
      "similarity_threshold": 0.9,
      "use_gpu_for_embeddings": true,
      "batch_size": 2000
    }
  },
  "tokenizer_training": {
    "algorithm": "sentencepiece",
    "vocab_size": 32000,
    "character_coverage": 0.9998,
    "num_threads": 8
  },
  "gguf_conversion": {
    "quantization_level": "Q4_0",
    "validate_output": true,
    "preferred_script": "llama_cpp"
  },
  "system": {
    "device": "cuda",
    "compile": true
  }
}
```

### Advanced Data Processing Configuration

```json
{
  "data": {
    "max_length": 2048,
    "ingestion": {
      "supported_formats": ["html", "markdown", "epub", "pdf"],
      "batch_size": 500,
      "num_workers": 16,
      "output_format": "jsonl",
      "preserve_structure": true,
      "extract_metadata": true,
      "html_parser": "lxml",
      "enable_ocr": true,
      "ocr_quality_threshold": 0.8,
      "pdf_extraction_method": "auto"
    },
    "deduplication": {
      "enable_exact_deduplication": true,
      "enable_semantic_deduplication": true,
      "similarity_threshold": 0.92,
      "embedding_model": "all-MiniLM-L6-v2",
      "batch_size": 5000,
      "chunk_size": 2048,
      "min_text_length": 200,
      "use_gpu_for_embeddings": true,
      "embedding_cache_size": 50000
    }
  },
  "tokenizer_training": {
    "algorithm": "sentencepiece",
    "vocab_size": 50000,
    "min_frequency": 5,
    "special_tokens": ["<pad>", "<unk>", "<s>", "</s>", "<mask>", "<cls>", "<sep>"],
    "character_coverage": 0.9998,
    "max_sentence_length": 16384,
    "num_threads": 16,
    "max_training_time": 14400
  }
}
```

### Inference-Optimized Configuration

```json
{
  "model": {
    "vocab_size": 16000,
    "num_layers": 8,
    "num_heads": 8,
    "embedding_dim": 512,
    "dropout": 0.0
  },
  "inference": {
    "max_new_tokens": 256,
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "repetition_penalty": 1.1
  },
  "gguf_conversion": {
    "quantization_level": "Q4_0",
    "validate_output": true,
    "output_naming": "quantization_suffix"
  },
  "system": {
    "device": "auto",
    "compile": true,
    "num_workers": 1
  }
}
```

### Fine-tuning Configuration

```json
{
  "training": {
    "learning_rate": 5e-5,
    "num_epochs": 3,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "save_every": 100
  },
  "data": {
    "max_length": 512,
    "stride": 256,
    "deduplication": {
      "enable_exact_deduplication": true,
      "enable_semantic_deduplication": false
    }
  },
  "tokenizer_training": {
    "algorithm": "bpe",
    "min_frequency": 1,
    "max_training_time": 600
  }
}
```

---

!!! tip "Configuration Tips"
    - Always validate your configuration before training
    - Start with presets and modify incrementally
    - Monitor memory usage and adjust batch size accordingly
    - Use gradient accumulation to simulate larger batch sizes
    - Save successful configurations for future use