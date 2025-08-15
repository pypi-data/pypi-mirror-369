"""
Unit tests for configuration management utilities.

This module tests the configuration loading, validation, and template
management functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from llmbuilder.config.manager import (
    ConfigurationManager, 
    load_config, 
    save_config, 
    validate_config,
    get_available_templates,
    create_config_from_template
)
from llmbuilder.config.defaults import Config, DefaultConfigs


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.config_manager = ConfigurationManager()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test ConfigurationManager initialization."""
        manager = ConfigurationManager()
        assert manager.template_dir.exists()
        assert manager._available_templates is None
    
    def test_get_available_templates(self):
        """Test getting available templates."""
        templates = self.config_manager.get_available_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Should include the templates we know exist
        expected_templates = ["basic_config", "cpu_optimized_config", "advanced_processing_config"]
        for template in expected_templates:
            assert template in templates
        
        # Second call should return cached result
        templates2 = self.config_manager.get_available_templates()
        assert templates == templates2
    
    def test_load_template_success(self):
        """Test successful template loading."""
        template_data = self.config_manager.load_template("basic_config")
        
        assert isinstance(template_data, dict)
        assert "model" in template_data
        assert "training" in template_data
        assert "data" in template_data
        assert "tokenizer_training" in template_data
        assert "gguf_conversion" in template_data
        
        # Check that it has the new processing sections
        assert "ingestion" in template_data["data"]
        assert "deduplication" in template_data["data"]
    
    def test_load_template_not_found(self):
        """Test loading non-existent template."""
        with pytest.raises(FileNotFoundError, match="Template 'nonexistent' not found"):
            self.config_manager.load_template("nonexistent")
    
    def test_load_template_invalid_json(self):
        """Test loading template with invalid JSON."""
        # Create a temporary template with invalid JSON
        invalid_template = self.config_manager.template_dir / "invalid_test.json"
        invalid_template.write_text("{ invalid json }")
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON in template"):
                self.config_manager.load_template("invalid_test")
        finally:
            invalid_template.unlink(missing_ok=True)
    
    def test_load_config_file_success(self):
        """Test successful config file loading."""
        # Create a valid config file
        config_data = {
            "model": {"vocab_size": 8000, "embedding_dim": 256},
            "training": {"batch_size": 16},
            "data": {"max_length": 512}
        }
        
        config_file = self.temp_dir / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = self.config_manager.load_config_file(config_file)
        
        assert isinstance(config, Config)
        assert config.model.vocab_size == 8000
        assert config.model.embedding_dim == 256
        assert config.training.batch_size == 16
        assert config.data.max_length == 512
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            self.config_manager.load_config_file(nonexistent_file)
    
    def test_load_config_file_invalid_json(self):
        """Test loading config file with invalid JSON."""
        invalid_config = self.temp_dir / "invalid.json"
        invalid_config.write_text("{ invalid json }")
        
        with pytest.raises(ValueError, match="Invalid JSON in config file"):
            self.config_manager.load_config_file(invalid_config)
    
    def test_save_config_file(self):
        """Test saving config file."""
        config = Config()
        config.model.vocab_size = 12000
        config.training.batch_size = 24
        
        output_file = self.temp_dir / "saved_config.json"
        self.config_manager.save_config_file(config, output_file)
        
        assert output_file.exists()
        
        # Load and verify
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["model"]["vocab_size"] == 12000
        assert saved_data["training"]["batch_size"] == 24
    
    def test_validate_config_success(self):
        """Test successful config validation."""
        config = Config()
        assert self.config_manager.validate_config(config) is True
    
    def test_validate_config_failure(self):
        """Test config validation failure."""
        config = Config()
        config.model.max_seq_length = 256
        config.data.max_length = 1024  # Larger than max_seq_length
        
        assert self.config_manager.validate_config(config) is False
    
    def test_create_config_from_template(self):
        """Test creating config from template."""
        config = self.config_manager.create_config_from_template("basic_config")
        
        assert isinstance(config, Config)
        assert config.model.vocab_size == 16000  # From basic_config template
        assert config.validate() is True
    
    def test_create_config_from_template_with_overrides(self):
        """Test creating config from template with overrides."""
        overrides = {
            "model": {"vocab_size": 24000},
            "training": {"batch_size": 64}
        }
        
        config = self.config_manager.create_config_from_template("basic_config", overrides)
        
        assert config.model.vocab_size == 24000  # Overridden
        assert config.training.batch_size == 64   # Overridden
        assert config.model.embedding_dim == 512  # From template (not overridden)
    
    def test_create_config_from_preset(self):
        """Test creating config from preset."""
        config = self.config_manager.create_config_from_preset("cpu_small")
        
        assert isinstance(config, Config)
        assert config.model.embedding_dim == 256  # From cpu_small preset
        assert config.system.device == "cpu"
        assert config.validate() is True
    
    def test_create_config_from_preset_with_overrides(self):
        """Test creating config from preset with overrides."""
        overrides = {
            "training": {"batch_size": 16}
        }
        
        config = self.config_manager.create_config_from_preset("cpu_small", overrides)
        
        assert config.training.batch_size == 16    # Overridden
        assert config.model.embedding_dim == 256   # From preset (not overridden)
    
    def test_get_config_summary(self):
        """Test getting config summary."""
        config = Config()
        summary = self.config_manager.get_config_summary(config)
        
        assert isinstance(summary, dict)
        assert "model" in summary
        assert "training" in summary
        assert "data" in summary
        assert "tokenizer_training" in summary
        assert "gguf_conversion" in summary
        assert "system" in summary
        
        # Check specific values
        assert summary["model"]["vocab_size"] == config.model.vocab_size
        assert summary["training"]["batch_size"] == config.training.batch_size
        assert summary["data"]["ingestion_formats"] == config.data.ingestion.supported_formats
    
    def test_validate_config_file_success(self):
        """Test successful config file validation."""
        # Create a valid config file
        config_data = {"model": {"vocab_size": 8000}}
        config_file = self.temp_dir / "valid_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        result = self.config_manager.validate_config_file(config_file)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["config_summary"] is not None
        assert result["config_summary"]["model"]["vocab_size"] == 8000
    
    def test_validate_config_file_not_found(self):
        """Test validation of non-existent config file."""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        result = self.config_manager.validate_config_file(nonexistent_file)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "File not found" in result["errors"][0]
    
    def test_validate_config_file_invalid(self):
        """Test validation of invalid config file."""
        # Create config that will fail validation
        invalid_config_data = {
            "model": {"max_seq_length": 256},
            "data": {"max_length": 1024}  # Larger than max_seq_length
        }
        
        config_file = self.temp_dir / "invalid_config.json"
        with open(config_file, 'w') as f:
            json.dump(invalid_config_data, f)
        
        result = self.config_manager.validate_config_file(config_file)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        base = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": [1, 2, 3]
        }
        
        override = {
            "a": 10,  # Override scalar
            "b": {"c": 20},  # Override nested value
            "f": 4  # Add new key
        }
        
        result = self.config_manager._deep_merge_dicts(base, override)
        
        assert result["a"] == 10  # Overridden
        assert result["b"]["c"] == 20  # Nested override
        assert result["b"]["d"] == 3   # Preserved from base
        assert result["e"] == [1, 2, 3]  # Preserved from base
        assert result["f"] == 4  # Added from override


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_config_function(self):
        """Test load_config convenience function."""
        config_data = {"model": {"vocab_size": 8000}}
        config_file = self.temp_dir / "test.json"
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = load_config(config_file)
        
        assert isinstance(config, Config)
        assert config.model.vocab_size == 8000
    
    def test_save_config_function(self):
        """Test save_config convenience function."""
        config = Config()
        config.model.vocab_size = 9000
        
        output_file = self.temp_dir / "output.json"
        save_config(config, output_file)
        
        assert output_file.exists()
        
        # Verify content
        with open(output_file, 'r') as f:
            data = json.load(f)
        assert data["model"]["vocab_size"] == 9000
    
    def test_validate_config_function_with_object(self):
        """Test validate_config function with Config object."""
        config = Config()
        assert validate_config(config) is True
        
        # Invalid config
        config.model.max_seq_length = 256
        config.data.max_length = 1024
        assert validate_config(config) is False
    
    def test_validate_config_function_with_file(self):
        """Test validate_config function with file path."""
        config_data = {"model": {"vocab_size": 8000}}
        config_file = self.temp_dir / "test.json"
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        assert validate_config(config_file) is True
        
        # Test with non-existent file
        assert validate_config(self.temp_dir / "nonexistent.json") is False
    
    def test_get_available_templates_function(self):
        """Test get_available_templates convenience function."""
        templates = get_available_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "basic_config" in templates
    
    def test_create_config_from_template_function(self):
        """Test create_config_from_template convenience function."""
        config = create_config_from_template("basic_config")
        
        assert isinstance(config, Config)
        assert config.validate() is True
        
        # With overrides
        overrides = {"model": {"vocab_size": 20000}}
        config_with_overrides = create_config_from_template("basic_config", overrides)
        
        assert config_with_overrides.model.vocab_size == 20000


