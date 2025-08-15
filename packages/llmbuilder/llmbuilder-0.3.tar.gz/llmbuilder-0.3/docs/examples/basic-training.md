# Basic Training Example

This comprehensive example demonstrates how to train a language model from scratch using LLMBuilder. We'll cover data preparation, tokenizer training, model training, and text generation.

## 🎯 Overview

In this example, we'll:

1. **Prepare training data** from various document formats
2. **Train a tokenizer** on our text corpus
3. **Configure and train** a language model
4. **Generate text** with the trained model
5. **Evaluate performance** and iterate

## 📁 Project Structure

```
basic_training_example/
├── data/
│   ├── raw/                    # Raw documents (PDF, DOCX, TXT)
│   └── processed/              # Cleaned text files
├── config/
│   └── training_config.json    # Training configuration
├── output/
│   ├── tokenizer/              # Trained tokenizer
│   ├── model/                  # Trained model
│   └── logs/                   # Training logs
└── train_model.py              # Main training script
```

## 🚀 Complete Training Script

```python
#!/usr/bin/env python3
"""
Basic Training Example for LLMBuilder

This script demonstrates a complete training pipeline:
1. Data loading and preprocessing
2. Tokenizer training
3. Model training
4. Text generation and evaluation
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main training pipeline."""
    
    # Configuration
    project_dir = Path(__file__).parent
    raw_data_dir = project_dir / "data" / "raw"
    processed_data_dir = project_dir / "data" / "processed"
    output_dir = project_dir / "output"
    
    # Create directories
    for dir_path in [processed_data_dir, output_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("🚀 Starting LLMBuilder training pipeline")
    
    # Step 1: Data Preparation
    logger.info("📁 Step 1: Preparing training data")
    training_data_path = prepare_training_data(raw_data_dir, processed_data_dir)
    
    # Step 2: Tokenizer Training
    logger.info("🔤 Step 2: Training tokenizer")
    tokenizer_dir = train_tokenizer(training_data_path, output_dir)
    
    # Step 3: Model Training
    logger.info("🧠 Step 3: Training language model")
    model_path = train_language_model(training_data_path, tokenizer_dir, output_dir)
    
    # Step 4: Text Generation
    logger.info("🎯 Step 4: Testing text generation")
    test_text_generation(model_path, tokenizer_dir)
    
    # Step 5: Evaluation
    logger.info("📊 Step 5: Evaluating model performance")
    evaluate_model(model_path, tokenizer_dir, training_data_path)
    
    logger.info("✅ Training pipeline completed successfully!")

def prepare_training_data(raw_data_dir, processed_data_dir):
    """Load and preprocess training data from various formats."""
    from llmbuilder.data import DataLoader, TextCleaner
    
    # Initialize data loader
    loader = DataLoader(
        min_length=50,              # Filter short texts
        clean_text=True,            # Apply basic cleaning
        remove_duplicates=True      # Remove duplicate content
    )
    
    # Load all supported files
    texts = []
    supported_extensions = ['.txt', '.pdf', '.docx', '.md', '.html']
    
    logger.info(f"Loading documents from {raw_data_dir}")
    
    if raw_data_dir.exists():
        for file_path in raw_data_dir.rglob("*"):
            if file_path.suffix.lower() in supported_extensions:
                try:
                    text = loader.load_file(file_path)
                    if text:
                        texts.append(text)
                        logger.info(f"  ✅ Loaded {file_path.name}: {len(text):,} characters")
                except Exception as e:
                    logger.warning(f"  ❌ Failed to load {file_path.name}: {e}")
    
    # If no files found, create sample data
    if not texts:
        logger.info("No data files found, creating sample training data")
        sample_text = create_sample_data()
        texts = [sample_text]
    
    # Combine and clean texts
    combined_text = "\n\n".join(texts)
    
    # Advanced text cleaning
    cleaner = TextCleaner(
        normalize_whitespace=True,
        remove_urls=True,
        remove_emails=True,
        min_sentence_length=20,
        remove_duplicates=True,
        language_filter="en"        # Keep only English text
    )
    
    cleaned_text = cleaner.clean(combined_text)
    stats = cleaner.get_stats()
    
    logger.info(f"Text cleaning results:")
    logger.info(f"  Original: {stats.original_length:,} characters")
    logger.info(f"  Cleaned: {stats.cleaned_length:,} characters")
    logger.info(f"  Removed: {stats.removal_percentage:.1f}%")
    
    # Save processed data
    training_data_path = processed_data_dir / "training_data.txt"
    with open(training_data_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    logger.info(f"Training data saved to {training_data_path}")
    return training_data_path

def train_tokenizer(training_data_path, output_dir):
    """Train a BPE tokenizer on the training data."""
    from llmbuilder.tokenizer import TokenizerTrainer
    from llmbuilder.config import TokenizerConfig
    
    tokenizer_dir = output_dir / "tokenizer"
    tokenizer_dir.mkdir(exist_ok=True)
    
    # Configure tokenizer
    config = TokenizerConfig(
        vocab_size=16000,           # Vocabulary size
        model_type="bpe",           # Byte-Pair Encoding
        character_coverage=1.0,     # Cover all characters
        max_sentence_length=4096,   # Maximum sentence length
        special_tokens=[            # Special tokens
            "<pad>", "<unk>", "<s>", "</s>", "<mask>"
        ]
    )
    
    # Train tokenizer
    trainer = TokenizerTrainer(config=config)
    results = trainer.train(
        input_file=str(training_data_path),
        output_dir=str(tokenizer_dir),
        model_prefix="tokenizer"
    )
    
    logger.info(f"Tokenizer training completed:")
    logger.info(f"  Model: {results['model_file']}")
    logger.info(f"  Vocab: {results['vocab_file']}")
    logger.info(f"  Training time: {results['training_time']:.1f}s")
    
    # Test tokenizer
    from llmbuilder.tokenizer import Tokenizer
    tokenizer = Tokenizer.from_pretrained(str(tokenizer_dir))
    
    test_text = "Hello, world! This is a test of the tokenizer."
    tokens = tokenizer.encode(test_text)
    decoded = tokenizer.decode(tokens)
    
    logger.info(f"Tokenizer test:")
    logger.info(f"  Original: {test_text}")
    logger.info(f"  Tokens: {tokens}")
    logger.info(f"  Decoded: {decoded}")
    logger.info(f"  Perfect reconstruction: {test_text == decoded}")
    
    return tokenizer_dir

def train_language_model(training_data_path, tokenizer_dir, output_dir):
    """Train the language model."""
    import llmbuilder as lb
    from llmbuilder.config import Config, ModelConfig, TrainingConfig
    from llmbuilder.data import TextDataset
    
    model_dir = output_dir / "model"
    model_dir.mkdir(exist_ok=True)
    
    # Create configuration
    config = Config(
        model=ModelConfig(
            vocab_size=16000,           # Must match tokenizer
            num_layers=8,               # Number of transformer layers
            num_heads=8,                # Number of attention heads
            embedding_dim=512,          # Embedding dimension
            max_seq_length=1024,        # Maximum sequence length
            dropout=0.1,                # Dropout rate
            model_type="gpt"            # Model architecture
        ),
        training=TrainingConfig(
            batch_size=8,               # Batch size (adjust for your hardware)
            num_epochs=10,              # Number of training epochs
            learning_rate=3e-4,         # Learning rate
            warmup_steps=1000,          # Warmup steps
            weight_decay=0.01,          # Weight decay
            max_grad_norm=1.0,          # Gradient clipping
            save_every=1000,            # Save checkpoint every N steps
            eval_every=500,             # Evaluate every N steps
            log_every=100               # Log every N steps
        )
    )
    
    # Save configuration
    config_path = model_dir / "config.json"
    config.save(str(config_path))
    logger.info(f"Configuration saved to {config_path}")
    
    # Build model
    model = lb.build_model(config.model)
    num_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model built with {num_params:,} parameters")
    
    # Prepare dataset
    dataset = TextDataset(
        data_path=str(training_data_path),
        block_size=config.model.max_seq_length,
        stride=config.model.max_seq_length // 2,  # 50% overlap
        cache_in_memory=True
    )
    
    logger.info(f"Dataset prepared: {len(dataset):,} samples")
    
    # Train model
    results = lb.train_model(
        model=model,
        dataset=dataset,
        config=config.training,
        checkpoint_dir=str(model_dir)
    )
    
    logger.info(f"Training completed:")
    logger.info(f"  Final loss: {results.final_loss:.4f}")
    logger.info(f"  Training time: {results.training_time}")
    logger.info(f"  Model saved to: {results.model_path}")
    
    return results.model_path

def test_text_generation(model_path, tokenizer_dir):
    """Test text generation with the trained model."""
    import llmbuilder as lb
    
    test_prompts = [
        "Artificial intelligence is",
        "The future of technology",
        "Machine learning can help us",
        "In the world of programming",
        "The benefits of renewable energy"
    ]
    
    logger.info("Testing text generation:")
    
    for prompt in test_prompts:
        try:
            generated_text = lb.generate_text(
                model_path=model_path,
                tokenizer_path=str(tokenizer_dir),
                prompt=prompt,
                max_new_tokens=50,
                temperature=0.8,
                top_k=50,
                top_p=0.9
            )
            
            logger.info(f"  Prompt: {prompt}")
            logger.info(f"  Generated: {generated_text}")
            logger.info("")
            
        except Exception as e:
            logger.error(f"  Generation failed for '{prompt}': {e}")

def evaluate_model(model_path, tokenizer_dir, training_data_path):
    """Evaluate model performance."""
    from llmbuilder.model import load_model
    from llmbuilder.tokenizer import Tokenizer
    from llmbuilder.data import TextDataset
    import torch
    
    # Load model and tokenizer
    model = load_model(model_path)
    tokenizer = Tokenizer.from_pretrained(str(tokenizer_dir))
    
    # Create evaluation dataset (small sample)
    eval_dataset = TextDataset(
        data_path=str(training_data_path),
        block_size=512,
        stride=256,
        max_samples=100  # Small sample for quick evaluation
    )
    
    # Calculate perplexity
    model.eval()
    total_loss = 0
    total_tokens = 0
    
    with torch.no_grad():
        for i, batch in enumerate(eval_dataset):
            if i >= 10:  # Limit evaluation for speed
                break
                
            input_ids = torch.tensor([batch], dtype=torch.long)
            
            # Forward pass
            outputs = model(input_ids[:, :-1])
            logits = outputs.logits if hasattr(outputs, 'logits') else outputs
            
            # Calculate loss
            targets = input_ids[:, 1:]
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=tokenizer.pad_token_id
            )
            
            total_loss += loss.item()
            total_tokens += targets.numel()
    
    avg_loss = total_loss / min(10, len(eval_dataset))
    perplexity = torch.exp(torch.tensor(avg_loss)).item()
    
    logger.info(f"Model evaluation:")
    logger.info(f"  Average loss: {avg_loss:.4f}")
    logger.info(f"  Perplexity: {perplexity:.2f}")
    logger.info(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")

def create_sample_data():
    """Create sample training data if no files are found."""
    return """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.

    Machine learning (ML) is a type of artificial intelligence that allows software applications to become more accurate at predicting outcomes without being explicitly programmed to do so. Machine learning algorithms use historical data as input to predict new output values.

    Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised.

    Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.

    Computer vision is an interdisciplinary scientific field that deals with how computers can gain high-level understanding from digital images or videos. From the perspective of engineering, it seeks to understand and automate tasks that the human visual system can do.

    The future of artificial intelligence holds great promise for solving complex problems in healthcare, transportation, education, and many other fields. As AI systems become more sophisticated, they will continue to transform how we work, learn, and interact with technology.
    """

if __name__ == "__main__":
    main()
```

