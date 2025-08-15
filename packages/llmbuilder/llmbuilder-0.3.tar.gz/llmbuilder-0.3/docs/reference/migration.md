# Migration Guide

This guide helps you migrate from legacy LLMBuilder scripts and configurations to the new package structure. Whether you're upgrading from older versions or transitioning from standalone scripts, this guide covers all the changes you need to know.

## 🎯 Overview

The LLMBuilder package represents a major evolution from the original standalone scripts. Key improvements include:

- **Unified API**: Single import for all functionality
- **Better Configuration**: Structured, validated configurations
- **CLI Interface**: Comprehensive command-line tools
- **Modular Design**: Use only what you need
- **Better Documentation**: Complete guides and examples

## 📋 Migration Checklist

- [ ] Update Python version to 3.8+
- [ ] Install new LLMBuilder package
- [ ] Convert configuration files
- [ ] Update import statements
- [ ] Migrate training scripts
- [ ] Update CLI commands
- [ ] Test functionality
- [ ] Update deployment scripts

## 🔄 Configuration Migration

### Legacy Configuration Format

**Old format (config.json):**
```json
{
  "n_layer": 12,
  "n_head": 12,
  "n_embd": 768,
  "block_size": 1024,
  "dropout": 0.1,
  "bias": true,
  "vocab_size": 16000,
  "device": "cuda",
  "batch_size": 16,
  "learning_rate": 3e-4,
  "max_iters": 10000,
  "eval_interval": 500,
  "eval_iters": 100
}
```

### New Configuration Format

**New format (structured):**
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
  },
  "training": {
    "batch_size": 16,
    "learning_rate": 3e-4,
    "num_epochs": 10,
    "warmup_steps": 1000,
    "weight_decay": 0.01,
    "max_grad_norm": 1.0,
    "save_every": 1000,
    "eval_every": 500,
    "log_every": 100
  },
  "system": {
    "device": "cuda",
    "seed": 42,
    "deterministic": false
  }
}
```

### Automatic Migration

LLMBuilder provides automatic migration for legacy configurations:

```python
import llmbuilder as lb

# Load legacy configuration (automatically migrated)
config = lb.load_config("legacy_config.json")

# Or migrate explicitly
from llmbuilder.config import migrate_legacy_config
new_config = migrate_legacy_config("legacy_config.json")
new_config.save("new_config.json")
```

### Configuration Key Mapping

| Legacy Key | New Key | Notes |
|------------|---------|-------|
| `n_layer` | `model.num_layers` | Number of transformer layers |
| `n_head` | `model.num_heads` | Number of attention heads |
| `n_embd` | `model.embedding_dim` | Embedding dimension |
| `block_size` | `model.max_seq_length` | Maximum sequence length |
| `dropout` | `model.dropout` | Dropout rate |
| `bias` | `model.bias` | Use bias in linear layers |
| `vocab_size` | `model.vocab_size` | Vocabulary size |
| `device` | `system.device` | Training device |
| `batch_size` | `training.batch_size` | Batch size |
| `learning_rate` | `training.learning_rate` | Learning rate |
| `max_iters` | `training.max_steps` | Maximum training steps |
| `eval_interval` | `training.eval_every` | Evaluation frequency |

## 🐍 Code Migration

### Legacy Import Pattern

**Old way:**
```python
# Legacy imports
from model import GPTConfig, GPT
from train import train
from sample import sample
import tiktoken

# Legacy usage
config = GPTConfig(
    n_layer=12,
    n_head=12,
    n_embd=768,
    block_size=1024,
    vocab_size=50257
)

model = GPT(config)
```

### New Import Pattern

**New way:**
```python
# New unified import
import llmbuilder as lb

# New usage
config = lb.load_config(preset="gpu_medium")
model = lb.build_model(config.model)
```

### Training Script Migration

**Legacy training script:**
```python
# train.py (legacy)
import torch
from model import GPTConfig, GPT
from dataset import get_batch

# Configuration
config = GPTConfig(...)
model = GPT(config)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)

# Training loop
for iter in range(max_iters):
    X, Y = get_batch('train')
    logits, loss = model(X, Y)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if iter % eval_interval == 0:
        evaluate()
```

**New training script:**
```python
# train.py (new)
import llmbuilder as lb
from llmbuilder.data import TextDataset

# Configuration
config = lb.load_config(preset="gpu_medium")
model = lb.build_model(config.model)

# Dataset
dataset = TextDataset("data.txt", block_size=config.model.max_seq_length)

# Training (handled automatically)
results = lb.train_model(model, dataset, config.training)
```

### Generation Script Migration

**Legacy generation:**
```python
# sample.py (legacy)
import torch
from model import GPT
import tiktoken

# Load model
model = GPT.from_pretrained('model.pt')
enc = tiktoken.get_encoding("gpt2")

