"""
Unit tests for tokenizer training infrastructure.

This module tests the tokenizer training base classes, configuration,
and validation functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from llmbuilder.training.train_tokenizer import (
    TokenizerConfig,
    ValidationResults,
    TokenizerTrainer,
    HuggingFaceTrainer,
    SentencePieceTrainer,
    create_tokenizer_trainer,
    get_preset_configs
)


class TestTokenizerConfig:
    """Test cases for TokenizerConfig."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = TokenizerConfig()
        
        assert config.backend == "huggingface"
        assert config.vocab_size == 16000
        assert config.algorithm == "bpe"
        assert config.special_tokens == ["<pad>", "<unk>", "<s>", "</s>"]
        assert config.character_coverage == 0.9995
        assert config.max_sentence_length == 4192
        assert config.shuffle_input_sentence is True
        assert config.min_frequency == 2
        assert config.show_progress is True
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = TokenizerConfig(
            backend="sentencepiece",
            vocab_size=32000,
            algorithm="unigram",
            special_tokens=["<pad>", "<unk>", "<bos>", "<eos>"],
            character_coverage=0.999,
            min_frequency=5
        )
        
        assert config.backend == "sentencepiece"
        assert config.vocab_size == 32000
        assert config.algorithm == "unigram"
        assert config.special_tokens == ["<pad>", "<unk>", "<bos>", "<eos>"]
        assert config.character_coverage == 0.999
        assert config.min_frequency == 5
    
    def test_invalid_backend_validation(self):
        """Test validation of invalid backend."""
        with pytest.raises(ValueError, match="Unsupported backend"):
            TokenizerConfig(backend="invalid_backend")
    
    def test_invalid_algorithm_validation(self):
        """Test validation of invalid algorithm."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            TokenizerConfig(algorithm="invalid_algorithm")
    
    def test_invalid_vocab_size_validation(self):
        """Test validation of invalid vocab size."""
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            TokenizerConfig(vocab_size=0)
        
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            TokenizerConfig(vocab_size=-100)
    
    def test_sentencepiece_wordpiece_warning(self, caplog):
        """Test warning when using WordPiece with SentencePiece."""
        config = TokenizerConfig(backend="sentencepiece", algorithm="wordpiece")
        
        # Should automatically change to BPE
        assert config.algorithm == "bpe"
        assert "WordPiece algorithm not directly supported by SentencePiece" in caplog.text
    
    def test_supported_constants(self):
        """Test that supported constants are properly defined."""
        assert "huggingface" in TokenizerConfig.SUPPORTED_BACKENDS
        assert "sentencepiece" in TokenizerConfig.SUPPORTED_BACKENDS
        
        assert "bpe" in TokenizerConfig.SUPPORTED_ALGORITHMS
        assert "wordpiece" in TokenizerConfig.SUPPORTED_ALGORITHMS
        assert "unigram" in TokenizerConfig.SUPPORTED_ALGORITHMS
        
        assert 8000 in TokenizerConfig.VOCAB_SIZE_PRESETS
        assert 16000 in TokenizerConfig.VOCAB_SIZE_PRESETS
        assert 32000 in TokenizerConfig.VOCAB_SIZE_PRESETS
        assert 50000 in TokenizerConfig.VOCAB_SIZE_PRESETS


class TestValidationResults:
    """Test cases for ValidationResults."""
    
    def test_validation_results_creation(self):
        """Test creation of ValidationResults."""
        results = ValidationResults(
            is_valid=True,
            vocab_size=16000,
            test_tokens=["hello", "world"],
            test_ids=[100, 200],
            round_trip_success=True
        )
        
        assert results.is_valid is True
        assert results.vocab_size == 16000
        assert results.test_tokens == ["hello", "world"]
        assert results.test_ids == [100, 200]
        assert results.round_trip_success is True
        assert results.error_message is None
    
    def test_validation_results_with_error(self):
        """Test ValidationResults with error message."""
        results = ValidationResults(
            is_valid=False,
            vocab_size=0,
            test_tokens=[],
            test_ids=[],
            round_trip_success=False,
            error_message="Test error message"
        )
        
        assert results.is_valid is False
        assert results.error_message == "Test error message"


class MockTokenizerTrainer(TokenizerTrainer):
    """Mock tokenizer trainer for testing abstract base class."""
    
    def __init__(self):
        self.trained = False
        self.saved = False
    
    def train(self, corpus_path: str, vocab_size: int, **kwargs) -> str:
        self.trained = True
        return corpus_path
    
    def save_tokenizer(self, output_path: str) -> None:
        self.saved = True
    
    def validate_tokenizer(self, test_text: str) -> ValidationResults:
        return ValidationResults(
            is_valid=True,
            vocab_size=16000,
            test_tokens=["test"],
            test_ids=[1],
            round_trip_success=True
        )


class TestTokenizerTrainerAbstract:
    """Test cases for abstract TokenizerTrainer base class."""
    
    def test_abstract_methods_implementation(self):
        """Test that abstract methods can be implemented."""
        trainer = MockTokenizerTrainer()
        
        # Test train method
        result = trainer.train("test_corpus.txt", 16000)
        assert result == "test_corpus.txt"
        assert trainer.trained is True
        
        # Test save_tokenizer method
        trainer.save_tokenizer("output_path")
        assert trainer.saved is True
        
        # Test validate_tokenizer method
        validation = trainer.validate_tokenizer("test text")
        assert isinstance(validation, ValidationResults)
        assert validation.is_valid is True
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract base class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TokenizerTrainer()


class TestHuggingFaceTrainer:
    """Test cases for HuggingFaceTrainer."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample training corpus
        self.corpus_content = """
        This is a sample training corpus for tokenizer training.
        It contains multiple sentences with various words and patterns.
        The tokenizer will learn to split text into subword units.
        This helps with handling out-of-vocabulary words in language models.
        """
        
        self.corpus_file = self.temp_path / "corpus.txt"
        self.corpus_file.write_text(self.corpus_content, encoding='utf-8')
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test HuggingFaceTrainer initialization."""
        config = TokenizerConfig(backend="huggingface", vocab_size=8000)
        trainer = HuggingFaceTrainer(config)
        
        assert trainer.config == config
        assert trainer.tokenizer is None
        assert isinstance(trainer._tokenizers_available, bool)
    
    def test_tokenizers_availability_check(self):
        """Test tokenizers library availability check."""
        config = TokenizerConfig()
        trainer = HuggingFaceTrainer(config)
        
        # Should return a boolean
        available = trainer._check_tokenizers_availability()
        assert isinstance(available, bool)
    
    @pytest.mark.skipif(True, reason="Requires tokenizers library")
    def test_tokenizer_creation_bpe(self):
        """Test BPE tokenizer creation."""
        config = TokenizerConfig(algorithm="bpe", vocab_size=1000)
        trainer = HuggingFaceTrainer(config)
        
        if trainer._tokenizers_available:
            tokenizer, trainer_obj = trainer._create_tokenizer()
            assert tokenizer is not None
            assert trainer_obj is not None
    
    @pytest.mark.skipif(True, reason="Requires tokenizers library")
    def test_tokenizer_creation_wordpiece(self):
        """Test WordPiece tokenizer creation."""
        config = TokenizerConfig(algorithm="wordpiece", vocab_size=1000)
        trainer = HuggingFaceTrainer(config)
        
        if trainer._tokenizers_available:
            tokenizer, trainer_obj = trainer._create_tokenizer()
            assert tokenizer is not None
            assert trainer_obj is not None
    
    @pytest.mark.skipif(True, reason="Requires tokenizers library")
    def test_tokenizer_creation_unigram(self):
        """Test Unigram tokenizer creation."""
        config = TokenizerConfig(algorithm="unigram", vocab_size=1000)
        trainer = HuggingFaceTrainer(config)
        
        if trainer._tokenizers_available:
            tokenizer, trainer_obj = trainer._create_tokenizer()
            assert tokenizer is not None
            assert trainer_obj is not None
    
    def test_tokenizer_creation_without_library(self):
        """Test tokenizer creation when library is not available."""
        config = TokenizerConfig()
        trainer = HuggingFaceTrainer(config)
        trainer._tokenizers_available = False
        
        with pytest.raises(ImportError, match="tokenizers library required"):
            trainer._create_tokenizer()
    
    @pytest.mark.skipif(True, reason="Requires tokenizers library")
    def test_training_workflow(self):
        """Test complete training workflow."""
        config = TokenizerConfig(vocab_size=1000, show_progress=False)
        trainer = HuggingFaceTrainer(config)
        
        if trainer._tokenizers_available:
            # Train tokenizer
            result = trainer.train(str(self.corpus_file), 1000)
            assert result == str(self.corpus_file)
            assert trainer.tokenizer is not None
            
            # Save tokenizer
            output_dir = self.temp_path / "tokenizer_output"
            trainer.save_tokenizer(str(output_dir))
            
            # Check that files were created
            assert (output_dir / "tokenizer.json").exists()
            assert (output_dir / "config.json").exists()
            
            # Validate tokenizer
            validation = trainer.validate_tokenizer("test text")
            assert isinstance(validation, ValidationResults)
    
    def test_training_without_library(self):
        """Test training when tokenizers library is not available."""
        config = TokenizerConfig()
        trainer = HuggingFaceTrainer(config)
        trainer._tokenizers_available = False
        
        with pytest.raises(ImportError):
            trainer.train(str(self.corpus_file), 1000)
    
    def test_save_without_training(self):
        """Test saving tokenizer without training first."""
        config = TokenizerConfig()
        trainer = HuggingFaceTrainer(config)
        
        with pytest.raises(RuntimeError, match="No tokenizer trained"):
            trainer.save_tokenizer("output_path")
    
    def test_validate_without_training(self):
        """Test validating tokenizer without training first."""
        config = TokenizerConfig()
        trainer = HuggingFaceTrainer(config)
        
        validation = trainer.validate_tokenizer("test text")
        assert validation.is_valid is False
        assert validation.error_message == "No tokenizer trained"


class TestSentencePieceTrainer:
    """Test cases for SentencePieceTrainer."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample training corpus
        self.corpus_content = """
        This is a sample training corpus for SentencePiece tokenizer training.
        It contains multiple sentences with various words and patterns.
        The tokenizer will learn to split text into subword units.
        This helps with handling out-of-vocabulary words in language models.
        """
        
        self.corpus_file = self.temp_path / "corpus.txt"
        self.corpus_file.write_text(self.corpus_content, encoding='utf-8')
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test SentencePieceTrainer initialization."""
        config = TokenizerConfig(backend="sentencepiece", vocab_size=8000)
        trainer = SentencePieceTrainer(config)
        
        assert trainer.config == config
        assert trainer.model_path is None
        assert isinstance(trainer._sentencepiece_available, bool)
    
    def test_sentencepiece_availability_check(self):
        """Test SentencePiece library availability check."""
        config = TokenizerConfig(backend="sentencepiece")
        trainer = SentencePieceTrainer(config)
        
        # Should return a boolean
        available = trainer._check_sentencepiece_availability()
        assert isinstance(available, bool)
    
    @pytest.mark.skipif(True, reason="Requires sentencepiece library")
    def test_training_workflow(self):
        """Test complete SentencePiece training workflow."""
        config = TokenizerConfig(backend="sentencepiece", vocab_size=1000)
        trainer = SentencePieceTrainer(config)
        
        if trainer._sentencepiece_available:
            # Train tokenizer
            model_path = trainer.train(str(self.corpus_file), 1000)
            assert model_path.endswith(".model")
            assert Path(model_path).exists()
            
            # Save tokenizer
            output_dir = self.temp_path / "sp_tokenizer_output"
            trainer.save_tokenizer(str(output_dir))
            
            # Check that files were created
            assert (output_dir / "tokenizer.model").exists()
            assert (output_dir / "config.json").exists()
            
            # Validate tokenizer
            validation = trainer.validate_tokenizer("test text")
            assert isinstance(validation, ValidationResults)
    
    def test_training_without_library(self):
        """Test training when SentencePiece library is not available."""
        config = TokenizerConfig(backend="sentencepiece")
        trainer = SentencePieceTrainer(config)
        trainer._sentencepiece_available = False
        
        with pytest.raises(ImportError):
            trainer.train(str(self.corpus_file), 1000)
    
    def test_save_without_training(self):
        """Test saving tokenizer without training first."""
        config = TokenizerConfig(backend="sentencepiece")
        trainer = SentencePieceTrainer(config)
        
        with pytest.raises(RuntimeError, match="No tokenizer trained"):
            trainer.save_tokenizer("output_path")
    
    def test_validate_without_training(self):
        """Test validating tokenizer without training first."""
        config = TokenizerConfig(backend="sentencepiece")
        trainer = SentencePieceTrainer(config)
        
        validation = trainer.validate_tokenizer("test text")
        assert validation.is_valid is False
        assert validation.error_message == "No tokenizer model available"


class TestTokenizerFactory:
    """Test cases for tokenizer factory functions."""
    
    def test_create_tokenizer_trainer_huggingface(self):
        """Test creating HuggingFace tokenizer trainer."""
        config = TokenizerConfig(backend="huggingface")
        trainer = create_tokenizer_trainer(config)
        
        assert isinstance(trainer, HuggingFaceTrainer)
        assert trainer.config == config
    
    def test_create_tokenizer_trainer_sentencepiece(self):
        """Test creating SentencePiece tokenizer trainer."""
        config = TokenizerConfig(backend="sentencepiece")
        trainer = create_tokenizer_trainer(config)
        
        assert isinstance(trainer, SentencePieceTrainer)
        assert trainer.config == config
    
    def test_create_tokenizer_trainer_invalid_backend(self):
        """Test creating trainer with invalid backend."""
        # This should be caught by TokenizerConfig validation
        with pytest.raises(ValueError, match="Unsupported backend"):
            config = TokenizerConfig(backend="invalid")
    
    def test_get_preset_configs(self):
        """Test getting preset configurations."""
        presets = get_preset_configs()
        
        assert isinstance(presets, dict)
        assert len(presets) > 0
        
        # Check that expected presets exist
        expected_presets = ["small_bpe", "medium_bpe", "large_bpe", "sentencepiece_unigram", "wordpiece"]
        for preset_name in expected_presets:
            assert preset_name in presets
            assert isinstance(presets[preset_name], TokenizerConfig)
        
        # Check specific preset configurations
        small_bpe = presets["small_bpe"]
        assert small_bpe.backend == "huggingface"
        assert small_bpe.vocab_size == 8000
        assert small_bpe.algorithm == "bpe"
        
        sp_unigram = presets["sentencepiece_unigram"]
        assert sp_unigram.backend == "sentencepiece"
        assert sp_unigram.vocab_size == 16000
        assert sp_unigram.algorithm == "unigram"


class TestTokenizerConfigurationIntegration:
    """Integration tests for tokenizer configuration with other components."""
    
    def test_config_serialization(self):
        """Test that TokenizerConfig can be serialized to JSON."""
        config = TokenizerConfig(
            backend="huggingface",
            vocab_size=32000,
            algorithm="wordpiece",
            special_tokens=["<pad>", "<unk>", "<cls>", "<sep>"]
        )
        
        # Convert to dict (simulating JSON serialization)
        config_dict = {
            "backend": config.backend,
            "vocab_size": config.vocab_size,
            "algorithm": config.algorithm,
            "special_tokens": config.special_tokens,
            "character_coverage": config.character_coverage,
            "max_sentence_length": config.max_sentence_length,
            "shuffle_input_sentence": config.shuffle_input_sentence,
            "min_frequency": config.min_frequency,
            "show_progress": config.show_progress,
            "training_params": config.training_params
        }
        
        # Verify all fields are serializable
        import json
        json_str = json.dumps(config_dict)
        assert isinstance(json_str, str)
        
        # Verify deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict["backend"] == "huggingface"
        assert loaded_dict["vocab_size"] == 32000
    
    def test_config_with_training_params(self):
        """Test TokenizerConfig with custom training parameters."""
        training_params = {
            "continuing_subword_prefix": "##",
            "end_of_word_suffix": "</w>",
            "max_token_length": 100
        }
        
        config = TokenizerConfig(
            backend="huggingface",
            algorithm="wordpiece",
            training_params=training_params
        )
        
        assert config.training_params == training_params
        assert config.training_params["continuing_subword_prefix"] == "##"
    
    def test_config_validation_edge_cases(self):
        """Test configuration validation with edge cases."""
        # Test minimum valid vocab size
        config = TokenizerConfig(vocab_size=1)
        assert config.vocab_size == 1
        
        # Test large vocab size
        config = TokenizerConfig(vocab_size=100000)
        assert config.vocab_size == 100000
        
        # Test empty special tokens
        config = TokenizerConfig(special_tokens=[])
        assert config.special_tokens == []
        
        # Test custom special tokens
        custom_tokens = ["<start>", "<end>", "<mask>"]
        config = TokenizerConfig(special_tokens=custom_tokens)
        assert config.special_tokens == custom_tokens