## 📊 Expected Output

When you run this script, you should see output similar to:

```
INFO:__main__:🚀 Starting LLMBuilder training pipeline
INFO:__main__:📁 Step 1: Preparing training data
INFO:__main__:No data files found, creating sample training data
INFO:__main__:Text cleaning results:
INFO:__main__:  Original: 1,234 characters
INFO:__main__:  Cleaned: 1,180 characters
INFO:__main__:  Removed: 4.4%
INFO:__main__:Training data saved to basic_training_example/data/processed/training_data.txt

INFO:__main__:🔤 Step 2: Training tokenizer
INFO:__main__:Tokenizer training completed:
INFO:__main__:  Model: basic_training_example/output/tokenizer/tokenizer.model
INFO:__main__:  Vocab: basic_training_example/output/tokenizer/tokenizer.vocab
INFO:__main__:  Training time: 5.2s
INFO:__main__:Tokenizer test:
INFO:__main__:  Original: Hello, world! This is a test of the tokenizer.
INFO:__main__:  Tokens: [15496, 995, 0, 1188, 374, 264, 1296, 315, 279, 4037, 3213, 13]
INFO:__main__:  Decoded: Hello, world! This is a test of the tokenizer.
INFO:__main__:  Perfect reconstruction: True

INFO:__main__:🧠 Step 3: Training language model
INFO:__main__:Configuration saved to basic_training_example/output/model/config.json
INFO:__main__:Model built with 42,123,456 parameters
INFO:__main__:Dataset prepared: 156 samples
INFO:__main__:Training completed:
INFO:__main__:  Final loss: 2.45
INFO:__main__:  Training time: 0:15:23
INFO:__main__:  Model saved to: basic_training_example/output/model/model.pt

INFO:__main__:🎯 Step 4: Testing text generation
INFO:__main__:Testing text generation:
INFO:__main__:  Prompt: Artificial intelligence is
INFO:__main__:  Generated: Artificial intelligence is a rapidly evolving field that encompasses machine learning, deep learning, and neural networks...

INFO:__main__:📊 Step 5: Evaluating model performance
INFO:__main__:Model evaluation:
INFO:__main__:  Average loss: 2.52
INFO:__main__:  Perplexity: 12.4
INFO:__main__:  Model parameters: 42,123,456

INFO:__main__:✅ Training pipeline completed successfully!
```

