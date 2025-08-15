# Quick Start

Get up and running with LLMBuilder in just 5 minutes! This guide will walk you through training your first language model.

## 🚀 5-Minute Setup

### Step 1: Install LLMBuilder

```bash
pip install llmbuilder
```

### Step 2: Prepare Your Data

Create a simple text file with some training data:

```bash
# Create a sample data file
echo "Artificial intelligence is transforming the world. Machine learning enables computers to learn from data. Deep learning uses neural networks to solve complex problems." > sample_data.txt
```

### Step 3: Train Your First Model

Use the interactive CLI to train a model:

```bash
llmbuilder welcome
```

Or use the direct command:

```bash
# Train a small model (perfect for testing)
llmbuilder train model \
  --data sample_data.txt \
  --tokenizer ./tokenizer \
  --output ./my_first_model \
  --epochs 5 \
  --batch-size 2
```

### Step 4: Generate Text

```bash
# Generate text with your trained model
llmbuilder generate text \
  --model ./my_first_model/model.pt \
  --tokenizer ./tokenizer \
  --prompt "Artificial intelligence" \
  --max-tokens 50
```

🎉 **Congratulations!** You've just trained and used your first language model with LLMBuilder!

## 🐍 Python API Quick Start

Prefer Python code? Here's the same workflow using the Python API:

```python
import llmbuilder as lb

# 1. Load configuration
cfg = lb.load_config(preset="cpu_small")

# 2. Build model
model = lb.build_model(cfg.model)

# 3. Prepare data
from llmbuilder.data import TextDataset
dataset = TextDataset("sample_data.txt", block_size=cfg.model.max_seq_length)

# 4. Train model
results = lb.train_model(model, dataset, cfg.training)

# 5. Generate text
text = lb.generate_text(
    model_path="./checkpoints/model.pt",
    tokenizer_path="./tokenizers",
    prompt="Artificial intelligence",
    max_new_tokens=50
)
print(text)
```

## 📊 Understanding the Output

When training completes, you'll see output like:

```
✅ Training completed successfully!
📊 Final Results:
  • Training Loss: 2.45
  • Validation Loss: 2.52
  • Training Time: 3m 24s
  • Model Parameters: 2.1M
  • Model Size: 8.4MB

💾 Outputs saved to:
  • Model: ./my_first_model/model.pt
  • Tokenizer: ./tokenizer/
  • Logs: ./my_first_model/training.log
```

## 🎯 What Just Happened?

Let's break down what LLMBuilder did:

1. **Data Processing**: Loaded and cleaned your text data
2. **Tokenization**: Created a vocabulary and tokenized the text
3. **Model Creation**: Built a GPT-style transformer model
4. **Training**: Trained the model to predict the next token
5. **Saving**: Saved the model and tokenizer for later use

## 🔧 Customization Options

### Different Model Sizes

```bash
# Tiny model (fastest, least memory)
llmbuilder train model --config-preset tiny --data data.txt --output model/

# Small model (balanced)
llmbuilder train model --config-preset cpu_small --data data.txt --output model/

# Medium model (better quality, needs more resources)
llmbuilder train model --config-preset gpu_medium --data data.txt --output model/
```

### Different Data Formats

LLMBuilder supports multiple input formats:

```bash
# Process PDF files
llmbuilder data load --input documents/ --output clean_text.txt --format pdf

# Process DOCX files
llmbuilder data load --input documents/ --output clean_text.txt --format docx

# Process all supported formats
llmbuilder data load --input documents/ --output clean_text.txt --format all
```

### Interactive Mode

For a guided experience:

```bash
# Interactive training setup
llmbuilder train model --interactive

# Interactive text generation
llmbuilder generate text --setup
```

## 📈 Next Steps

Now that you have a working model, here are some things to try:

### 1. Improve Your Model

```bash
# Train for more epochs
llmbuilder train model --data data.txt --output model/ --epochs 20

# Use a larger model
llmbuilder train model --data data.txt --output model/ --layers 12 --dim 768

# Add more training data
llmbuilder data load --input more_documents/ --output bigger_dataset.txt
```

### 2. Fine-tune on Specific Data

```bash
# Fine-tune your model on domain-specific data
llmbuilder finetune model \
  --model ./my_first_model/model.pt \
  --dataset domain_specific_data.txt \
  --output ./fine_tuned_model
```

### 3. Export for Production

```bash
# Export to GGUF format for llama.cpp
llmbuilder export gguf ./my_first_model/model.pt --output model.gguf

# Export to ONNX for mobile/edge deployment
llmbuilder export onnx ./my_first_model/model.pt --output model.onnx
```

### 4. Advanced Generation

```python
import llmbuilder as lb

# Interactive chat-like generation
lb.interactive_cli(
    model_path="./my_first_model/model.pt",
    tokenizer_path="./tokenizer",
    temperature=0.8,
    top_k=50
)
```

## 🛠️ Configuration Presets

LLMBuilder comes with several built-in presets:

| Preset | Use Case | Memory | Training Time |
|--------|----------|---------|---------------|
| `tiny` | Testing, debugging | ~1GB | Minutes |
| `cpu_small` | CPU training, learning | ~2GB | Hours |
| `gpu_medium` | Single GPU training | ~8GB | Hours |
| `gpu_large` | High-end GPU training | ~16GB+ | Days |

## 🔍 Monitoring Training

### Real-time Monitoring

```bash
# Monitor training progress
tail -f ./my_first_model/training.log

# Or use the built-in progress display
llmbuilder train model --data data.txt --output model/ --verbose
```

### Training Metrics

LLMBuilder tracks important metrics:

- **Loss**: How well the model is learning
- **Perplexity**: Model confidence (lower is better)
- **Learning Rate**: Training speed
- **Memory Usage**: Resource consumption

## 🚨 Common Issues & Solutions

### Out of Memory

```bash
# Reduce batch size
llmbuilder train model --data data.txt --output model/ --batch-size 1

# Use CPU-only mode
llmbuilder train model --data data.txt --output model/ --device cpu
```

### Slow Training

```bash
# Use GPU if available
llmbuilder train model --data data.txt --output model/ --device cuda

# Reduce model size
llmbuilder train model --data data.txt --output model/ --layers 4 --dim 256
```

### Poor Generation Quality

```bash
# Train for more epochs
llmbuilder train model --data data.txt --output model/ --epochs 50

# Use more training data
# Add more text files to your dataset

# Adjust generation parameters
llmbuilder generate text --model model.pt --tokenizer tokenizer/ \
  --prompt "Your prompt" --temperature 0.7 --top-k 40
```

## 📚 Learn More

Ready to dive deeper? Check out these resources:

- **[First Model Tutorial](first-model.md)** - Detailed step-by-step guide
- **[Configuration Guide](../user-guide/configuration.md)** - Customize your setup
- **[Training Guide](../user-guide/training.md)** - Advanced training techniques
- **[Model Export](../user-guide/export.md)** - Deploy your models
- **[CLI Reference](../cli/overview.md)** - Complete CLI documentation

---

!!! success "You're Ready!"
    You now have a working LLMBuilder setup! The model you just trained might be small, but you've learned the complete workflow. Try experimenting with different data, model sizes, and generation parameters to see what works best for your use case.