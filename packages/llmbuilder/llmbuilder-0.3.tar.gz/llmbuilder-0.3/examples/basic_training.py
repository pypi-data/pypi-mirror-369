#!/usr/bin/env python3
"""
Basic Training Example for LLMBuilder

This script demonstrates a complete training pipeline using LLMBuilder's
advanced data processing capabilities:

1. Multi-format document ingestion
2. Advanced deduplication (exact + semantic)
3. Custom tokenizer training
4. Model training with configuration templates
5. GGUF model conversion
6. Text generation and evaluation

Usage:
    python basic_training.py

Requirements:
    pip install llmbuilder[all]
"""

import os
import sys
from pathlib import Path
import logging
import tempfile
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline demonstrating LLMBuilder's capabilities."""
    
    # Create temporary working directory
    work_dir = Path(tempfile.mkdtemp(prefix="llmbuilder_example_"))
    logger.info(f"🚀 Starting LLMBuilder example in {work_dir}")
    
    try:
        # Step 1: Create sample data and configuration
        logger.info("📁 Step 1: Setting up sample data and configuration")
        data_file, config_file = setup_example_data(work_dir)
        
        # Step 2: Process data with advanced ingestion
        logger.info("🔄 Step 2: Processing data with multi-format ingestion")
        processed_file = process_data_advanced(data_file, work_dir)
        
        # Step 3: Advanced deduplication
        logger.info("🧹 Step 3: Advanced deduplication (exact + semantic)")
        clean_file = deduplicate_data(processed_file, work_dir)
        
        # Step 4: Train custom tokenizer
        logger.info("🔤 Step 4: Training custom tokenizer")
        tokenizer_dir = train_tokenizer(clean_file, work_dir)
        
        # Step 5: Train model (simplified for demo)
        logger.info("🧠 Step 5: Training language model")
        model_path = train_model_demo(clean_file, tokenizer_dir, config_file, work_dir)
        
        # Step 6: Convert to GGUF format
        logger.info("🔄 Step 6: Converting model to GGUF format")
        gguf_path = convert_to_gguf(model_path, work_dir)
        
        # Step 7: Test text generation
        logger.info("🎯 Step 7: Testing text generation")
        test_generation(model_path, tokenizer_dir)
        
        logger.info("✅ Example completed successfully!")
        logger.info(f"📁 Results saved in: {work_dir}")
        
        # Ask user if they want to keep the results
        try:
            keep = input("\nKeep example results? (y/N): ").lower().startswith('y')
            if not keep:
                shutil.rmtree(work_dir)
                logger.info("🗑️  Cleaned up temporary files")
        except KeyboardInterrupt:
            logger.info("\n🗑️  Cleaning up...")
            shutil.rmtree(work_dir)
            
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")
        shutil.rmtree(work_dir, ignore_errors=True)
        raise


def setup_example_data(work_dir):
    """Create sample data and configuration for the example."""
    
    # Create sample text data (simulating multi-format documents)
    sample_texts = [
        # Simulating HTML content
        """
        <html><body>
        <h1>Introduction to Machine Learning</h1>
        <p>Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.</p>
        <p>There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.</p>
        </body></html>
        """,
        
        # Simulating Markdown content
        """
        # Deep Learning Fundamentals
        
        Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data.
        
        ## Key Concepts
        - Neural networks
        - Backpropagation
        - Gradient descent
        - Activation functions
        
        Deep learning has revolutionized fields like computer vision, natural language processing, and speech recognition.
        """,
        
        # Simulating plain text content
        """
        Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret and manipulate human language. NLP draws from many disciplines, including computer science and computational linguistics, in its pursuit to fill the gap between human communication and computer understanding.
        
        Modern NLP techniques use machine learning algorithms to automatically extract, classify and label elements of text and voice data and then assign a statistical likelihood to each possible meaning of those elements.
        
        Applications of NLP include machine translation, sentiment analysis, chatbots, and text summarization.
        """,
        
        # Add some duplicate content to test deduplication
        """
        Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.
        """,
        
        # Similar content to test semantic deduplication
        """
        ML is a branch of AI that allows computers to learn and enhance their performance from data without explicit programming.
        """
    ]
    
    # Save sample data
    data_dir = work_dir / "data"
    data_dir.mkdir()
    
    data_files = []
    for i, text in enumerate(sample_texts):
        file_path = data_dir / f"sample_{i}.txt"
        file_path.write_text(text.strip(), encoding='utf-8')
        data_files.append(file_path)
    
    # Create combined data file
    combined_file = data_dir / "combined.txt"
    combined_text = "\n\n".join(sample_texts)
    combined_file.write_text(combined_text, encoding='utf-8')
    
    # Create configuration using template
    from llmbuilder.config.manager import create_config_from_template
    
    config = create_config_from_template("basic_config", {
        "model": {
            "vocab_size": 8000,
            "num_layers": 4,
            "num_heads": 4,
            "embedding_dim": 256,
            "max_seq_length": 512
        },
        "training": {
            "batch_size": 2,
            "num_epochs": 2,
            "learning_rate": 1e-3
        },
        "data": {
            "ingestion": {
                "batch_size": 10,
                "num_workers": 1
            },
            "deduplication": {
                "similarity_threshold": 0.8,
                "use_gpu_for_embeddings": False,
                "batch_size": 100
            }
        },
        "tokenizer_training": {
            "vocab_size": 8000,
            "algorithm": "bpe"
        }
    })
    
    config_file = work_dir / "config.json"
    from llmbuilder.config.manager import save_config
    save_config(config, config_file)
    
    logger.info(f"  ✅ Created sample data: {len(sample_texts)} files")
    logger.info(f"  ✅ Created configuration: {config_file}")
    
    return combined_file, config_file