## 🎯 Customization Options

### 1. Adjust Model Size

```python
# Smaller model (faster training, less memory)
model_config = ModelConfig(
    vocab_size=8000,
    num_layers=4,
    num_heads=4,
    embedding_dim=256,
    max_seq_length=512
)

# Larger model (better quality, more resources)
model_config = ModelConfig(
    vocab_size=32000,
    num_layers=16,
    num_heads=16,
    embedding_dim=1024,
    max_seq_length=2048
)
```

### 2. Modify Training Parameters

```python
# Fast training (for testing)
training_config = TrainingConfig(
    batch_size=16,
    num_epochs=3,
    learning_rate=1e-3,
    save_every=100
)

# High-quality training (for production)
training_config = TrainingConfig(
    batch_size=8,
    num_epochs=50,
    learning_rate=1e-4,
    warmup_steps=2000,
    weight_decay=0.01
)
```

### 3. Different Data Sources

```python
# Load from specific file types
loader = DataLoader(
    supported_formats=['.txt', '.md'],  # Only text and markdown
    min_length=100,                     # Longer minimum length
    max_length=10000,                   # Maximum length limit
    clean_text=True
)

# Custom text cleaning
cleaner = TextCleaner(
    normalize_whitespace=True,
    remove_urls=True,
    remove_emails=True,
    remove_phone_numbers=True,
    min_sentence_length=30,
    language_filter="en",
    custom_filters=[
        lambda text: text.replace("specific_pattern", "replacement")
    ]
)
```

