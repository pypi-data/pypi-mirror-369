# Your First Model

This comprehensive tutorial will guide you through training your first language model with LLMBuilder, from data preparation to text generation. By the end, you'll have a working model and understand the entire process.

## 🎯 What We'll Build

We'll create a small GPT-style language model that can:
- Generate coherent text based on prompts
- Complete sentences and paragraphs
- Demonstrate understanding of the training data

**Estimated time**: 30-60 minutes  
**Requirements**: 4GB RAM, Python 3.8+

## 📋 Prerequisites

Make sure you have LLMBuilder installed:

```bash
pip install llmbuilder
```

Verify the installation:

```bash
llmbuilder --version
```

## 📚 Step 1: Prepare Training Data

### Option A: Use Sample Data

Create a sample dataset for testing:

```python
# create_sample_data.py
sample_text = """
Artificial intelligence is a rapidly evolving field that encompasses machine learning, deep learning, and neural networks. Machine learning algorithms enable computers to learn patterns from data without explicit programming. Deep learning, a subset of machine learning, uses multi-layered neural networks to process complex information.

Natural language processing is a branch of AI that focuses on the interaction between computers and human language. It enables machines to understand, interpret, and generate human language in a valuable way. Applications include chatbots, translation services, and text analysis.

Computer vision is another important area of AI that enables machines to interpret and understand visual information from the world. It combines techniques from machine learning, image processing, and pattern recognition to analyze and understand images and videos.

The future of artificial intelligence holds great promise for solving complex problems in healthcare, transportation, education, and many other fields. As AI systems become more sophisticated, they will continue to transform how we work, learn, and interact with technology.
"""

with open("training_data.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)

print("Sample data created: training_data.txt")
```

Run the script:

```bash
python create_sample_data.py
```

### Option B: Use Your Own Data

If you have your own text data:

```bash
# Process various document formats
llmbuilder data load \
  --input ./documents \
  --output training_data.txt \
  --format all \
  --clean \
  --min-length 100
```

This will:
- Load PDF, DOCX, TXT files from `./documents`
- Clean and normalize the text
- Filter out short passages
- Save everything to `training_data.txt`

## 🔧 Step 2: Configure Your Model

Create a configuration file for your model:

```bash
llmbuilder config create \
  --preset cpu_small \
  --output model_config.json \
  --interactive
```

This will create a configuration optimized for CPU training. The interactive mode will ask you questions like:

```
⚙️ LLMBuilder Configuration Creator
Choose a preset: cpu_small
Output file path: model_config.json
🧠 Model layers: 6
📏 Embedding dimension: 384
🔤 Vocabulary size: 8000
📦 Batch size: 8
📈 Learning rate: 0.0003
```

### Understanding the Configuration

Let's examine what was created:

```bash
cat model_config.json
```

```json
{
  "model": {
    "vocab_size": 8000,
    "num_layers": 6,
    "num_heads": 6,
    "embedding_dim": 384,
    "max_seq_length": 512,
    "dropout": 0.1
  },
  "training": {
    "batch_size": 8,
    "num_epochs": 10,
    "learning_rate": 0.0003,
    "warmup_steps": 100,
    "save_every": 1000,
    "eval_every": 500
  },
  "system": {
    "device": "cpu"
  }
}
```

## 🔤 Step 3: Train the Tokenizer

Before training the model, we need to create a tokenizer:

```bash
llmbuilder data tokenizer \
  --input training_data.txt \
  --output ./tokenizer \
  --vocab-size 8000 \
  --model-type bpe
```

This creates a Byte-Pair Encoding (BPE) tokenizer with 8,000 vocabulary items. You'll see output like:

```
🔤 Training BPE tokenizer with vocab size 8000...
📊 Processing text data...
⚙️ Training tokenizer model...
✅ Tokenizer training completed!
  Model: ./tokenizer/tokenizer.model
  Vocab: ./tokenizer/tokenizer.vocab
  Training time: 12.3s
```

