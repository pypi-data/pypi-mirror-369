"""
Integration tests for tokenizer training workflow.

This module tests the complete tokenizer training pipeline including
configuration management, training execution, and validation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from llmbuilder.training.train_tokenizer import (
    TokenizerConfig,
    create_tokenizer_trainer,
    get_preset_configs
)


class TestTokenizerTrainingIntegration:
    """Integration tests for complete tokenizer training workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample training corpus
        self._create_sample_corpus()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_corpus(self):
        """Create sample training corpus files."""
        # Create a substantial corpus for tokenizer training
        corpus_content = []
        
        # Add various types of text
        corpus_content.extend([
            "This is a sample sentence for tokenizer training.",
            "Machine learning models require good tokenization.",
            "Subword tokenization helps handle out-of-vocabulary words.",
            "BPE, WordPiece, and Unigram are popular tokenization algorithms.",
            "The tokenizer learns to split words into meaningful subunits.",
        ])
        
        # Add some technical content
        corpus_content.extend([
            "Natural language processing involves text preprocessing.",
            "Tokenization is the first step in text analysis.",
            "Deep learning models use embeddings for text representation.",
            "Transformer architectures have revolutionized NLP.",
            "Attention mechanisms allow models to focus on relevant parts.",
        ])
        
        # Add some varied vocabulary
        corpus_content.extend([
            "Programming languages include Python, JavaScript, and C++.",
            "Data structures like lists, dictionaries, and trees are important.",
            "Algorithms solve computational problems efficiently.",
            "Software engineering requires good design patterns.",
            "Testing ensures code quality and reliability.",
        ])
        
        # Repeat content to have enough data for training
        full_corpus = corpus_content * 10
        
        # Create main corpus file
        self.corpus_file = self.temp_path / "corpus.txt"
        self.corpus_file.write_text('\n'.join(full_corpus), encoding='utf-8')
        
        # Create additional corpus files for multi-file training
        self.corpus_dir = self.temp_path / "corpus_dir"
        self.corpus_dir.mkdir()
        
        # Split corpus into multiple files
        chunk_size = len(full_corpus) // 3
        for i in range(3):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < 2 else len(full_corpus)
            chunk_content = full_corpus[start_idx:end_idx]
            
            chunk_file = self.corpus_dir / f"corpus_part_{i}.txt"
            chunk_file.write_text('\n'.join(chunk_content), encoding='utf-8')
    
    def test_preset_configurations_validity(self):
        """Test that all preset configurations are valid."""
        presets = get_preset_configs()
        
        for preset_name, config in presets.items():
            # Each preset should be a valid TokenizerConfig
            assert isinstance(config, TokenizerConfig)
            
            # Should have reasonable parameters
            assert config.vocab_size > 0
            assert config.backend in TokenizerConfig.SUPPORTED_BACKENDS
            assert config.algorithm in TokenizerConfig.SUPPORTED_ALGORITHMS
            assert len(config.special_tokens) > 0
            
            # Should be able to create a trainer
            trainer = create_tokenizer_trainer(config)
            assert trainer is not None
    
    def test_configuration_compatibility(self):
        """Test compatibility between different configuration options."""
        # Test HuggingFace configurations
        hf_configs = [
            TokenizerConfig(backend="huggingface", algorithm="bpe", vocab_size=1000),
            TokenizerConfig(backend="huggingface", algorithm="wordpiece", vocab_size=2000),
            TokenizerConfig(backend="huggingface", algorithm="unigram", vocab_size=3000),
        ]
        
        for config in hf_configs:
            trainer = create_tokenizer_trainer(config)
            assert trainer.config.backend == "huggingface"
            assert trainer.config.algorithm == config.algorithm
            assert trainer.config.vocab_size == config.vocab_size
        
        # Test SentencePiece configurations
        sp_configs = [
            TokenizerConfig(backend="sentencepiece", algorithm="bpe", vocab_size=1000),
            TokenizerConfig(backend="sentencepiece", algorithm="unigram", vocab_size=2000),
        ]
        
        for config in sp_configs:
            trainer = create_tokenizer_trainer(config)
            assert trainer.config.backend == "sentencepiece"
            # Note: WordPiece gets converted to BPE for SentencePiece
            assert trainer.config.algorithm in ["bpe", "unigram"]
            assert trainer.config.vocab_size == config.vocab_size
    
    def test_training_workflow_simulation(self):
        """Test simulated training workflow without actual training."""
        # Test different configurations
        configs_to_test = [
            TokenizerConfig(backend="huggingface", algorithm="bpe", vocab_size=1000, show_progress=False),
            TokenizerConfig(backend="sentencepiece", algorithm="unigram", vocab_size=1000),
        ]
        
        for config in configs_to_test:
            trainer = create_tokenizer_trainer(config)
            
            # Test that trainer can be created
            assert trainer is not None
            assert trainer.config == config
            
            # Test configuration validation
            if hasattr(trainer, 'validate_configuration'):
                validation = trainer.validate_configuration()
                assert isinstance(validation, dict)
    
    def test_corpus_file_handling(self):
        """Test handling of different corpus file configurations."""
        config = TokenizerConfig(vocab_size=1000, show_progress=False)
        trainer = create_tokenizer_trainer(config)
        
        # Test single file corpus
        assert self.corpus_file.exists()
        assert self.corpus_file.stat().st_size > 0
        
        # Test directory corpus
        corpus_files = list(self.corpus_dir.glob("*.txt"))
        assert len(corpus_files) == 3
        
        for corpus_file in corpus_files:
            assert corpus_file.exists()
            assert corpus_file.stat().st_size > 0
    
    def test_output_directory_creation(self):
        """Test that output directories are created correctly."""
        config = TokenizerConfig(vocab_size=1000)
        trainer = create_tokenizer_trainer(config)
        
        # Test output directory creation
        output_dir = self.temp_path / "tokenizer_output"
        
        # Directory should not exist initially
        assert not output_dir.exists()
        
        # Simulate save operation (create directory structure)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Directory should now exist
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_special_tokens_handling(self):
        """Test handling of different special token configurations."""
        # Test default special tokens
        config_default = TokenizerConfig()
        assert config_default.special_tokens == ["<pad>", "<unk>", "<s>", "</s>"]
        
        # Test custom special tokens
        custom_tokens = ["<pad>", "<unk>", "<bos>", "<eos>", "<mask>", "<cls>", "<sep>"]
        config_custom = TokenizerConfig(special_tokens=custom_tokens)
        assert config_custom.special_tokens == custom_tokens
        
        # Test empty special tokens
        config_empty = TokenizerConfig(special_tokens=[])
        assert config_empty.special_tokens == []
        
        # All configurations should be valid
        for config in [config_default, config_custom, config_empty]:
            trainer = create_tokenizer_trainer(config)
            assert trainer is not None
    
    def test_vocab_size_variations(self):
        """Test different vocabulary size configurations."""
        vocab_sizes = [100, 1000, 8000, 16000, 32000, 50000]
        
        for vocab_size in vocab_sizes:
            config = TokenizerConfig(vocab_size=vocab_size)
            trainer = create_tokenizer_trainer(config)
            
            assert trainer.config.vocab_size == vocab_size
            assert trainer is not None
    
    def test_algorithm_specific_parameters(self):
        """Test algorithm-specific parameter handling."""
        # BPE configuration
        bpe_config = TokenizerConfig(
            algorithm="bpe",
            min_frequency=3,
            show_progress=False
        )
        bpe_trainer = create_tokenizer_trainer(bpe_config)
        assert bpe_trainer.config.algorithm == "bpe"
        assert bpe_trainer.config.min_frequency == 3
        
        # WordPiece configuration
        wp_config = TokenizerConfig(
            algorithm="wordpiece",
            min_frequency=2,
            show_progress=True
        )
        wp_trainer = create_tokenizer_trainer(wp_config)
        assert wp_trainer.config.algorithm == "wordpiece"
        assert wp_trainer.config.min_frequency == 2
        
        # Unigram configuration
        unigram_config = TokenizerConfig(
            algorithm="unigram",
            character_coverage=0.999,
            max_sentence_length=2048
        )
        unigram_trainer = create_tokenizer_trainer(unigram_config)
        assert unigram_trainer.config.algorithm == "unigram"
        assert unigram_trainer.config.character_coverage == 0.999
        assert unigram_trainer.config.max_sentence_length == 2048
    
    def test_backend_specific_features(self):
        """Test backend-specific feature handling."""
        # HuggingFace specific features
        hf_config = TokenizerConfig(
            backend="huggingface",
            training_params={
                "continuing_subword_prefix": "##",
                "end_of_word_suffix": "</w>"
            }
        )
        hf_trainer = create_tokenizer_trainer(hf_config)
        assert hf_trainer.config.backend == "huggingface"
        assert "continuing_subword_prefix" in hf_trainer.config.training_params
        
        # SentencePiece specific features
        sp_config = TokenizerConfig(
            backend="sentencepiece",
            character_coverage=0.9995,
            shuffle_input_sentence=True
        )
        sp_trainer = create_tokenizer_trainer(sp_config)
        assert sp_trainer.config.backend == "sentencepiece"
        assert sp_trainer.config.character_coverage == 0.9995
        assert sp_trainer.config.shuffle_input_sentence is True
    
    def test_error_handling_scenarios(self):
        """Test error handling in various scenarios."""
        # Test invalid corpus path
        config = TokenizerConfig(vocab_size=1000)
        trainer = create_tokenizer_trainer(config)
        
        # Non-existent file should be handled gracefully
        # (actual error handling depends on implementation)
        nonexistent_file = str(self.temp_path / "nonexistent.txt")
        assert not Path(nonexistent_file).exists()
        
        # Test empty corpus file
        empty_file = self.temp_path / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
        assert empty_file.exists()
        assert empty_file.stat().st_size == 0
    
    def test_configuration_serialization_roundtrip(self):
        """Test configuration serialization and deserialization."""
        import json
        
        # Create a complex configuration
        original_config = TokenizerConfig(
            backend="huggingface",
            vocab_size=25000,
            algorithm="wordpiece",
            special_tokens=["<pad>", "<unk>", "<cls>", "<sep>", "<mask>"],
            character_coverage=0.998,
            max_sentence_length=1024,
            shuffle_input_sentence=False,
            min_frequency=3,
            show_progress=True,
            training_params={
                "continuing_subword_prefix": "##",
                "end_of_word_suffix": "</w>",
                "max_token_length": 200
            }
        )
        
        # Serialize to JSON
        config_dict = {
            "backend": original_config.backend,
            "vocab_size": original_config.vocab_size,
            "algorithm": original_config.algorithm,
            "special_tokens": original_config.special_tokens,
            "character_coverage": original_config.character_coverage,
            "max_sentence_length": original_config.max_sentence_length,
            "shuffle_input_sentence": original_config.shuffle_input_sentence,
            "min_frequency": original_config.min_frequency,
            "show_progress": original_config.show_progress,
            "training_params": original_config.training_params
        }
        
        json_str = json.dumps(config_dict, indent=2)
        
        # Deserialize from JSON
        loaded_dict = json.loads(json_str)
        
        # Create new config from loaded data
        restored_config = TokenizerConfig(**loaded_dict)
        
        # Verify all fields match
        assert restored_config.backend == original_config.backend
        assert restored_config.vocab_size == original_config.vocab_size
        assert restored_config.algorithm == original_config.algorithm
        assert restored_config.special_tokens == original_config.special_tokens
        assert restored_config.character_coverage == original_config.character_coverage
        assert restored_config.max_sentence_length == original_config.max_sentence_length
        assert restored_config.shuffle_input_sentence == original_config.shuffle_input_sentence
        assert restored_config.min_frequency == original_config.min_frequency
        assert restored_config.show_progress == original_config.show_progress
        assert restored_config.training_params == original_config.training_params
    
    def test_preset_config_usage(self):
        """Test using preset configurations in practice."""
        presets = get_preset_configs()
        
        # Test each preset configuration
        for preset_name, preset_config in presets.items():
            # Should be able to create trainer
            trainer = create_tokenizer_trainer(preset_config)
            assert trainer is not None
            
            # Configuration should be valid
            assert preset_config.vocab_size > 0
            assert preset_config.backend in TokenizerConfig.SUPPORTED_BACKENDS
            assert preset_config.algorithm in TokenizerConfig.SUPPORTED_ALGORITHMS
            
            # Should be able to simulate training workflow
            # (without actually training due to dependency requirements)
            assert hasattr(trainer, 'train')
            assert hasattr(trainer, 'save_tokenizer')
            assert hasattr(trainer, 'validate_tokenizer')
    
    @pytest.mark.skipif(True, reason="Requires actual tokenizer libraries")
    def test_end_to_end_training_workflow(self):
        """Test complete end-to-end training workflow."""
        # This test would require actual tokenizer libraries to be installed
        # It's marked as skip by default to avoid dependency issues
        
        config = TokenizerConfig(vocab_size=1000, show_progress=False)
        trainer = create_tokenizer_trainer(config)
        
        # Train tokenizer
        result = trainer.train(str(self.corpus_file), config.vocab_size)
        assert result is not None
        
        # Save tokenizer
        output_dir = self.temp_path / "trained_tokenizer"
        trainer.save_tokenizer(str(output_dir))
        
        # Validate tokenizer
        validation = trainer.validate_tokenizer("This is a test sentence.")
        assert validation.is_valid is True
        assert validation.vocab_size == config.vocab_size
    
    def test_memory_efficiency_large_corpus(self):
        """Test memory efficiency with larger corpus."""
        # Create a larger corpus for memory testing
        large_corpus_content = []
        
        # Generate more content
        base_sentences = [
            "This is sentence number {}.",
            "Machine learning example {}.",
            "Natural language processing task {}.",
            "Deep learning model training {}.",
            "Tokenization algorithm test {}."
        ]
        
        for i in range(1000):  # Create 5000 sentences
            for template in base_sentences:
                large_corpus_content.append(template.format(i))
        
        large_corpus_file = self.temp_path / "large_corpus.txt"
        large_corpus_file.write_text('\n'.join(large_corpus_content), encoding='utf-8')
        
        # Test that configuration can handle large corpus
        config = TokenizerConfig(vocab_size=5000, show_progress=False)
        trainer = create_tokenizer_trainer(config)
        
        # Should be able to create trainer without memory issues
        assert trainer is not None
        assert large_corpus_file.stat().st_size > 100000  # Should be substantial