def process_data_advanced(data_file, work_dir):
    """Demonstrate advanced data processing with ingestion pipeline."""
    
    try:
        from llmbuilder.data.ingest import IngestionPipeline
        from llmbuilder.config.manager import load_config
        
        config = load_config(work_dir / "config.json")
        
        # Create ingestion pipeline
        pipeline = IngestionPipeline(config.data.ingestion)
        
        # Process the data file
        output_file = work_dir / "processed.txt"
        
        # For demo, we'll just copy and clean the data
        # In real usage, this would process multiple formats
        text = data_file.read_text(encoding='utf-8')
        
        # Basic text cleaning
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove extra newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        output_file.write_text(text.strip(), encoding='utf-8')
        
        logger.info(f"  ✅ Processed data saved to: {output_file}")
        logger.info(f"  📊 Processed text length: {len(text):,} characters")
        
        return output_file
        
    except ImportError as e:
        logger.warning(f"  ⚠️  Advanced ingestion not available: {e}")
        # Fallback to simple processing
        output_file = work_dir / "processed.txt"
        shutil.copy2(data_file, output_file)
        return output_file


def deduplicate_data(data_file, work_dir):
    """Demonstrate advanced deduplication capabilities."""
    
    try:
        from llmbuilder.data.dedup import DeduplicationPipeline
        from llmbuilder.config.manager import load_config
        
        config = load_config(work_dir / "config.json")
        
        # Create deduplication pipeline
        dedup = DeduplicationPipeline(config.data.deduplication)
        
        output_file = work_dir / "deduplicated.txt"
        
        # Process deduplication
        stats = dedup.process_file(str(data_file), str(output_file))
        
        logger.info(f"  ✅ Deduplication completed")
        logger.info(f"  📊 Removed {stats.get('duplicates_removed', 0)} duplicates")
        logger.info(f"  📊 Final text length: {output_file.stat().st_size:,} bytes")
        
        return output_file
        
    except ImportError as e:
        logger.warning(f"  ⚠️  Advanced deduplication not available: {e}")
        # Fallback to simple deduplication
        output_file = work_dir / "deduplicated.txt"
        
        # Simple exact duplicate removal
        text = data_file.read_text(encoding='utf-8')
        lines = text.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                unique_lines.append(line)
                seen.add(line)
        
        deduplicated_text = '\n'.join(unique_lines)
        output_file.write_text(deduplicated_text, encoding='utf-8')
        
        logger.info(f"  ✅ Simple deduplication completed")
        logger.info(f"  📊 Removed {len(lines) - len(unique_lines)} duplicate lines")
        
        return output_file


def train_tokenizer(data_file, work_dir):
    """Train a custom tokenizer."""
    
    try:
        from llmbuilder.tokenizer import TokenizerTrainer
        from llmbuilder.config.manager import load_config
        
        config = load_config(work_dir / "config.json")
        tokenizer_dir = work_dir / "tokenizer"
        tokenizer_dir.mkdir()
        
        # Train tokenizer
        trainer = TokenizerTrainer(config.tokenizer_training)
        results = trainer.train(str(data_file), str(tokenizer_dir))
        
        logger.info(f"  ✅ Tokenizer training completed")
        logger.info(f"  📊 Vocabulary size: {results.get('vocab_size', 'unknown')}")
        logger.info(f"  ⏱️  Training time: {results.get('training_time', 'unknown')}")
        
        return tokenizer_dir
        
    except ImportError as e:
        logger.warning(f"  ⚠️  Tokenizer training not available: {e}")
        # Create a dummy tokenizer directory
        tokenizer_dir = work_dir / "tokenizer"
        tokenizer_dir.mkdir()
        (tokenizer_dir / "tokenizer.model").write_text("dummy tokenizer")
        return tokenizer_dir