class TestConfigurationIntegration:
    """Integration tests for configuration management."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigurationManager()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_roundtrip_config_save_load(self):
        """Test saving and loading config maintains integrity."""
        # Create config from template
        original_config = self.config_manager.create_config_from_template("advanced_processing_config")
        
        # Save to file
        config_file = self.temp_dir / "roundtrip.json"
        self.config_manager.save_config_file(original_config, config_file)
        
        # Load from file
        loaded_config = self.config_manager.load_config_file(config_file)
        
        # Compare key values
        assert loaded_config.model.vocab_size == original_config.model.vocab_size
        assert loaded_config.model.embedding_dim == original_config.model.embedding_dim
        assert loaded_config.training.batch_size == original_config.training.batch_size
        assert loaded_config.data.ingestion.supported_formats == original_config.data.ingestion.supported_formats
        assert loaded_config.data.deduplication.similarity_threshold == original_config.data.deduplication.similarity_threshold
        assert loaded_config.tokenizer_training.algorithm == original_config.tokenizer_training.algorithm
        assert loaded_config.gguf_conversion.quantization_level == original_config.gguf_conversion.quantization_level
    
    def test_template_vs_preset_consistency(self):
        """Test that templates and presets produce consistent results."""
        # Load CPU optimized template
        template_config = self.config_manager.create_config_from_template("cpu_optimized_config")
        
        # Create CPU small preset
        preset_config = self.config_manager.create_config_from_preset("cpu_small")
        
        # They should have similar characteristics for CPU optimization
        assert template_config.system.device == "cpu"
        assert preset_config.system.device == "cpu"
        assert template_config.system.mixed_precision is False
        assert preset_config.system.mixed_precision is False
        
        # Both should be valid
        assert template_config.validate() is True
        assert preset_config.validate() is True
    
    def test_config_override_deep_merge(self):
        """Test that deep overrides work correctly."""
        overrides = {
            "data": {
                "ingestion": {
                    "batch_size": 500,
                    "enable_ocr": False
                },
                "deduplication": {
                    "similarity_threshold": 0.95
                }
            },
            "tokenizer_training": {
                "algorithm": "unigram"
            }
        }
        
        config = self.config_manager.create_config_from_template("basic_config", overrides)
        
        # Check that overrides were applied
        assert config.data.ingestion.batch_size == 500
        assert config.data.ingestion.enable_ocr is False
        assert config.data.deduplication.similarity_threshold == 0.95
        assert config.tokenizer_training.algorithm == "unigram"
        
        # Check that non-overridden values are preserved
        assert config.data.ingestion.num_workers == 4  # From template
        assert config.data.deduplication.enable_exact_deduplication is True  # From template
        
        # Should still be valid
        assert config.validate() is True
    
    def test_all_templates_are_loadable_and_valid(self):
        """Test that all available templates can be loaded and are valid."""
        templates = self.config_manager.get_available_templates()
        
        for template_name in templates:
            config = self.config_manager.create_config_from_template(template_name)
            assert config.validate() is True, f"Template '{template_name}' produces invalid config"
            
            # Check that it has all required sections
            summary = self.config_manager.get_config_summary(config)
            required_sections = ["model", "training", "data", "tokenizer_training", "gguf_conversion", "system"]
            for section in required_sections:
                assert section in summary, f"Template '{template_name}' missing section '{section}'"