# Generate
context = enc.encode("Hello")
generated = model.generate(context, max_new_tokens=100)
text = enc.decode(generated)
```

**New generation:**
```python
# generate.py (new)
import llmbuilder as lb

# Generate (much simpler)
text = lb.generate_text(
    model_path="model.pt",
    tokenizer_path="tokenizer/",
    prompt="Hello",
    max_new_tokens=100
)
```

## 🖥️ CLI Migration

### Legacy CLI Commands

**Old commands:**
```bash
# Legacy training
python train.py --config config.json --data data.txt

# Legacy generation
python sample.py --model model.pt --prompt "Hello" --num_samples 5

# Legacy data preparation
python prepare_data.py --input raw/ --output data.txt
```

### New CLI Commands

**New commands:**
```bash
# New training
llmbuilder train model --config config.json --data data.txt --output model/

# New generation
llmbuilder generate text --model model.pt --tokenizer tokenizer/ --prompt "Hello"

# New data preparation
llmbuilder data load --input raw/ --output data.txt --clean
```

### CLI Command Mapping

| Legacy Command | New Command | Notes |
|----------------|-------------|-------|
| `python train.py` | `llmbuilder train model` | Unified training interface |
| `python sample.py` | `llmbuilder generate text` | Enhanced generation options |
| `python prepare_data.py` | `llmbuilder data load` | Better data processing |
| `python eval.py` | `llmbuilder model evaluate` | Built-in evaluation |

## 📊 Data Format Migration

### Legacy Data Format

**Old format:**
- Single text file with raw concatenated text
- Manual tokenization required
- No metadata or structure

### New Data Format

**New format:**
- Multiple input formats supported (PDF, DOCX, etc.)
- Automatic cleaning and preprocessing
- Structured dataset with metadata
- Built-in train/validation splitting

**Migration example:**
```python
# Legacy data preparation
with open('data.txt', 'r') as f:
    text = f.read()

# Tokenize manually
import tiktoken
enc = tiktoken.get_encoding("gpt2")
tokens = enc.encode(text)

# New data preparation
from llmbuilder.data import DataLoader, TextDataset

# Load and clean automatically
loader = DataLoader(clean_text=True, remove_duplicates=True)
texts = loader.load_directory("raw_data/")

# Create structured dataset
dataset = TextDataset(
    texts,
    block_size=1024,
    stride=512,
    train_split=0.9
)
```

## 🔧 Model Architecture Migration

### Legacy Model Definition

**Old way:**
```python
class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        # Manual layer definition...
        
    def forward(self, idx, targets=None):
        # Manual forward pass...
```

### New Model Definition

**New way:**
```python
# Use built-in model builder
import llmbuilder as lb

config = lb.load_config(preset="gpu_medium")
model = lb.build_model(config.model)

# Or customize if needed
from llmbuilder.model import GPTModel
from llmbuilder.config import ModelConfig

custom_config = ModelConfig(
    vocab_size=32000,
    num_layers=16,
    num_heads=16,
    embedding_dim=1024
)

model = GPTModel(custom_config)
```

## 🚀 Deployment Migration

### Legacy Deployment

**Old way:**
```python
# Manual model saving/loading
torch.save({
    'model': model.state_dict(),
    'config': config,
    'iter_num': iter_num,
}, 'model.pt')

# Manual inference setup
checkpoint = torch.load('model.pt')
model.load_state_dict(checkpoint['model'])
```

### New Deployment

**New way:**
```python
# Automatic model management
from llmbuilder.model import save_model, load_model

# Save with metadata
save_model(model, "model.pt", metadata={
    "training_config": config,
    "performance_metrics": results
})

# Load with validation
model = load_model("model.pt")

# Export for deployment
from llmbuilder.export import export_gguf
export_gguf("model.pt", "model.gguf", quantization="q4_0")
```

## 🔍 Testing Migration

### Verify Migration Success

**1. Configuration Test:**
```python
import llmbuilder as lb

# Test configuration loading
config = lb.load_config("migrated_config.json")
print(f"Config loaded: {config.model.num_layers} layers")

# Test model building
model = lb.build_model(config.model)
print(f"Model built: {sum(p.numel() for p in model.parameters()):,} parameters")
```

**2. Training Test:**
```python
# Test training pipeline
from llmbuilder.data import TextDataset

dataset = TextDataset("test_data.txt", block_size=512)
results = lb.train_model(model, dataset, config.training)
print(f"Training completed: {results.final_loss:.4f} final loss")
```

**3. Generation Test:**
```python
# Test generation
text = lb.generate_text(
    model_path="model.pt",
    tokenizer_path="tokenizer/",
    prompt="Test prompt",
    max_new_tokens=50
)
print(f"Generated: {text}")
```

## 🚨 Common Migration Issues

### Issue 1: Configuration Validation Errors

**Problem:** Legacy configs fail validation
**Solution:**
```python
from llmbuilder.config import validate_config, fix_config

