"""
Configuration management utilities for LLMBuilder.

This module provides utilities for loading, validating, and managing
configuration files with support for templates and validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

from .defaults import Config, DefaultConfigs

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages configuration loading, validation, and templates."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.template_dir = Path(__file__).parent / "templates"
        self._available_templates = None
    
    def get_available_templates(self) -> List[str]:
        """Get list of available configuration templates."""
        if self._available_templates is None:
            self._available_templates = []
            if self.template_dir.exists():
                for template_file in self.template_dir.glob("*.json"):
                    template_name = template_file.stem
                    self._available_templates.append(template_name)
        return self._available_templates.copy()
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load a configuration template by name.
        
        Args:
            template_name: Name of the template (without .json extension)
            
        Returns:
            Dictionary containing the template configuration
            
        Raises:
            FileNotFoundError: If template doesn't exist
            ValueError: If template is invalid JSON
        """
        template_path = self.template_dir / f"{template_name}.json"
        
        if not template_path.exists():
            available = ", ".join(self.get_available_templates())
            raise FileNotFoundError(
                f"Template '{template_name}' not found. "
                f"Available templates: {available}"
            )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            logger.info(f"Loaded configuration template: {template_name}")
            return template_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template '{template_name}': {e}")
    
    def load_config_file(self, config_path: Union[str, Path]) -> Config:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Config object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = Config.from_dict(config_data)
            
            # Validate the loaded configuration
            if not self.validate_config(config):
                raise ValueError(f"Configuration validation failed for: {config_path}")
            
            logger.info(f"Loaded configuration from: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file '{config_path}': {e}")
        except Exception as e:
            raise ValueError(f"Error loading config from '{config_path}': {e}")
    
    def save_config_file(self, config: Config, output_path: Union[str, Path], 
                        indent: int = 2) -> None:
        """
        Save configuration to a file.
        
        Args:
            config: Configuration object to save
            output_path: Path where to save the configuration
            indent: JSON indentation level
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = config.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"Saved configuration to: {output_path}")
    
    def validate_config(self, config: Config) -> bool:
        """
        Validate a configuration object.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return config.validate()
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def create_config_from_template(self, template_name: str, 
                                  overrides: Optional[Dict[str, Any]] = None) -> Config:
        """
        Create a configuration from a template with optional overrides.
        
        Args:
            template_name: Name of the template to use
            overrides: Optional dictionary of values to override
            
        Returns:
            Config object
        """
        template_data = self.load_template(template_name)
        
        if overrides:
            template_data = self._deep_merge_dicts(template_data, overrides)
        
        config = Config.from_dict(template_data)
        
        if not self.validate_config(config):
            raise ValueError(f"Configuration created from template '{template_name}' is invalid")
        
        return config
    
    def create_config_from_preset(self, preset_name: str, 
                                overrides: Optional[Dict[str, Any]] = None) -> Config:
        """
        Create a configuration from a code preset with optional overrides.
        
        Args:
            preset_name: Name of the preset (cpu_small, gpu_medium, etc.)
            overrides: Optional dictionary of values to override
            
        Returns:
            Config object
        """
        config = DefaultConfigs.get_preset(preset_name)
        
        if overrides:
            # Convert config to dict, apply overrides, then back to Config
            config_dict = config.to_dict()
            config_dict = self._deep_merge_dicts(config_dict, overrides)
            config = Config.from_dict(config_dict)
        
        if not self.validate_config(config):
            raise ValueError(f"Configuration created from preset '{preset_name}' is invalid")
        
        return config
    
    def get_config_summary(self, config: Config) -> Dict[str, Any]:
        """
        Get a summary of key configuration parameters.
        
        Args:
            config: Configuration to summarize
            
        Returns:
            Dictionary with key configuration values
        """
        return {
            "model": {
                "vocab_size": config.model.vocab_size,
                "embedding_dim": config.model.embedding_dim,
                "num_layers": config.model.num_layers,
                "num_heads": config.model.num_heads,
                "max_seq_length": config.model.max_seq_length
            },
            "training": {
                "batch_size": config.training.batch_size,
                "learning_rate": config.training.learning_rate,
                "num_epochs": config.training.num_epochs
            },
            "data": {
                "max_length": config.data.max_length,
                "ingestion_formats": config.data.ingestion.supported_formats,
                "deduplication_enabled": {
                    "exact": config.data.deduplication.enable_exact_deduplication,
                    "semantic": config.data.deduplication.enable_semantic_deduplication
                }
            },
            "tokenizer_training": {
                "algorithm": config.tokenizer_training.algorithm,
                "vocab_size": config.tokenizer_training.vocab_size
            },
            "gguf_conversion": {
                "quantization_level": config.gguf_conversion.quantization_level,
                "preferred_script": config.gguf_conversion.preferred_script
            },
            "system": {
                "device": config.system.device,
                "mixed_precision": config.system.mixed_precision,
                "num_workers": config.system.num_workers
            }
        }
    
    def validate_config_file(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a configuration file and return validation results.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "config_summary": None
        }
        
        try:
            config = self.load_config_file(config_path)
            result["valid"] = True
            result["config_summary"] = self.get_config_summary(config)
            
        except FileNotFoundError as e:
            result["errors"].append(f"File not found: {e}")
        except ValueError as e:
            result["errors"].append(f"Validation error: {e}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")
        
        return result
    
    def _deep_merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Dictionary with override values
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result


# Global configuration manager instance
config_manager = ConfigurationManager()


def load_config(config_path: Union[str, Path]) -> Config:
    """
    Convenience function to load a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Config object
    """
    return config_manager.load_config_file(config_path)


def save_config(config: Config, output_path: Union[str, Path]) -> None:
    """
    Convenience function to save a configuration file.
    
    Args:
        config: Configuration object to save
        output_path: Path where to save the configuration
    """
    config_manager.save_config_file(config, output_path)


def validate_config(config: Union[Config, str, Path]) -> bool:
    """
    Convenience function to validate a configuration.
    
    Args:
        config: Configuration object or path to config file
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(config, (str, Path)):
        try:
            config = load_config(config)
        except Exception:
            return False
    
    return config_manager.validate_config(config)


def get_available_templates() -> List[str]:
    """
    Get list of available configuration templates.
    
    Returns:
        List of template names
    """
    return config_manager.get_available_templates()


def create_config_from_template(template_name: str, 
                              overrides: Optional[Dict[str, Any]] = None) -> Config:
    """
    Create a configuration from a template.
    
    Args:
        template_name: Name of the template to use
        overrides: Optional dictionary of values to override
        
    Returns:
        Config object
    """
    return config_manager.create_config_from_template(template_name, overrides)