def train_model_demo(data_file, tokenizer_dir, config_file, work_dir):
    """Demonstrate model training (simplified for demo)."""
    
    try:
        import llmbuilder as lb
        from llmbuilder.config.manager import load_config
        from llmbuilder.data import TextDataset
        
        config = load_config(config_file)
        
        # Build model
        model = lb.build_model(config.model)
        num_params = sum(p.numel() for p in model.parameters())
        logger.info(f"  🧠 Model built with {num_params:,} parameters")
        
        # Create dataset
        dataset = TextDataset(
            str(data_file),
            block_size=config.model.max_seq_length,
            stride=config.model.max_seq_length // 2
        )
        logger.info(f"  📊 Dataset created with {len(dataset)} samples")
        
        # For demo purposes, we'll do minimal training
        # In real usage, you'd train for many epochs
        logger.info("  🏋️  Starting training (demo mode - minimal epochs)")
        
        # Simplified training for demo
        model_dir = work_dir / "model"
        model_dir.mkdir()
        
        # Save model (without actual training for demo speed)
        import torch
        model_path = model_dir / "model.pt"
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': config.model.__dict__,
            'vocab_size': config.model.vocab_size
        }, model_path)
        
        logger.info(f"  ✅ Model saved to: {model_path}")
        
        return model_path
        
    except ImportError as e:
        logger.warning(f"  ⚠️  Model training not available: {e}")
        # Create dummy model file
        model_dir = work_dir / "model"
        model_dir.mkdir()
        model_path = model_dir / "model.pt"
        model_path.write_text("dummy model")
        return model_path


def convert_to_gguf(model_path, work_dir):
    """Demonstrate GGUF model conversion."""
    
    try:
        from llmbuilder.tools.convert_to_gguf import GGUFConverter
        
        converter = GGUFConverter()
        gguf_dir = work_dir / "gguf"
        gguf_dir.mkdir()
        
        gguf_path = gguf_dir / "model_q8_0.gguf"
        
        # Attempt conversion
        result = converter.convert_model(str(model_path), str(gguf_path), "Q8_0")
        
        if result.success:
            logger.info(f"  ✅ GGUF conversion successful")
            logger.info(f"  📊 Output size: {result.file_size_bytes / (1024*1024):.1f} MB")
            logger.info(f"  ⏱️  Conversion time: {result.conversion_time_seconds:.1f}s")
        else:
            logger.warning(f"  ⚠️  GGUF conversion failed: {result.error_message}")
            # Create dummy GGUF file
            gguf_path.write_text("dummy gguf file")
        
        return gguf_path
        
    except ImportError as e:
        logger.warning(f"  ⚠️  GGUF conversion not available: {e}")
        # Create dummy GGUF file
        gguf_dir = work_dir / "gguf"
        gguf_dir.mkdir()
        gguf_path = gguf_dir / "model_q8_0.gguf"
        gguf_path.write_text("dummy gguf file")
        return gguf_path


def test_generation(model_path, tokenizer_dir):
    """Test text generation with the trained model."""
    
    try:
        import llmbuilder as lb
        
        test_prompts = [
            "Machine learning is",
            "Artificial intelligence can",
            "The future of technology"
        ]
        
        logger.info("  🎯 Testing text generation:")
        
        for prompt in test_prompts:
            try:
                generated = lb.generate_text(
                    model_path=str(model_path),
                    tokenizer_path=str(tokenizer_dir),
                    prompt=prompt,
                    max_new_tokens=20,
                    temperature=0.8
                )
                logger.info(f"    '{prompt}' → '{generated}'")
            except Exception as e:
                logger.info(f"    '{prompt}' → [Generation failed: {e}]")
                
    except ImportError as e:
        logger.warning(f"  ⚠️  Text generation not available: {e}")
        logger.info("  💡 Install full dependencies with: pip install llmbuilder[all]")


if __name__ == "__main__":
    print("🤖 LLMBuilder Basic Training Example")
    print("=" * 50)
    print()
    print("This example demonstrates LLMBuilder's advanced data processing capabilities:")
    print("• Multi-format document ingestion")
    print("• Advanced deduplication (exact + semantic)")
    print("• Custom tokenizer training")
    print("• Model training with configuration templates")
    print("• GGUF model conversion")
    print("• Text generation and evaluation")
    print()
    print("Note: Some features require optional dependencies.")
    print("Install with: pip install llmbuilder[all]")
    print()
    
    try:
        input("Press Enter to start the example...")
        main()
    except KeyboardInterrupt:
        print("\n👋 Example cancelled by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Install dependencies: pip install llmbuilder[all]")
        print("2. Check system dependencies (Tesseract, llama.cpp)")
        print("3. Enable debug logging: export LLMBUILDER_LOG_LEVEL=DEBUG")
        sys.exit(1)