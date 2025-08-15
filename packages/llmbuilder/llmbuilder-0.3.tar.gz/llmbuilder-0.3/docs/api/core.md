# Core API

The core LLMBuilder API provides high-level functions for common tasks. These functions are designed to be simple to use while providing access to the full power of the framework.

## 🎯 Overview

The core API is accessible through the main `llmbuilder` module:

```python
import llmbuilder as lb

# High-level functions
config = lb.load_config(preset="cpu_small")
model = lb.build_model(config.model)
text = lb.generate_text(model_path, tokenizer_path, prompt)
```

## 📋 Core Functions

### Configuration Functions

::: llmbuilder.load_config
    options:
      show_source: true
      show_root_heading: true

### Model Functions

::: llmbuilder.build_model
    options:
      show_source: true
      show_root_heading: true

### Training Functions

::: llmbuilder.train_model
    options:
      show_source: true
      show_root_heading: true

::: llmbuilder.train
    options:
      show_source: true
      show_root_heading: true

### Generation Functions

::: llmbuilder.generate_text
    options:
      show_source: true
      show_root_heading: true

::: llmbuilder.interactive_cli
    options:
      show_source: true
      show_root_heading: true

### Fine-tuning Functions

::: llmbuilder.finetune_model
    options:
      show_source: true
      show_root_heading: true

## 🚀 Quick Examples

### Basic Training Pipeline

```python
import llmbuilder as lb

# 1. Load configuration
config = lb.load_config(preset="cpu_small")

# 2. Build model
model = lb.build_model(config.model)

# 3. Prepare dataset
from llmbuilder.data import TextDataset
dataset = TextDataset("training_data.txt", block_size=config.model.max_seq_length)

# 4. Train model
results = lb.train_model(model, dataset, config.training)

# 5. Generate text
text = lb.generate_text(
    model_path="./checkpoints/model.pt",
    tokenizer_path="./tokenizers",
    prompt="Hello world",
    max_new_tokens=50
)
```

### High-Level Training

```python
import llmbuilder as lb

# Complete training pipeline in one function
pipeline = lb.train(
    data_path="./my_data/",
    output_dir="./output/",
    config={
        "model": {"num_layers": 8, "embedding_dim": 512},
        "training": {"num_epochs": 10, "batch_size": 16}
    }
)

# Generate text after training
text = pipeline.generate("The future of AI is")
```

### Interactive Generation

```python
import llmbuilder as lb

# Start interactive text generation
lb.interactive_cli(
    model_path="./model/model.pt",
    tokenizer_path="./tokenizer/",
    temperature=0.8,
    max_new_tokens=100
)
```

## 🔧 Advanced Usage

### Custom Configuration

```python
import llmbuilder as lb
from llmbuilder.config import Config, ModelConfig, TrainingConfig

# Create custom configuration
config = Config(
    model=ModelConfig(
        vocab_size=32000,
        num_layers=24,
        num_heads=16,
        embedding_dim=1024
    ),
    training=TrainingConfig(
        batch_size=8,
        learning_rate=1e-4,
        num_epochs=20
    )
)

# Use with core functions
model = lb.build_model(config.model)
```

### Error Handling

```python
import llmbuilder as lb
from llmbuilder.utils import ModelError, DataError

try:
    config = lb.load_config("config.json")
    model = lb.build_model(config.model)
except ModelError as e:
    print(f"Model error: {e}")
except DataError as e:
    print(f"Data error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📊 Return Types

### Training Results

```python
results = lb.train_model(model, dataset, config)

# Access training metrics
print(f"Final loss: {results.final_loss}")
print(f"Training time: {results.training_time}")
print(f"Best validation loss: {results.best_val_loss}")
print(f"Model path: {results.model_path}")
```

### Generation Results

```python
# Simple string return
text = lb.generate_text(model_path, tokenizer_path, prompt)

# With detailed results
from llmbuilder.inference import generate_with_details

result = generate_with_details(
    model_path=model_path,
    tokenizer_path=tokenizer_path,
    prompt=prompt,
    return_details=True
)

print(f"Generated text: {result.text}")
print(f"Generation time: {result.generation_time}")
print(f"Tokens per second: {result.tokens_per_second}")
```

## 🎯 Best Practices

### 1. Configuration Management

```python
# Use presets as starting points
config = lb.load_config(preset="gpu_medium")

# Modify specific settings
config.model.num_layers = 16
config.training.learning_rate = 5e-5

# Save for reuse
config.save("my_config.json")
```

### 2. Resource Management

```python
# Check available resources
from llmbuilder.utils import get_device_info

device_info = get_device_info()
if device_info.has_cuda:
    config = lb.load_config(preset="gpu_medium")
else:
    config = lb.load_config(preset="cpu_small")
```

### 3. Error Recovery

```python
# Implement checkpointing
try:
    results = lb.train_model(model, dataset, config)
except KeyboardInterrupt:
    print("Training interrupted, saving checkpoint...")
    # Checkpoint is automatically saved
except Exception as e:
    print(f"Training failed: {e}")
    # Resume from last checkpoint if available
```

---

!!! tip "Core API Tips"
    - Start with high-level functions and move to lower-level APIs as needed
    - Use configuration presets as starting points
    - Always handle exceptions appropriately
    - Take advantage of automatic checkpointing for long training runs