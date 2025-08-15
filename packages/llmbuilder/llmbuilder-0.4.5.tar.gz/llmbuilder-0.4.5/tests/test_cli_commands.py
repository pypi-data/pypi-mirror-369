"""
Unit tests for CLI command parsing and execution.

This module tests the new CLI commands for data processing,
tokenizer training, and GGUF conversion.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from llmbuilder.cli import main


class TestDataProcessingCommands:
    """Test cases for data processing CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_ingest_command_help(self):
        """Test data ingest command help."""
        result = self.runner.invoke(main, ['data', 'ingest', '--help'])
        assert result.exit_code == 0
        assert 'Ingest and process multi-format documents' in result.output
        assert '--input' in result.output
        assert '--output' in result.output
        assert '--formats' in result.output
    
    def test_data_deduplicate_command_help(self):
        """Test data deduplicate command help."""
        result = self.runner.invoke(main, ['data', 'deduplicate', '--help'])
        assert result.exit_code == 0
        assert 'Remove duplicate content from text data' in result.output
        assert '--input' in result.output
        assert '--output' in result.output
        assert '--method' in result.output
        assert '--similarity-threshold' in result.output
    
    @patch('llmbuilder.data.ingest.IngestionPipeline')
    def test_data_ingest_command_execution(self, mock_pipeline_class):
        """Test data ingest command execution."""
        # Create test input file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Test content")
        
        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.process_file.return_value = {
            'files_processed': 1,
            'successful': 1,
            'failed': 0,
            'errors': []
        }
        mock_pipeline_class.return_value = mock_pipeline
        
        # Run command
        result = self.runner.invoke(main, [
            'data', 'ingest',
            '--input', str(test_file),
            '--output', str(self.temp_path / 'output'),
            '--formats', 'all'
        ])
        
        assert result.exit_code == 0
        assert 'Ingestion completed' in result.output
        mock_pipeline_class.assert_called_once()
        mock_pipeline.process_file.assert_called_once()
    
    @patch('llmbuilder.data.dedup.DeduplicationPipeline')
    def test_data_deduplicate_command_execution(self, mock_pipeline_class):
        """Test data deduplicate command execution."""
        # Create test input file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 1\nLine 3\n")
        
        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.remove_exact_duplicates.return_value = ["Line 1", "Line 2", "Line 3"]
        mock_pipeline.remove_semantic_duplicates.return_value = ["Line 1", "Line 2", "Line 3"]
        mock_pipeline_class.return_value = mock_pipeline
        
        # Run command
        result = self.runner.invoke(main, [
            'data', 'deduplicate',
            '--input', str(test_file),
            '--output', str(self.temp_path / 'deduplicated.txt'),
            '--method', 'both'
        ])
        
        assert result.exit_code == 0
        assert 'Deduplication completed' in result.output
        mock_pipeline_class.assert_called_once()
    
    def test_data_ingest_invalid_input(self):
        """Test data ingest with invalid input."""
        result = self.runner.invoke(main, [
            'data', 'ingest',
            '--input', '/nonexistent/path',
            '--output', str(self.temp_path / 'output')
        ])
        
        # Should handle error gracefully
        assert result.exit_code == 0  # CLI doesn't exit with error code
        assert 'failed' in result.output.lower()
    
    def test_data_deduplicate_invalid_method(self):
        """Test data deduplicate with invalid method."""
        result = self.runner.invoke(main, [
            'data', 'deduplicate',
            '--input', str(self.temp_path / 'test.txt'),
            '--output', str(self.temp_path / 'output.txt'),
            '--method', 'invalid'
        ])
        
        assert result.exit_code != 0  # Should fail due to invalid choice
        assert 'Invalid value' in result.output