## 🚨 Troubleshooting

### Common Issues

#### Out of Memory

```python
# Reduce batch size
training_config.batch_size = 4

# Enable gradient checkpointing
model_config.gradient_checkpointing = True

# Use gradient accumulation
training_config.gradient_accumulation_steps = 4
```

#### Poor Generation Quality

```python
# Train for more epochs
training_config.num_epochs = 20

# Use more training data
# Add more text files to data/raw/

# Adjust generation parameters
generated_text = lb.generate_text(
    model_path=model_path,
    tokenizer_path=str(tokenizer_dir),
    prompt=prompt,
    max_new_tokens=100,
    temperature=0.7,        # Lower temperature
    top_k=40,              # More focused sampling
    repetition_penalty=1.1  # Reduce repetition
)
```

#### Slow Training

```python
# Use GPU if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

# Reduce sequence length
model_config.max_seq_length = 512

# Increase batch size (if memory allows)
training_config.batch_size = 16
```

## 📚 Next Steps

After running this basic example:

1. **Experiment with different model sizes** and training parameters
2. **Add your own training data** to the `data/raw/` directory
3. **Try fine-tuning** the trained model on specific tasks
4. **Export the model** for deployment using the export functionality
5. **Implement evaluation metrics** specific to your use case

---

!!! tip "Training Tips"
    - Start with small models and datasets to verify everything works
    - Monitor training loss to ensure the model is learning
    - Save checkpoints frequently during long training runs
    - Test generation quality throughout training
    - Keep track of what configurations work best for your data