### Test Your Tokenizer

Let's verify the tokenizer works:

```python
# test_tokenizer.py
from llmbuilder.tokenizer import Tokenizer

# Load the tokenizer
tokenizer = Tokenizer.from_pretrained("./tokenizer")

# Test encoding and decoding
text = "Artificial intelligence is amazing!"
tokens = tokenizer.encode(text)
decoded = tokenizer.decode(tokens)

print(f"Original: {text}")
print(f"Tokens: {tokens}")
print(f"Decoded: {decoded}")
print(f"Vocabulary size: {len(tokenizer)}")
```

## 🧠 Step 4: Train the Model

Now for the main event - training your language model:

```bash
llmbuilder train model \
  --config model_config.json \
  --data training_data.txt \
  --tokenizer ./tokenizer \
  --output ./my_first_model \
  --verbose
```

### What Happens During Training

You'll see output like this:

```
🚀 Starting model training...
📊 Dataset: 1,234 tokens, 156 samples
🧠 Model: 2.1M parameters
📈 Training configuration:
  • Epochs: 10
  • Batch size: 8
  • Learning rate: 0.0003
  • Device: cpu

Epoch 1/10:
  Step 10/20: loss=4.23, lr=0.00015, time=2.1s
  Step 20/20: loss=3.87, lr=0.00030, time=4.2s
  Validation: loss=3.92, perplexity=50.4

Epoch 2/10:
  Step 10/20: loss=3.45, lr=0.00030, time=2.0s
  Step 20/20: loss=3.21, lr=0.00030, time=4.1s
  Validation: loss=3.28, perplexity=26.7

...

✅ Training completed successfully!
📊 Final Results:
  • Training Loss: 2.45
  • Validation Loss: 2.52
  • Training Time: 8m 34s
  • Model saved to: ./my_first_model/model.pt
```

### Understanding Training Metrics

- **Loss**: How well the model predicts the next token (lower is better)
- **Perplexity**: Model confidence (lower means more confident)
- **Learning Rate**: How fast the model learns (adjusted automatically)

## 🎯 Step 5: Generate Text

Time to test your model! Let's generate some text:

```bash
llmbuilder generate text \
  --model ./my_first_model/model.pt \
  --tokenizer ./tokenizer \
  --prompt "Artificial intelligence" \
  --max-tokens 100 \
  --temperature 0.8
```

You should see output like:

```
💭 Prompt: Artificial intelligence
🤔 Generating...

🎯 Generated Text:
──────────────────────────────────────────────────
Artificial intelligence is a rapidly evolving field that encompasses machine learning and deep learning technologies. These systems can process vast amounts of data to identify patterns and make predictions. Natural language processing enables computers to understand and generate human language, while computer vision allows machines to interpret visual information.
──────────────────────────────────────────────────
📊 Settings: temp=0.8, max_tokens=100
```

### Interactive Generation

For a more interactive experience:

```bash
llmbuilder generate text \
  --model ./my_first_model/model.pt \
  --tokenizer ./tokenizer \
  --interactive
```

This starts an interactive session where you can try different prompts:

```
🎮 Interactive Text Generation
💡 Type your prompts and watch the AI respond!

> Prompt: Machine learning is
Generated: Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed...

> Prompt: The future of AI
Generated: The future of AI holds tremendous potential for transforming industries and solving complex global challenges...

> Prompt: /quit
Goodbye! 👋
```

## 📊 Step 6: Evaluate Your Model

Let's assess how well your model performed:

```bash
llmbuilder model evaluate \
  ./my_first_model/model.pt \
  --dataset training_data.txt \
  --batch-size 16
```

This will output metrics like:

```
📊 Model Evaluation Results:
  • Perplexity: 15.2 (lower is better)
  • Loss: 2.72
  • Tokens per second: 1,234
  • Memory usage: 1.2GB
  • Model size: 8.4MB
```

### Model Information

Get detailed information about your model:

```bash
llmbuilder model info ./my_first_model/model.pt
```

```
✅ Model loaded successfully
  Total parameters: 2,123,456
  Trainable parameters: 2,123,456
  Architecture: 6 layers, 6 heads
  Embedding dim: 384
  Vocab size: 8,000
  Max sequence length: 512
```

## 🚀 Step 7: Experiment and Improve

Now that you have a working model, try these experiments:

### Experiment 1: Different Generation Parameters

```python
# experiment_generation.py
import llmbuilder as lb

model_path = "./my_first_model/model.pt"
tokenizer_path = "./tokenizer"
prompt = "The future of technology"

# Conservative generation (more predictable)
conservative = lb.generate_text(
    model_path, tokenizer_path, prompt,
    temperature=0.3, top_k=10, max_new_tokens=50
)

# Creative generation (more diverse)
creative = lb.generate_text(
    model_path, tokenizer_path, prompt,
    temperature=1.2, top_k=100, max_new_tokens=50
)

print("Conservative:", conservative)
print("Creative:", creative)
```

### Experiment 2: Fine-tuning

If you have domain-specific data, try fine-tuning:

```bash
# Create domain-specific data
echo "Your domain-specific text here..." > domain_data.txt

# Fine-tune the model
llmbuilder finetune model \
  --model ./my_first_model/model.pt \
  --dataset domain_data.txt \
  --output ./fine_tuned_model \
  --epochs 5 \
  --lr 1e-5
```

### Experiment 3: Export for Production

Export your model for different deployment scenarios:

```bash
# Export to GGUF for llama.cpp
llmbuilder export gguf \
  ./my_first_model/model.pt \
  --output my_model.gguf \
  --quantization q4_0

# Export to ONNX for mobile/edge
llmbuilder export onnx \
  ./my_first_model/model.pt \
  --output my_model.onnx
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Out of Memory Error

```bash
# Reduce batch size
llmbuilder train model --config model_config.json --batch-size 2

# Or use gradient accumulation
llmbuilder train model --config model_config.json --gradient-accumulation-steps 4
```

#### 2. Poor Generation Quality

```bash
# Train for more epochs
llmbuilder train model --config model_config.json --epochs 20

# Use more training data
# Add more text files to your dataset

# Adjust model size
llmbuilder config create --preset gpu_medium --output larger_config.json
```

#### 3. Training Too Slow

```bash
# Use GPU if available
llmbuilder train model --config model_config.json --device cuda

# Reduce sequence length
# Edit model_config.json: "max_seq_length": 256
```

## 📈 Understanding Your Results

### What Makes a Good Model?

- **Perplexity < 20**: Good for small datasets
- **Coherent text**: Generated text should make sense
- **Diverse outputs**: Different prompts should produce varied responses
- **Fast inference**: Generation should be reasonably quick

### Improving Your Model

1. **More data**: The most important factor
2. **Longer training**: More epochs often help
3. **Better data quality**: Clean, relevant text
4. **Hyperparameter tuning**: Adjust learning rate, batch size
5. **Model architecture**: Try different sizes

## 🎉 Congratulations!

You've successfully:

✅ Prepared training data  
✅ Configured a model  
✅ Trained a tokenizer  
✅ Trained a language model  
✅ Generated text  
✅ Evaluated performance  

## 🚀 Next Steps

Now that you have the basics down, explore:

- **[Advanced Training](../user-guide/training.md)** - Learn advanced techniques
- **[Fine-tuning Guide](../user-guide/fine-tuning.md)** - Adapt models to specific domains
- **[Model Export](../user-guide/export.md)** - Deploy your models
- **[CLI Reference](../cli/overview.md)** - Complete CLI documentation

---

!!! tip "Keep Experimenting!"
    The model you just trained is small and trained on limited data, but you've learned the complete workflow. Try training on larger datasets, experimenting with different architectures, and fine-tuning for specific tasks. The possibilities are endless!