# Validate and fix automatically
config = lb.load_config("legacy_config.json")
is_valid, errors = validate_config(config)

if not is_valid:
    fixed_config = fix_config(config, errors)
    fixed_config.save("fixed_config.json")
```

### Issue 2: Model Size Mismatch

**Problem:** Tokenizer vocab size doesn't match model
**Solution:**
```python
# Check and fix vocab size mismatch
from llmbuilder.tokenizer import Tokenizer

tokenizer = Tokenizer.from_pretrained("tokenizer/")
config.model.vocab_size = len(tokenizer)
```

### Issue 3: Performance Regression

**Problem:** New version is slower than legacy
**Solution:**
```python
# Enable performance optimizations
config.system.compile = True  # PyTorch 2.0 compilation
config.training.mixed_precision = "fp16"  # Mixed precision
config.training.dataloader_num_workers = 4  # Parallel data loading
```

### Issue 4: Generation Quality Differences

**Problem:** Generated text quality differs from legacy
**Solution:**
```python
# Match legacy generation parameters
from llmbuilder.inference import GenerationConfig

legacy_config = GenerationConfig(
    temperature=0.8,
    top_k=200,  # Legacy often used higher top_k
    do_sample=True,
    repetition_penalty=1.0  # Legacy default
)

text = lb.generate_text(
    model_path="model.pt",
    tokenizer_path="tokenizer/",
    prompt=prompt,
    config=legacy_config
)
```

## 📚 Migration Examples

### Complete Migration Script

```python
#!/usr/bin/env python3
"""
Complete migration script from legacy LLMBuilder to new package.
"""

import json
import shutil
from pathlib import Path
import llmbuilder as lb

def migrate_project(legacy_dir, new_dir):
    """Migrate entire legacy project to new structure."""
    
    legacy_path = Path(legacy_dir)
    new_path = Path(new_dir)
    new_path.mkdir(exist_ok=True)
    
    print(f"Migrating {legacy_dir} -> {new_dir}")
    
    # 1. Migrate configuration
    legacy_config = legacy_path / "config.json"
    if legacy_config.exists():
        print("Migrating configuration...")
        config = lb.load_config(str(legacy_config))
        config.save(str(new_path / "config.json"))
    
    # 2. Copy and organize data
    print("Organizing data...")
    data_dir = new_path / "data"
    data_dir.mkdir(exist_ok=True)
    
    for data_file in legacy_path.glob("*.txt"):
        if "data" in data_file.name.lower():
            shutil.copy2(data_file, data_dir / data_file.name)
    
    # 3. Migrate model if exists
    model_files = list(legacy_path.glob("*.pt"))
    if model_files:
        print("Migrating model...")
        model_dir = new_path / "model"
        model_dir.mkdir(exist_ok=True)
        
        for model_file in model_files:
            shutil.copy2(model_file, model_dir / model_file.name)
    
    # 4. Create new training script
    print("Creating new training script...")
    create_training_script(new_path)
    
    print("Migration completed!")

def create_training_script(project_dir):
    """Create new training script using LLMBuilder package."""
    
    script_content = '''#!/usr/bin/env python3
"""
Migrated training script using LLMBuilder package.
"""

import llmbuilder as lb
from llmbuilder.data import TextDataset

def main():
    # Load configuration
    config = lb.load_config("config.json")
    
    # Build model
    model = lb.build_model(config.model)
    
    # Prepare dataset
    dataset = TextDataset(
        "data/training_data.txt",
        block_size=config.model.max_seq_length
    )
    
    # Train model
    results = lb.train_model(model, dataset, config.training)
    
    print(f"Training completed: {results.final_loss:.4f} final loss")

if __name__ == "__main__":
    main()
'''
    
    script_path = project_dir / "train.py"
    with open(script_path, 'w') as f:
        f.write(script_content)

# Usage
if __name__ == "__main__":
    migrate_project("legacy_project/", "new_project/")
```

## ✅ Post-Migration Checklist

After migration, verify these items:

- [ ] **Configuration loads without errors**
- [ ] **Model builds with correct architecture**
- [ ] **Training runs successfully**
- [ ] **Generation produces expected quality**
- [ ] **Performance meets expectations**
- [ ] **All CLI commands work**
- [ ] **Export functionality works**
- [ ] **Tests pass**

## 🆘 Getting Help

If you encounter issues during migration:

1. **Check the FAQ**: Common migration issues are covered
2. **GitHub Issues**: Search for similar migration problems
3. **GitHub Discussions**: Ask the community for help
4. **Documentation**: Review the complete guides
5. **Examples**: Look at working migration examples

---

!!! tip "Migration Tips"
    - Start with a small test project before migrating everything
    - Keep backups of your legacy code and models
    - Test thoroughly after migration
    - Take advantage of new features like automatic data cleaning
    - Update your deployment scripts to use the new export functionality