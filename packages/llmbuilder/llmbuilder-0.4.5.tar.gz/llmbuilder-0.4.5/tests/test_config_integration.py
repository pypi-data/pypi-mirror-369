"""
Unit tests for configuration loading and validation.

This module tests the extended configuration system with new
processing parameters and validation logic.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

from llmbuilder.config.defaults import (
    Config, 
    IngestionConfig, 
    DeduplicationConfig, 
    TokenizerTrainingConfig,
    GGUFConversionConfig,
    DefaultConfigs
)


class TestIngestionConfig:
    """Test cases for IngestionConfig."""
    
    def test_default_ingestion_config(self):
        """Test default ingestion configuration."""
        config = IngestionConfig()
        
        assert config.supported_formats == ['html', 'markdown', 'epub', 'pdf', 'txt']
        assert config.batch_size == 100
        assert config.num_workers == 4
        assert config.enable_ocr is True
        assert config.ocr_quality_threshold == 0.5
    
    def test_custom_ingestion_config(self):
        """Test custom ingestion configuration."""
        config = IngestionConfig(
            supported_formats=['html', 'pdf'],
            batch_size=50,
            num_workers=2,
            enable_ocr=False,
            html_parser='lxml'
        )
        
        assert config.supported_formats == ['html', 'pdf']
        assert config.batch_size == 50
        assert config.num_workers == 2
        assert config.enable_ocr is False
        assert config.html_parser == 'lxml'
    
    def test_ingestion_config_validation(self):
        """Test ingestion configuration validation."""
        # Test invalid batch_size
        with pytest.raises(ValueError, match="batch_size must be positive"):
            IngestionConfig(batch_size=0)
        
        # Test invalid num_workers
        with pytest.raises(ValueError, match="num_workers must be positive"):
            IngestionConfig(num_workers=-1)
        
        # Test invalid ocr_quality_threshold
        with pytest.raises(ValueError, match="ocr_quality_threshold must be between 0 and 1"):
            IngestionConfig(ocr_quality_threshold=1.5)
        
        # Test invalid output_format
        with pytest.raises(ValueError, match="output_format must be 'txt' or 'jsonl'"):
            IngestionConfig(output_format='invalid')


class TestDeduplicationConfig:
    """Test cases for DeduplicationConfig."""
    
    def test_default_deduplication_config(self):
        """Test default deduplication configuration."""
        config = DeduplicationConfig()
        
        assert config.enable_exact_deduplication is True
        assert config.enable_semantic_deduplication is True
        assert config.similarity_threshold == 0.85
        assert config.embedding_model == 'all-MiniLM-L6-v2'
        assert config.batch_size == 1000
    
    def test_custom_deduplication_config(self):
        """Test custom deduplication configuration."""
        config = DeduplicationConfig(
            similarity_threshold=0.9,
            embedding_model='sentence-transformers/all-mpnet-base-v2',
            batch_size=500,
            use_gpu_for_embeddings=False
        )
        
        assert config.similarity_threshold == 0.9
        assert config.embedding_model == 'sentence-transformers/all-mpnet-base-v2'
        assert config.batch_size == 500
        assert config.use_gpu_for_embeddings is False
    
    def test_deduplication_config_validation(self):
        """Test deduplication configuration validation."""
        # Test invalid similarity_threshold
        with pytest.raises(ValueError, match="similarity_threshold must be between 0 and 1"):
            DeduplicationConfig(similarity_threshold=1.5)
        
        # Test invalid batch_size
        with pytest.raises(ValueError, match="batch_size must be positive"):
            DeduplicationConfig(batch_size=0)
        
        # Test invalid similarity_metric
        with pytest.raises(ValueError, match="similarity_metric must be one of"):
            DeduplicationConfig(similarity_metric='invalid')


class TestTokenizerTrainingConfig:
    """Test cases for TokenizerTrainingConfig."""
    
    def test_default_tokenizer_training_config(self):
        """Test default tokenizer training configuration."""
        config = TokenizerTrainingConfig()
        
        assert config.vocab_size == 16000
        assert config.algorithm == "bpe"
        assert config.min_frequency == 2
        assert config.special_tokens == ['<pad>', '<unk>', '<s>', '</s>']
        assert config.character_coverage == 0.9995
    
    def test_custom_tokenizer_training_config(self):
        """Test custom tokenizer training configuration."""
        config = TokenizerTrainingConfig(
            vocab_size=32000,
            algorithm="sentencepiece",
            min_frequency=3,
            special_tokens=['<pad>', '<unk>', '<s>', '</s>', '<mask>'],
            character_coverage=0.9998
        )
        
        assert config.vocab_size == 32000
        assert config.algorithm == "sentencepiece"
        assert config.min_frequency == 3
        assert '<mask>' in config.special_tokens
        assert config.character_coverage == 0.9998
    
    def test_tokenizer_training_config_validation(self):
        """Test tokenizer training configuration validation."""
        # Test invalid vocab_size
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            TokenizerTrainingConfig(vocab_size=0)
        
        # Test invalid algorithm
        with pytest.raises(ValueError, match="algorithm must be one of"):
            TokenizerTrainingConfig(algorithm="invalid")
        
        # Test invalid min_frequency
        with pytest.raises(ValueError, match="min_frequency must be at least 1"):
            TokenizerTrainingConfig(min_frequency=0)
        
        # Test invalid character_coverage
        with pytest.raises(ValueError, match="character_coverage must be between 0 and 1"):
            TokenizerTrainingConfig(character_coverage=1.5)


class TestGGUFConversionConfig:
    """Test cases for GGUFConversionConfig."""
    
    def test_default_gguf_conversion_config(self):
        """Test default GGUF conversion configuration."""
        config = GGUFConversionConfig()
        
        assert config.quantization_level == "Q8_0"
        assert config.validate_output is True
        assert config.conversion_timeout == 3600
        assert config.preferred_script == "auto"
    
    def test_custom_gguf_conversion_config(self):
        """Test custom GGUF conversion configuration."""
        config = GGUFConversionConfig(
            quantization_level="Q4_0",
            validate_output=False,
            conversion_timeout=7200,
            preferred_script="llama_cpp",
            output_naming="quantization_suffix"
        )
        
        assert config.quantization_level == "Q4_0"
        assert config.validate_output is False
        assert config.conversion_timeout == 7200
        assert config.preferred_script == "llama_cpp"
        assert config.output_naming == "quantization_suffix"
    
    def test_gguf_conversion_config_validation(self):
        """Test GGUF conversion configuration validation."""
        # Test invalid quantization_level
        with pytest.raises(ValueError, match="quantization_level must be one of"):
            GGUFConversionConfig(quantization_level="INVALID")
        
        # Test invalid conversion_timeout
        with pytest.raises(ValueError, match="conversion_timeout must be positive"):
            GGUFConversionConfig(conversion_timeout=0)
        
        # Test invalid preferred_script
        with pytest.raises(ValueError, match="preferred_script must be one of"):
            GGUFConversionConfig(preferred_script="invalid")


class TestConfigIntegration:
    """Test cases for integrated configuration system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_with_new_sections(self):
        """Test Config class with new configuration sections."""
        config = Config()
        
        # Check that new sections are present
        assert hasattr(config, 'tokenizer_training')
        assert hasattr(config, 'gguf_conversion')
        assert hasattr(config.data, 'ingestion')
        assert hasattr(config.data, 'deduplication')
        
        # Check default values
        assert isinstance(config.tokenizer_training, TokenizerTrainingConfig)
        assert isinstance(config.gguf_conversion, GGUFConversionConfig)
        assert isinstance(config.data.ingestion, IngestionConfig)
        assert isinstance(config.data.deduplication, DeduplicationConfig)
    
    def test_config_validation_with_new_sections(self):
        """Test configuration validation with new sections."""
        config = Config()
        
        # Should validate successfully with defaults
        assert config.validate() is True
        
        # Test auto-sync behavior - vocab_size should be automatically synced
        original_model_vocab_size = config.model.vocab_size
        config.tokenizer_training.vocab_size = 32000
        
        # Validation should succeed and auto-sync the values
        assert config.validate() is True
        assert config.tokenizer_training.vocab_size == original_model_vocab_size  # Should be synced back
        assert config.tokenizer.vocab_size == original_model_vocab_size  # Should also be synced
        
        # Test deduplication auto-sync behavior
        original_max_length = config.data.max_length
        config.data.deduplication.chunk_size = 2048  # Larger than max_length
        
        # Validation should succeed and auto-sync the chunk_size
        assert config.validate() is True
        assert config.data.deduplication.chunk_size <= original_max_length  # Should be synced down
        
        # Test a validation that should still fail - sequence length consistency
        config.model.max_seq_length = 256  # Smaller than data.max_length
        with pytest.raises(ValueError, match="Model max_seq_length.*must be"):
            config.validate()
    
    def test_config_from_dict_with_new_sections(self):
        """Test Config.from_dict with new configuration sections."""
        config_dict = {
            "model": {"vocab_size": 32000, "embedding_dim": 768},
            "data": {
                "max_length": 1024,
                "ingestion": {
                    "batch_size": 200,
                    "enable_ocr": True
                },
                "deduplication": {
                    "similarity_threshold": 0.9,
                    "embedding_model": "custom-model"
                }
            },
            "tokenizer_training": {
                "vocab_size": 32000,
                "algorithm": "sentencepiece"
            },
            "gguf_conversion": {
                "quantization_level": "Q4_0",
                "preferred_script": "llama_cpp"
            }
        }
        
        config = Config.from_dict(config_dict)
        
        # Check model config
        assert config.model.vocab_size == 32000
        assert config.model.embedding_dim == 768
        
        # Check nested data config
        assert config.data.max_length == 1024
        assert config.data.ingestion.batch_size == 200
        assert config.data.ingestion.enable_ocr is True
        assert config.data.deduplication.similarity_threshold == 0.9
        assert config.data.deduplication.embedding_model == "custom-model"
        
        # Check new sections
        assert config.tokenizer_training.vocab_size == 32000
        assert config.tokenizer_training.algorithm == "sentencepiece"
        assert config.gguf_conversion.quantization_level == "Q4_0"
        assert config.gguf_conversion.preferred_script == "llama_cpp"
    
    def test_config_to_dict_with_new_sections(self):
        """Test Config.to_dict with new configuration sections."""
        config = Config()
        config.tokenizer_training.algorithm = "sentencepiece"
        config.gguf_conversion.quantization_level = "Q4_0"
        config.data.ingestion.batch_size = 200
        
        config_dict = config.to_dict()
        
        # Check that new sections are in the dictionary
        assert 'tokenizer_training' in config_dict
        assert 'gguf_conversion' in config_dict
        assert 'ingestion' in config_dict['data']
        assert 'deduplication' in config_dict['data']
        
        # Check values
        assert config_dict['tokenizer_training']['algorithm'] == "sentencepiece"
        assert config_dict['gguf_conversion']['quantization_level'] == "Q4_0"
        assert config_dict['data']['ingestion']['batch_size'] == 200
    
    def test_config_template_loading(self):
        """Test loading configuration from template files."""
        # Test basic config template
        basic_template_path = Path("llmbuilder/config/templates/basic_config.json")
        if basic_template_path.exists():
            with open(basic_template_path, 'r') as f:
                config_dict = json.load(f)
            
            config = Config.from_dict(config_dict)
            assert config.validate() is True
            
            # Check that advanced sections are present
            assert hasattr(config, 'tokenizer_training')
            assert hasattr(config, 'gguf_conversion')
    
    def test_preset_configs_with_new_sections(self):
        """Test that preset configurations work with new sections."""
        presets = ['cpu_small', 'gpu_medium', 'gpu_large', 'inference']
        
        for preset_name in presets:
            config = DefaultConfigs.get_preset(preset_name)
            
            # Should have new sections with defaults
            assert hasattr(config, 'tokenizer_training')
            assert hasattr(config, 'gguf_conversion')
            assert hasattr(config.data, 'ingestion')
            assert hasattr(config.data, 'deduplication')
            
            # Should validate successfully
            assert config.validate() is True
    
    def test_backward_compatibility(self):
        """Test backward compatibility with old configuration format."""
        # Old-style flat configuration
        old_config_dict = {
            "vocab_size": 16000,
            "n_embd": 512,
            "n_layer": 8,
            "n_head": 8,
            "block_size": 1024,
            "dropout": 0.1,
            "device": "cuda"
        }
        
        config = Config.from_dict(old_config_dict)
        
        # Should map to new structure
        assert config.model.vocab_size == 16000
        assert config.model.embedding_dim == 512
        assert config.model.num_layers == 8
        assert config.model.num_heads == 8
        assert config.model.max_seq_length == 1024
        assert config.model.dropout == 0.1
        assert config.system.device == "cuda"
        
        # Should have new sections with defaults
        assert hasattr(config, 'tokenizer_training')
        assert hasattr(config, 'gguf_conversion')
        
        # Should validate
        assert config.validate() is True
    
    def test_config_file_roundtrip(self):
        """Test saving and loading configuration files."""
        # Create a config with custom values
        config = Config()
        config.model.vocab_size = 32000
        config.tokenizer_training.vocab_size = 32000
        config.tokenizer_training.algorithm = "sentencepiece"
        config.gguf_conversion.quantization_level = "Q4_0"
        config.data.ingestion.batch_size = 200
        config.data.deduplication.similarity_threshold = 0.9
        
        # Save to file
        config_file = self.temp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        # Load from file
        with open(config_file, 'r') as f:
            loaded_dict = json.load(f)
        
        loaded_config = Config.from_dict(loaded_dict)
        
        # Should match original
        assert loaded_config.model.vocab_size == 32000
        assert loaded_config.tokenizer_training.vocab_size == 32000
        assert loaded_config.tokenizer_training.algorithm == "sentencepiece"
        assert loaded_config.gguf_conversion.quantization_level == "Q4_0"
        assert loaded_config.data.ingestion.batch_size == 200
        assert loaded_config.data.deduplication.similarity_threshold == 0.9
        
        # Should validate
        assert loaded_config.validate() is True


