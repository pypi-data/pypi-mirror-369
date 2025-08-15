"""
Simplified unit tests for PDF text extraction processor.

This module tests the core PDF processor functionality without
complex dependency mocking.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from llmbuilder.data.pdf_processor import PDFProcessor


class TestPDFProcessorSimple:
    """Simplified test cases for PDF processor functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create a mock PDF file for testing
        self.mock_pdf_path = self.temp_path / "test.pdf"
        self.mock_pdf_path.write_bytes(b"%PDF-1.4\nMock PDF content")
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_processor_initialization(self):
        """Test PDF processor initialization."""
        processor = PDFProcessor()
        
        assert processor.ocr_enabled is True
        assert processor.quality_threshold == 0.5
        assert hasattr(processor, '_fitz_available')
        assert hasattr(processor, '_ocr_available')
    
    def test_processor_initialization_with_options(self):
        """Test PDF processor initialization with custom options."""
        processor = PDFProcessor(ocr_enabled=False, quality_threshold=0.8)
        
        assert processor.ocr_enabled is False
        assert processor.quality_threshold == 0.8
        assert processor._ocr_available is False  # Should be False when disabled
    
    def test_supports_format(self):
        """Test file format support detection."""
        processor = PDFProcessor()
        
        assert processor.supports_format('.pdf') is True
        assert processor.supports_format('.PDF') is True
        assert processor.supports_format('.txt') is False
        assert processor.supports_format('.html') is False
        assert processor.supports_format('.docx') is False
    
    def test_file_validation(self):
        """Test file validation logic."""
        processor = PDFProcessor()
        
        # Test with existing file
        assert processor.validate_file(str(self.mock_pdf_path)) is True
        
        # Test with non-existent file
        assert processor.validate_file("non_existent.pdf") is False
        
        # Test with directory instead of file
        assert processor.validate_file(str(self.temp_path)) is False
    
    def test_text_quality_calculation(self):
        """Test text quality scoring algorithm."""
        processor = PDFProcessor()
        
        # High quality text
        good_text = "This is a well-formatted document with proper sentences and good structure."
        quality = processor._calculate_text_quality(good_text, len(good_text), len(good_text.replace(' ', '')))
        assert quality > 0.3  # Should be reasonably high
        
        # Low quality text (mostly artifacts)
        bad_text = "....... @@@@@ ##### ...... %%%%% ......."
        quality = processor._calculate_text_quality(bad_text, len(bad_text), len(bad_text.replace(' ', '')))
        assert quality < 0.5  # Should be lower
        
        # Empty text
        quality = processor._calculate_text_quality("", 0, 0)
        assert quality == 0.0
        
        # Text with excessive whitespace
        whitespace_text = "word1     word2          word3               word4"
        quality = processor._calculate_text_quality(whitespace_text, len(whitespace_text), len(whitespace_text.replace(' ', '')))
        assert 0.0 <= quality <= 1.0
    
    def test_process_with_invalid_file(self):
        """Test processing with invalid file."""
        processor = PDFProcessor()
        
        with pytest.raises(ValueError, match="Invalid PDF file"):
            processor.process("non_existent.pdf")
    
    def test_dependency_availability_checks(self):
        """Test dependency availability checking methods."""
        processor = PDFProcessor()
        
        # These should return boolean values
        fitz_available = processor._check_fitz_availability()
        ocr_available = processor._check_ocr_availability()
        
        assert isinstance(fitz_available, bool)
        assert isinstance(ocr_available, bool)
    
    def test_quality_calculation_edge_cases(self):
        """Test quality calculation with edge cases."""
        processor = PDFProcessor()
        
        # Test with various text patterns
        test_cases = [
            ("", 0, 0),  # Empty text
            ("a", 1, 1),  # Single character
            ("hello world", 11, 10),  # Normal text
            ("123 456 789", 11, 9),  # Numbers
            ("!@# $%^ &*()", 11, 0),  # Only symbols
        ]
        
        for text, total_chars, text_chars in test_cases:
            quality = processor._calculate_text_quality(text, total_chars, text_chars)
            assert 0.0 <= quality <= 1.0, f"Quality score out of range for text: '{text}'"
    
    def test_processor_without_dependencies_graceful_handling(self):
        """Test that processor handles missing dependencies gracefully."""
        # This test ensures the processor doesn't crash when dependencies are missing
        processor = PDFProcessor()
        
        # The processor should initialize even if dependencies are missing
        assert processor is not None
        
        # Availability flags should be set appropriately
        assert isinstance(processor._fitz_available, bool)
        assert isinstance(processor._ocr_available, bool)
    
    def test_get_pdf_info_without_dependencies(self):
        """Test PDF info method when dependencies are not available."""
        processor = PDFProcessor()
        
        # If fitz is not available, should return error info
        if not processor._fitz_available:
            info = processor.get_pdf_info(str(self.mock_pdf_path))
            assert "error" in info
            assert isinstance(info["error"], str)
    
    def test_extract_with_options_parameter_validation(self):
        """Test parameter validation in extract_with_options method."""
        processor = PDFProcessor()
        
        # Test with invalid file
        with pytest.raises(ValueError, match="Invalid PDF file"):
            processor.extract_with_options("non_existent.pdf")
    
    def test_processor_configuration_validation(self):
        """Test that processor validates configuration parameters."""
        # Test with valid parameters
        processor1 = PDFProcessor(ocr_enabled=True, quality_threshold=0.5)
        assert processor1.ocr_enabled is True
        assert processor1.quality_threshold == 0.5
        
        # Test with edge case parameters
        processor2 = PDFProcessor(ocr_enabled=False, quality_threshold=0.0)
        assert processor2.ocr_enabled is False
        assert processor2.quality_threshold == 0.0
        
        processor3 = PDFProcessor(ocr_enabled=True, quality_threshold=1.0)
        assert processor3.ocr_enabled is True
        assert processor3.quality_threshold == 1.0