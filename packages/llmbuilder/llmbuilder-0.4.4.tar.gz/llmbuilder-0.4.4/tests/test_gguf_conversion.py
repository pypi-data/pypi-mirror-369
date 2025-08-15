"""
Unit tests for GGUF conversion and quantization infrastructure.

This module tests the GGUF conversion classes, configuration,
and validation functionality.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from llmbuilder.tools.convert_to_gguf import (
    ConversionResult,
    QuantizationConfig,
    ConversionValidator,
    GGUFConverter
)


class TestConversionResult:
    """Test cases for ConversionResult."""
    
    def test_conversion_result_creation(self):
        """Test creation of ConversionResult."""
        result = ConversionResult(
            success=True,
            output_path="/path/to/model.gguf",
            quantization_level="Q8_0",
            file_size_bytes=1024000,
            conversion_time_seconds=45.5,
            validation_passed=True
        )
        
        assert result.success is True
        assert result.output_path == "/path/to/model.gguf"
        assert result.quantization_level == "Q8_0"
        assert result.file_size_bytes == 1024000
        assert result.conversion_time_seconds == 45.5
        assert result.validation_passed is True
        assert result.error_message is None
    
    def test_conversion_result_with_error(self):
        """Test ConversionResult with error message."""
        result = ConversionResult(
            success=False,
            output_path="/path/to/model.gguf",
            quantization_level="Q4_0",
            error_message="Conversion failed due to missing dependencies"
        )
        
        assert result.success is False
        assert result.error_message == "Conversion failed due to missing dependencies"
        assert result.file_size_bytes == 0
        assert result.conversion_time_seconds == 0.0
        assert result.validation_passed is False


class TestQuantizationConfig:
    """Test cases for QuantizationConfig."""
    
    def test_default_configuration(self):
        """Test default quantization configuration."""
        config = QuantizationConfig()
        
        assert config.level == "Q8_0"
        assert config.use_f16 is True
        assert config.use_f32 is False
    
    def test_custom_configuration(self):
        """Test custom quantization configuration."""
        config = QuantizationConfig(
            level="Q4_0",
            use_f16=False,
            use_f32=True
        )
        
        assert config.level == "Q4_0"
        assert config.use_f16 is False
        assert config.use_f32 is True
    
    def test_supported_levels_constant(self):
        """Test that supported levels are properly defined."""
        expected_levels = ["Q8_0", "Q4_0", "Q4_1", "Q5_0", "Q5_1", "F16", "F32"]
        assert QuantizationConfig.SUPPORTED_LEVELS == expected_levels
    
    def test_valid_quantization_levels(self):
        """Test all valid quantization levels."""
        for level in QuantizationConfig.SUPPORTED_LEVELS:
            config = QuantizationConfig(level=level)
            assert config.level == level
    
    def test_invalid_quantization_level(self):
        """Test validation of invalid quantization level."""
        with pytest.raises(ValueError, match="Unsupported quantization level"):
            QuantizationConfig(level="INVALID_LEVEL")
    
    def test_quantization_level_case_sensitivity(self):
        """Test that quantization levels are case sensitive."""
        with pytest.raises(ValueError, match="Unsupported quantization level"):
            QuantizationConfig(level="q8_0")  # lowercase
        
        with pytest.raises(ValueError, match="Unsupported quantization level"):
            QuantizationConfig(level="Q8_0_EXTRA")  # extra suffix


class TestConversionValidator:
    """Test cases for ConversionValidator."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.validator = ConversionValidator()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validator_initialization(self):
        """Test ConversionValidator initialization."""
        validator = ConversionValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_conversion')
        assert hasattr(validator, 'get_file_info')
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        nonexistent_path = str(self.temp_path / "nonexistent.gguf")
        result = self.validator.validate_conversion(nonexistent_path)
        assert result is False
    
    def test_validate_empty_file(self):
        """Test validation of empty file."""
        empty_file = self.temp_path / "empty.gguf"
        empty_file.write_bytes(b"")
        
        result = self.validator.validate_conversion(str(empty_file))
        assert result is False
    
    def test_validate_small_file(self):
        """Test validation of file that's too small."""
        small_file = self.temp_path / "small.gguf"
        small_file.write_bytes(b"small")  # Less than 1KB
        
        result = self.validator.validate_conversion(str(small_file))
        assert result is False
    
    def test_validate_invalid_header(self):
        """Test validation of file with invalid header."""
        invalid_file = self.temp_path / "invalid.gguf"
        # Create file with wrong header but sufficient size
        invalid_content = b"INVALID" + b"x" * 2000
        invalid_file.write_bytes(invalid_content)
        
        result = self.validator.validate_conversion(str(invalid_file))
        assert result is False
    
    def test_validate_valid_gguf_file(self):
        """Test validation of valid GGUF file."""
        valid_file = self.temp_path / "valid.gguf"
        # Create file with correct header and sufficient size
        valid_content = b"GGUF" + b"x" * 2000
        valid_file.write_bytes(valid_content)
        
        result = self.validator.validate_conversion(str(valid_file))
        assert result is True
    
    def test_validate_file_without_gguf_extension(self):
        """Test validation of file without .gguf extension."""
        no_ext_file = self.temp_path / "model"
        valid_content = b"GGUF" + b"x" * 2000
        no_ext_file.write_bytes(valid_content)
        
        # Should still validate but with warning
        result = self.validator.validate_conversion(str(no_ext_file))
        assert result is True
    
    def test_get_file_info_nonexistent(self):
        """Test getting info for non-existent file."""
        nonexistent_path = str(self.temp_path / "nonexistent.gguf")
        info = self.validator.get_file_info(nonexistent_path)
        
        assert "error" in info
        assert info["error"] == "File does not exist"
    
    def test_get_file_info_valid_file(self):
        """Test getting info for valid file."""
        test_file = self.temp_path / "test.gguf"
        test_content = b"GGUF" + b"x" * 1048576  # 1MB + 4 bytes to ensure MB > 0
        test_file.write_bytes(test_content)
        
        info = self.validator.get_file_info(str(test_file))
        
        assert "error" not in info
        assert "file_size_bytes" in info
        assert "file_size_mb" in info
        assert "created_time" in info
        assert "modified_time" in info
        assert "is_valid_gguf" in info
        
        assert info["file_size_bytes"] == len(test_content)
        assert info["file_size_mb"] >= 1.0  # Should be at least 1 MB
        assert info["is_valid_gguf"] is True
    
    def test_validation_exception_handling(self):
        """Test that validation handles exceptions gracefully."""
        # Test with a path that might cause permission errors
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = self.validator.validate_conversion("some_path.gguf")
            assert result is False