class TestTokenizerCommands:
    """Test cases for tokenizer CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tokenizer_train_command_help(self):
        """Test tokenizer train command help."""
        result = self.runner.invoke(main, ['tokenizer', 'train', '--help'])
        assert result.exit_code == 0
        assert 'Train a tokenizer on text data' in result.output
        assert '--input' in result.output
        assert '--output' in result.output
        assert '--vocab-size' in result.output
        assert '--algorithm' in result.output
    
    def test_tokenizer_test_command_help(self):
        """Test tokenizer test command help."""
        result = self.runner.invoke(main, ['tokenizer', 'test', '--help'])
        assert result.exit_code == 0
        assert 'Test a trained tokenizer' in result.output
        assert '--text' in result.output
        assert '--file' in result.output
        assert '--interactive' in result.output
    
    @patch('llmbuilder.training.tokenizer.TokenizerTrainer')
    def test_tokenizer_train_command_execution(self, mock_trainer_class):
        """Test tokenizer train command execution."""
        # Create test input file
        test_file = self.temp_path / "corpus.txt"
        test_file.write_text("This is a test corpus for tokenizer training.")
        
        # Mock trainer
        mock_trainer = Mock()
        mock_trainer.train.return_value = {
            'model_file': 'tokenizer.model',
            'vocab_file': 'tokenizer.vocab',
            'training_time': 10.5,
            'final_vocab_size': 1000
        }
        mock_trainer.validate_tokenizer.return_value = {
            'valid': True,
            'test_samples': 100
        }
        mock_trainer_class.return_value = mock_trainer
        
        # Run command
        result = self.runner.invoke(main, [
            'tokenizer', 'train',
            '--input', str(test_file),
            '--output', str(self.temp_path / 'tokenizer'),
            '--vocab-size', '1000',
            '--algorithm', 'bpe',
            '--validate'
        ])
        
        assert result.exit_code == 0
        assert 'Training completed' in result.output
        assert 'Validation passed' in result.output
        mock_trainer_class.assert_called_once()
        mock_trainer.train.assert_called_once()
    
    @patch('llmbuilder.training.tokenizer.TokenizerTrainer')
    def test_tokenizer_test_command_with_text(self, mock_trainer_class):
        """Test tokenizer test command with text input."""
        # Mock trainer and tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.encode.return_value = [1, 2, 3, 4]
        mock_tokenizer.decode.return_value = "test text"
        
        mock_trainer = Mock()
        mock_trainer.load_tokenizer.return_value = mock_tokenizer
        mock_trainer_class.return_value = mock_trainer
        
        # Run command
        result = self.runner.invoke(main, [
            'tokenizer', 'test',
            str(self.temp_path / 'tokenizer'),
            '--text', 'test text'
        ])
        
        assert result.exit_code == 0
        assert 'Tokens:' in result.output
        assert 'Token count:' in result.output
        mock_trainer.load_tokenizer.assert_called_once()
        mock_tokenizer.encode.assert_called_once_with('test text')
    
    def test_tokenizer_train_invalid_algorithm(self):
        """Test tokenizer train with invalid algorithm."""
        result = self.runner.invoke(main, [
            'tokenizer', 'train',
            '--input', str(self.temp_path / 'corpus.txt'),
            '--output', str(self.temp_path / 'tokenizer'),
            '--algorithm', 'invalid'
        ])
        
        assert result.exit_code != 0
        assert 'Invalid value' in result.output


class TestConversionCommands:
    """Test cases for GGUF conversion CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_convert_to_gguf_command_help(self):
        """Test convert-to-gguf command help."""
        result = self.runner.invoke(main, ['convert-to-gguf', '--help'])
        assert result.exit_code == 0
        assert 'Convert model to GGUF format' in result.output
        assert '--output' in result.output
        assert '--quantization' in result.output
        assert '--validate' in result.output
    
    @patch('llmbuilder.tools.convert_to_gguf.GGUFConverter')
    def test_convert_to_gguf_command_execution(self, mock_converter_class):
        """Test convert-to-gguf command execution."""
        # Create mock model directory
        model_dir = self.temp_path / "model"
        model_dir.mkdir()
        (model_dir / "config.json").write_text('{"model_type": "test"}')
        
        # Mock converter
        mock_converter = Mock()
        mock_converter.conversion_scripts = {"llama_cpp": "convert.py"}
        mock_result = Mock()
        mock_result.success = True
        mock_result.output_path = str(self.temp_path / "output.gguf")
        mock_result.file_size_bytes = 1024000
        mock_result.conversion_time_seconds = 30.5
        mock_result.validation_passed = True
        mock_converter.convert_model.return_value = mock_result
        mock_converter_class.return_value = mock_converter
        
        # Run command
        result = self.runner.invoke(main, [
            'convert-to-gguf',
            str(model_dir),
            '--output', str(self.temp_path / 'output.gguf'),
            '--quantization', 'Q8_0',
            '--validate'
        ])
        
        assert result.exit_code == 0
        assert 'Conversion successful' in result.output
        assert 'Validation passed' in result.output
        mock_converter_class.assert_called_once()
        mock_converter.convert_model.assert_called_once()
    
    @patch('llmbuilder.tools.convert_to_gguf.GGUFConverter')
    def test_convert_to_gguf_command_failure(self, mock_converter_class):
        """Test convert-to-gguf command with conversion failure."""
        # Mock converter with failure
        mock_converter = Mock()
        mock_converter.conversion_scripts = {}
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "No conversion scripts available"
        mock_converter.convert_model.return_value = mock_result
        mock_converter_class.return_value = mock_converter
        
        # Run command
        result = self.runner.invoke(main, [
            'convert-to-gguf',
            str(self.temp_path / 'nonexistent'),
            '--output', str(self.temp_path / 'output.gguf')
        ])
        
        assert result.exit_code == 0  # CLI handles errors gracefully
        assert 'Conversion failed' in result.output
    
    def test_convert_to_gguf_invalid_quantization(self):
        """Test convert-to-gguf with invalid quantization."""
        result = self.runner.invoke(main, [
            'convert-to-gguf',
            str(self.temp_path / 'model'),
            '--output', str(self.temp_path / 'output.gguf'),
            '--quantization', 'INVALID'
        ])
        
        assert result.exit_code != 0
        assert 'Invalid value' in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
    
    def test_main_help(self):
        """Test main CLI help."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'LLMBuilder' in result.output
        assert 'data' in result.output
        assert 'tokenizer' in result.output
        assert 'convert-to-gguf' in result.output
    
    def test_data_group_help(self):
        """Test data command group help."""
        result = self.runner.invoke(main, ['data', '--help'])
        assert result.exit_code == 0
        assert 'Data loading and preprocessing commands' in result.output
        assert 'ingest' in result.output
        assert 'deduplicate' in result.output
    
    def test_tokenizer_group_help(self):
        """Test tokenizer command group help."""
        result = self.runner.invoke(main, ['tokenizer', '--help'])
        assert result.exit_code == 0
        assert 'Tokenizer training and management commands' in result.output
        assert 'train' in result.output
        assert 'test' in result.output
    
    def test_convert_group_help(self):
        """Test convert command group help."""
        result = self.runner.invoke(main, ['convert', '--help'])
        assert result.exit_code == 0
        assert 'Model conversion commands' in result.output
        assert 'gguf' in result.output
        assert 'batch' in result.output
    
    def test_command_availability(self):
        """Test that all required commands are available."""
        # Test data commands
        result = self.runner.invoke(main, ['data', 'ingest', '--help'])
        assert result.exit_code == 0
        
        result = self.runner.invoke(main, ['data', 'deduplicate', '--help'])
        assert result.exit_code == 0
        
        # Test tokenizer commands
        result = self.runner.invoke(main, ['tokenizer', 'train', '--help'])
        assert result.exit_code == 0
        
        result = self.runner.invoke(main, ['tokenizer', 'test', '--help'])
        assert result.exit_code == 0
        
        # Test conversion commands
        result = self.runner.invoke(main, ['convert-to-gguf', '--help'])
        assert result.exit_code == 0
        
        result = self.runner.invoke(main, ['convert', 'gguf', '--help'])
        assert result.exit_code == 0
    
    def test_verbose_flag_support(self):
        """Test that verbose flags are supported across commands."""
        commands_with_verbose = [
            ['data', 'ingest', '--help'],
            ['data', 'deduplicate', '--help'],
            ['tokenizer', 'train', '--help'],
            ['convert-to-gguf', '--help']
        ]
        
        for cmd in commands_with_verbose:
            result = self.runner.invoke(main, cmd)
            assert result.exit_code == 0
            assert '--verbose' in result.output or '-v' in result.output
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across commands."""
        # All commands should handle missing required arguments gracefully
        error_commands = [
            ['data', 'ingest'],  # Missing required --input and --output
            ['data', 'deduplicate'],  # Missing required --input and --output
            ['tokenizer', 'train'],  # Missing required --input and --output
            ['convert-to-gguf']  # Missing required model_path and --output
        ]
        
        for cmd in error_commands:
            result = self.runner.invoke(main, cmd)
            # Should exit with error code for missing required arguments
            assert result.exit_code != 0
            assert 'Missing' in result.output or 'required' in result.output.lower()