class TestConfigurationExamples:
    """Test cases for configuration examples and templates."""
    
    def test_all_templates_are_valid(self):
        """Test that all configuration templates are valid."""
        template_dir = Path("llmbuilder/config/templates")
        
        if template_dir.exists():
            for template_file in template_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    config_dict = json.load(f)
                
                # Should load without errors
                config = Config.from_dict(config_dict)
                
                # Should validate successfully
                assert config.validate() is True, f"Template {template_file.name} failed validation"
    
    def test_template_completeness(self):
        """Test that templates include all necessary sections."""
        template_dir = Path("llmbuilder/config/templates")
        
        if template_dir.exists():
            for template_file in template_dir.glob("*.json"):
                with open(template_file, 'r') as f:
                    config_dict = json.load(f)
                
                # Should have main sections
                required_sections = ['model', 'training', 'data', 'system']
                for section in required_sections:
                    assert section in config_dict, f"Template {template_file.name} missing {section} section"
                
                # Should have advanced sections
                advanced_sections = ['tokenizer_training', 'gguf_conversion']
                for section in advanced_sections:
                    assert section in config_dict, f"Template {template_file.name} missing {section} section"
                
                # Data section should have nested configs
                assert 'ingestion' in config_dict['data'], f"Template {template_file.name} missing data.ingestion"
                assert 'deduplication' in config_dict['data'], f"Template {template_file.name} missing data.deduplication"