#!/usr/bin/env python3
"""
Basic Training Example for LLMBuilder

This script demonstrates how easy it is to train a language model with LLMBuilder.
Just provide some text data and LLMBuilder handles everything else!

Usage:
    python basic_training.py

Requirements:
    pip install llmbuilder[all]
"""

import tempfile
from pathlib import Path
import llmbuilder as lb

def main():
    """Simple training example using LLMBuilder's high-level API."""
    
    print("🤖 LLMBuilder Basic Training Example")
    print("=" * 50)
    
    # Create a temporary directory for this example
    work_dir = Path(tempfile.mkdtemp(prefix="llmbuilder_basic_"))
    print(f"📁 Working directory: {work_dir}")
    
    try:
        # Step 1: Create some sample training data
        print("\n📝 Step 1: Creating sample training data...")
        sample_text = """
        Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.
        Deep learning uses neural networks with multiple layers to model complex patterns in data.
        Natural language processing helps computers understand and generate human language.
        Transformers are a type of neural network architecture that has revolutionized NLP.
        Large language models can generate coherent text and answer questions.
        """
        
        data_file = work_dir / "training_data.txt"
        data_file.write_text(sample_text.strip())
        print(f"✅ Created training data: {len(sample_text)} characters")
        
        # Step 2: Train the model using LLMBuilder's one-line API
        print("\n🚀 Step 2: Training model with LLMBuilder...")
        print("This will handle data processing, tokenization, and training automatically!")
        
        # Train using LLMBuilder's high-level API - this is all you need!
        pipeline = lb.train(
            data_path=str(data_file),
            output_dir=str(work_dir / "output"),
            config={
                "vocab_size": 500,  # Small vocab for demo data
                "model": {"vocab_size": 500, "num_layers": 2, "num_heads": 2, "embedding_dim": 128},
                "training": {"batch_size": 1, "num_epochs": 1, "learning_rate": 1e-3}
            }
        )
        
        print("✅ Training completed!")
        
        # Step 3: Generate some text
        print("\n🎯 Step 3: Generating text with trained model...")
        try:
            generated = pipeline.generate("Machine learning is", max_new_tokens=20)
            print(f"Generated: '{generated}'")
        except Exception as e:
            print(f"Generation not available: {e}")
            print("💡 This is normal for a minimal training example")
        
        # Step 4: Show what was created
        print(f"\n📊 Results saved in: {work_dir / 'output'}")
        output_dir = work_dir / "output"
        if output_dir.exists():
            files = list(output_dir.rglob("*"))
            print(f"Created {len(files)} files including model, tokenizer, and checkpoints")
        
        print("\n🎉 Basic training example completed!")
        print("This demonstrates LLMBuilder's power - complex ML training in just a few lines!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Install dependencies: pip install llmbuilder[all]")
        print("2. Check system requirements")
    
    finally:
        # Ask user if they want to keep results
        try:
            keep = input(f"\nKeep results in {work_dir}? (y/N): ").lower().startswith('y')
            if not keep:
                import shutil
                shutil.rmtree(work_dir)
                print("🗑️  Cleaned up temporary files")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()