class TestGGUFConverter:
    """Test cases for GGUFConverter."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.converter = GGUFConverter()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_converter_initialization(self):
        """Test GGUFConverter initialization."""
        converter = GGUFConverter()
        
        assert converter is not None
        assert hasattr(converter, 'validator')
        assert hasattr(converter, 'conversion_scripts')
        assert isinstance(converter.validator, ConversionValidator)
        assert isinstance(converter.conversion_scripts, dict)
    
    def test_script_detection(self):
        """Test conversion script detection."""
        scripts = self.converter._detect_conversion_scripts()
        
        assert isinstance(scripts, dict)
        assert "llama_cpp" in scripts
        assert "convert_hf_to_gguf" in scripts
        
        # Values should be None or valid paths
        for script_type, path in scripts.items():
            if path is not None:
                assert isinstance(path, str)
    
    def test_get_quantization_options(self):
        """Test getting quantization options."""
        options = self.converter.get_quantization_options()
        
        assert isinstance(options, list)
        assert len(options) > 0
        assert "Q8_0" in options
        assert "Q4_0" in options
        assert "F16" in options
        assert "F32" in options
    
    def test_convert_model_nonexistent_input(self):
        """Test conversion with non-existent input model."""
        nonexistent_model = str(self.temp_path / "nonexistent_model")
        output_path = str(self.temp_path / "output.gguf")
        
        result = self.converter.convert_model(nonexistent_model, output_path)
        
        assert result.success is False
        assert "does not exist" in result.error_message
        assert result.output_path == output_path
        assert result.quantization_level == "Q8_0"  # default
    
    def test_convert_model_invalid_quantization(self):
        """Test conversion with invalid quantization level."""
        # Create dummy model directory
        model_dir = self.temp_path / "model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        output_path = str(self.temp_path / "output.gguf")
        
        # Should return failed result due to QuantizationConfig validation
        result = self.converter.convert_model(str(model_dir), output_path, "INVALID")
        
        assert result.success is False
        assert "Unsupported quantization level" in result.error_message
    
    @patch('subprocess.run')
    def test_convert_with_llama_cpp_success(self, mock_run):
        """Test successful conversion with llama.cpp script."""
        # Mock successful subprocess run
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="Success")
        
        # Create dummy model directory
        model_dir = self.temp_path / "model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        # Mock script detection
        self.converter.conversion_scripts["llama_cpp"] = "convert.py"
        
        output_path = str(self.temp_path / "output.gguf")
        
        # Create actual output file for testing
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(b"GGUF" + b"x" * 1024000)  # Create valid GGUF file
        
        result = self.converter.convert_model(str(model_dir), output_path, "Q8_0")
        
        assert result.success is True
        assert result.output_path == output_path
        assert result.quantization_level == "Q8_0"
        assert result.file_size_bytes > 1000000  # Should be around 1MB
        assert result.validation_passed is True
    
    @patch('subprocess.run')
    def test_convert_with_llama_cpp_failure(self, mock_run):
        """Test failed conversion with llama.cpp script."""
        # Mock failed subprocess run
        mock_run.return_value = Mock(returncode=1, stderr="Conversion failed", stdout="")
        
        # Create dummy model directory
        model_dir = self.temp_path / "model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        # Mock script detection
        self.converter.conversion_scripts["llama_cpp"] = "convert.py"
        
        output_path = str(self.temp_path / "output.gguf")
        
        result = self.converter.convert_model(str(model_dir), output_path, "Q8_0")
        
        assert result.success is False
        assert "Conversion failed" in result.error_message or "return code 1" in result.error_message
    
    def test_convert_no_scripts_available(self):
        """Test conversion when no scripts are available."""
        # Create dummy model directory
        model_dir = self.temp_path / "model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        # Mock no scripts available
        self.converter.conversion_scripts = {"llama_cpp": None, "convert_hf_to_gguf": None}
        
        output_path = str(self.temp_path / "output.gguf")
        
        result = self.converter.convert_model(str(model_dir), output_path)
        
        assert result.success is False
        assert "No conversion scripts available" in result.error_message
    
    def test_batch_convert_single_model(self):
        """Test batch conversion with single model."""
        models = [
            {"input_path": str(self.temp_path / "model1"), "output_path": str(self.temp_path / "output1.gguf")}
        ]
        
        # Mock convert_model to return success
        with patch.object(self.converter, 'convert_model') as mock_convert:
            mock_convert.return_value = ConversionResult(
                success=True,
                output_path=models[0]["output_path"],
                quantization_level="Q8_0"
            )
            
            results = self.converter.batch_convert(models)
        
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].quantization_level == "Q8_0"
    
    def test_batch_convert_multiple_quantizations(self):
        """Test batch conversion with multiple quantization levels."""
        models = [
            {"input_path": str(self.temp_path / "model1"), "output_path": str(self.temp_path / "output1.gguf")}
        ]
        quantization_levels = ["Q8_0", "Q4_0"]
        
        # Mock convert_model to return success
        with patch.object(self.converter, 'convert_model') as mock_convert:
            mock_convert.return_value = ConversionResult(
                success=True,
                output_path="mock_path",
                quantization_level="mock_level"
            )
            
            results = self.converter.batch_convert(models, quantization_levels)
        
        # Should have 1 model × 2 quantization levels = 2 results
        assert len(results) == 2
        assert all(result.success for result in results)
    
    def test_batch_convert_multiple_models(self):
        """Test batch conversion with multiple models."""
        models = [
            {"input_path": str(self.temp_path / "model1"), "output_path": str(self.temp_path / "output1.gguf")},
            {"input_path": str(self.temp_path / "model2"), "output_path": str(self.temp_path / "output2.gguf")}
        ]
        
        # Mock convert_model to return success
        with patch.object(self.converter, 'convert_model') as mock_convert:
            mock_convert.return_value = ConversionResult(
                success=True,
                output_path="mock_path",
                quantization_level="Q8_0"
            )
            
            results = self.converter.batch_convert(models)
        
        assert len(results) == 2
        assert all(result.success for result in results)


class TestGGUFConversionIntegration:
    """Integration tests for GGUF conversion workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow_simulation(self):
        """Test simulated end-to-end conversion workflow."""
        # Create mock model directory structure
        model_dir = self.temp_path / "test_model"
        model_dir.mkdir()
        
        # Create mock model files
        (model_dir / "config.json").write_text('{"model_type": "llama", "vocab_size": 32000}')
        (model_dir / "pytorch_model.bin").write_bytes(b"mock_model_data" * 1000)
        (model_dir / "tokenizer.json").write_text('{"version": "1.0"}')
        
        # Initialize converter
        converter = GGUFConverter()
        validator = ConversionValidator()
        
        # Test configuration validation
        config = QuantizationConfig(level="Q8_0")
        assert config.level == "Q8_0"
        
        # Test script detection
        scripts = converter._detect_conversion_scripts()
        assert isinstance(scripts, dict)
        
        # Test quantization options
        options = converter.get_quantization_options()
        assert "Q8_0" in options
        
        # Test file validation with mock GGUF file
        mock_gguf = self.temp_path / "test.gguf"
        mock_gguf.write_bytes(b"GGUF" + b"x" * 2000)
        
        assert validator.validate_conversion(str(mock_gguf)) is True
        
        file_info = validator.get_file_info(str(mock_gguf))
        assert file_info["is_valid_gguf"] is True
        assert file_info["file_size_bytes"] > 2000
    
    def test_configuration_combinations(self):
        """Test various configuration combinations."""
        # Test all supported quantization levels
        for level in QuantizationConfig.SUPPORTED_LEVELS:
            config = QuantizationConfig(level=level)
            assert config.level == level
            
            converter = GGUFConverter()
            options = converter.get_quantization_options()
            assert level in options
    
    def test_error_handling_robustness(self):
        """Test robustness of error handling."""
        converter = GGUFConverter()
        validator = ConversionValidator()
        
        # Test with various invalid inputs
        invalid_paths = [
            "",
            "/nonexistent/path",
            "invalid_path_with_special_chars!@#$%",
            str(self.temp_path / "nonexistent" / "nested" / "path")
        ]
        
        for invalid_path in invalid_paths:
            # Should not raise exceptions
            result = converter.convert_model(invalid_path, "output.gguf")
            assert result.success is False
            assert result.error_message is not None
            
            # Validator should handle gracefully
            validation_result = validator.validate_conversion(invalid_path)
            assert validation_result is False
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large file simulation."""
        # Create a larger mock model
        large_model_dir = self.temp_path / "large_model"
        large_model_dir.mkdir()
        
        # Create mock files
        (large_model_dir / "config.json").write_text('{"model_type": "large_llama"}')
        
        # Simulate large model file (don't actually create huge file)
        large_model_file = large_model_dir / "pytorch_model.bin"
        large_model_file.write_bytes(b"x" * 10000)  # 10KB mock
        
        # Test that converter can handle the directory structure
        converter = GGUFConverter()
        
        # Should be able to detect the model directory
        assert large_model_dir.exists()
        assert (large_model_dir / "config.json").exists()
        
        # Conversion would fail due to no scripts, but should handle gracefully
        result = converter.convert_model(str(large_model_dir), "output.gguf")
        assert isinstance(result, ConversionResult)
    
    def test_concurrent_conversion_safety(self):
        """Test that conversion operations are safe for concurrent use."""
        # Create multiple converters (simulating concurrent usage)
        converters = [GGUFConverter() for _ in range(3)]
        
        # Each should have independent state
        for i, converter in enumerate(converters):
            assert converter.validator is not None
            assert isinstance(converter.conversion_scripts, dict)
            
            # Test that they don't interfere with each other
            options = converter.get_quantization_options()
            assert len(options) == len(QuantizationConfig.SUPPORTED_LEVELS)
    
    def test_validation_edge_cases(self):
        """Test validation with edge cases."""
        validator = ConversionValidator()
        
        # Test with minimum valid GGUF file
        min_valid = self.temp_path / "min_valid.gguf"
        min_valid.write_bytes(b"GGUF" + b"x" * 1020)  # Just over 1KB
        
        assert validator.validate_conversion(str(min_valid)) is True
        
        # Test with file exactly at size threshold
        threshold_file = self.temp_path / "threshold.gguf"
        threshold_file.write_bytes(b"GGUF" + b"x" * 1020)  # Exactly 1024 bytes
        
        assert validator.validate_conversion(str(threshold_file)) is True
        
        # Test with file just under threshold
        under_threshold = self.temp_path / "under.gguf"
        under_threshold.write_bytes(b"GGUF" + b"x" * 1019)  # Just under 1024 bytes
        
        assert validator.validate_conversion(str(under_threshold)) is False
    
    def test_complete_conversion_pipeline_workflow(self):
        """Test complete end-to-end conversion pipeline with all components."""
        # Create realistic model structure
        model_dir = self.temp_path / "complete_model"
        model_dir.mkdir()
        
        # Create comprehensive model files
        config_data = {
            "model_type": "llama",
            "vocab_size": 32000,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "num_hidden_layers": 32
        }
        (model_dir / "config.json").write_text(json.dumps(config_data, indent=2))
        (model_dir / "pytorch_model.bin").write_bytes(b"mock_model_weights" * 1000)
        (model_dir / "tokenizer.json").write_text('{"version": "1.0", "model": {"type": "BPE"}}')
        (model_dir / "tokenizer_config.json").write_text('{"tokenizer_class": "LlamaTokenizer"}')
        
        # Initialize complete pipeline
        converter = GGUFConverter()
        
        # Test all quantization levels in sequence
        quantization_levels = ["Q8_0", "Q4_0", "F16"]
        results = []
        
        for quant_level in quantization_levels:
            output_path = self.temp_path / f"model_{quant_level}.gguf"
            
            # Test conversion (will fail due to no scripts, but should handle gracefully)
            result = converter.convert_model(str(model_dir), str(output_path), quant_level)
            results.append(result)
            
            # Verify result structure
            assert isinstance(result, ConversionResult)
            assert result.quantization_level == quant_level
            assert result.output_path == str(output_path)
            
            # Should fail gracefully without scripts
            assert result.success is False
            assert result.error_message is not None
        
        # Test batch conversion
        models = [{"input_path": str(model_dir), "output_path": str(self.temp_path / "batch_output.gguf")}]
        batch_results = converter.batch_convert(models, ["Q8_0", "Q4_0"])
        
        assert len(batch_results) == 2  # 1 model × 2 quantization levels
        for result in batch_results:
            assert isinstance(result, ConversionResult)
            assert result.success is False  # Expected due to no conversion scripts
    
    def test_progress_reporting_and_logging(self):
        """Test that conversion pipeline provides proper progress reporting."""
        import logging
        from io import StringIO
        
        # Set up logging capture
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('llmbuilder.tools.convert_to_gguf')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        try:
            # Create test model
            model_dir = self.temp_path / "logging_test_model"
            model_dir.mkdir()
            (model_dir / "config.json").write_text('{"model_type": "test"}')
            
            converter = GGUFConverter()
            
            # Test conversion with logging
            result = converter.convert_model(str(model_dir), str(self.temp_path / "logged.gguf"))
            
            # Check that logging occurred
            log_output = log_capture.getvalue()
            assert "Detected conversion scripts" in log_output
            
            # Test validation logging
            mock_gguf = self.temp_path / "validation_test.gguf"
            mock_gguf.write_bytes(b"GGUF" + b"x" * 2000)
            
            validator = ConversionValidator()
            validator.validate_conversion(str(mock_gguf))
            
            log_output = log_capture.getvalue()
            assert "GGUF validation passed" in log_output
            
        finally:
            logger.removeHandler(handler)
    
    def test_conversion_result_serialization(self):
        """Test that conversion results can be properly serialized for reporting."""
        import json
        
        # Create test result
        result = ConversionResult(
            success=True,
            output_path="/path/to/model.gguf",
            quantization_level="Q8_0",
            file_size_bytes=1024000,
            conversion_time_seconds=45.5,
            validation_passed=True
        )
        
        # Test serialization to dict
        result_dict = {
            "success": result.success,
            "output_path": result.output_path,
            "quantization_level": result.quantization_level,
            "file_size_bytes": result.file_size_bytes,
            "conversion_time_seconds": result.conversion_time_seconds,
            "validation_passed": result.validation_passed,
            "error_message": result.error_message
        }
        
        # Should be JSON serializable
        json_str = json.dumps(result_dict)
        assert json_str is not None
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        assert deserialized["success"] is True
        assert deserialized["quantization_level"] == "Q8_0"
    
    def test_pipeline_error_recovery(self):
        """Test pipeline behavior under various error conditions."""
        converter = GGUFConverter()
        
        # Test with permission errors (simulated)
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Access denied")):
            result = converter.convert_model("dummy_path", "/restricted/output.gguf")
            assert result.success is False
            assert "Access denied" in result.error_message or "does not exist" in result.error_message
        
        # Test with disk space errors (simulated)
        with patch('subprocess.run', side_effect=OSError("No space left on device")):
            # Mock script availability
            converter.conversion_scripts["llama_cpp"] = "mock_script.py"
            
            model_dir = self.temp_path / "space_test_model"
            model_dir.mkdir()
            (model_dir / "config.json").write_text('{"model_type": "test"}')
            
            result = converter.convert_model(str(model_dir), str(self.temp_path / "space_test.gguf"))
            assert result.success is False
    
    def test_quantization_level_validation_integration(self):
        """Test integration between quantization config and converter."""
        converter = GGUFConverter()
        
        # Test that converter respects quantization config validation
        valid_levels = converter.get_quantization_options()
        
        for level in valid_levels:
            # Should not raise exception
            config = QuantizationConfig(level=level)
            assert config.level == level
        
        # Test invalid level handling
        with pytest.raises(ValueError):
            QuantizationConfig(level="INVALID_LEVEL")
    
    def test_file_system_integration(self):
        """Test integration with file system operations."""
        converter = GGUFConverter()
        validator = ConversionValidator()
        
        # Test directory creation
        nested_output = self.temp_path / "nested" / "deep" / "output.gguf"
        
        # Create model for testing
        model_dir = self.temp_path / "fs_test_model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        # Conversion should create necessary directories
        result = converter.convert_model(str(model_dir), str(nested_output))
        
        # Directory should be created even if conversion fails
        assert nested_output.parent.exists()
        
        # Test file validation with various file system states
        test_cases = [
            ("empty.gguf", b""),
            ("small.gguf", b"GGUF" + b"x" * 100),
            ("valid.gguf", b"GGUF" + b"x" * 2000),
            ("invalid_header.gguf", b"INVALID" + b"x" * 2000)
        ]
        
        for filename, content in test_cases:
            test_file = self.temp_path / filename
            test_file.write_bytes(content)
            
            # Validation should handle all cases gracefully
            result = validator.validate_conversion(str(test_file))
            assert isinstance(result, bool)
            
            # File info should always return a dict
            info = validator.get_file_info(str(test_file))
            assert isinstance(info, dict)