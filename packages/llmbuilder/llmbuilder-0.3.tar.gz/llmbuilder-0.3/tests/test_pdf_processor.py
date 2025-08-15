"""
Unit tests for PDF text extraction processor.

This module tests PDF text extraction functionality including
primary text extraction, OCR fallback, and quality assessment.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from llmbuilder.data.pdf_processor import PDFProcessor


class TestPDFProcessor:
    """Test cases for PDF processor functionality."""
    
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
    
    def test_fitz_availability_check(self):
        """Test PyMuPDF availability checking."""
        processor = PDFProcessor()
        
        # Test the actual availability check method
        with patch('builtins.__import__', side_effect=ImportError):
            assert processor._check_fitz_availability() is False
        
        # Test when import succeeds (mock the import)
        with patch('builtins.__import__'):
            assert processor._check_fitz_availability() is True
    
    def test_ocr_availability_check(self):
        """Test OCR dependencies availability checking."""
        processor = PDFProcessor()
        
        # Test when imports fail
        with patch('builtins.__import__', side_effect=ImportError):
            assert processor._check_ocr_availability() is False
        
        # Test when imports succeed
        with patch('builtins.__import__'):
            assert processor._check_ocr_availability() is True
    
    def test_text_quality_calculation(self):
        """Test text quality scoring algorithm."""
        processor = PDFProcessor()
        
        # High quality text
        good_text = "This is a well-formatted document with proper sentences and good structure."
        quality = processor._calculate_text_quality(good_text, len(good_text), len(good_text.replace(' ', '')))
        assert quality > 0.5
        
        # Low quality text (mostly artifacts)
        bad_text = "....... @@@@@ ##### ...... %%%%% ......."
        quality = processor._calculate_text_quality(bad_text, len(bad_text), len(bad_text.replace(' ', '')))
        assert quality < 0.3
        
        # Empty text
        quality = processor._calculate_text_quality("", 0, 0)
        assert quality == 0.0
        
        # Text with excessive whitespace
        whitespace_text = "word1     word2          word3               word4"
        quality = processor._calculate_text_quality(whitespace_text, len(whitespace_text), len(whitespace_text.replace(' ', '')))
        assert 0.0 <= quality <= 1.0
    
    def test_extract_text_with_fitz_success(self):
        """Test successful text extraction with fitz."""
        processor = PDFProcessor()
        processor._fitz_available = True
        
        # Mock the fitz import and usage
        with patch('builtins.__import__') as mock_import:
            mock_fitz = Mock()
            mock_doc = Mock()
            mock_page = Mock()
            mock_page.get_text.return_value = "Sample PDF text content"
            mock_doc.load_page.return_value = mock_page
            mock_doc.__len__.return_value = 1
            mock_doc.close = Mock()
            mock_fitz.open.return_value = mock_doc
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'fitz':
                    return mock_fitz
                return Mock()
            
            mock_import.side_effect = import_side_effect
            
            text, quality = processor._extract_text_with_fitz(str(self.mock_pdf_path))
            
            assert text == "Sample PDF text content"
            assert isinstance(quality, float)
            assert 0.0 <= quality <= 1.0
    
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_extract_text_with_fitz_failure(self, mock_fitz):
        """Test fitz extraction failure handling."""
        mock_fitz.open.side_effect = Exception("Mock fitz error")
        
        processor = PDFProcessor()
        processor._fitz_available = True
        
        with pytest.raises(RuntimeError, match="Failed to process PDF with fitz"):
            processor._extract_text_with_fitz(str(self.mock_pdf_path))
    
    @patch('llmbuilder.data.pdf_processor.pytesseract')
    @patch('llmbuilder.data.pdf_processor.Image')
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_extract_text_with_ocr_success(self, mock_fitz, mock_image_module, mock_pytesseract):
        """Test successful OCR text extraction."""
        # Mock fitz components
        mock_doc = Mock()
        mock_page = Mock()
        mock_pix = Mock()
        mock_pix.tobytes.return_value = b"mock image data"
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        mock_fitz.Matrix.return_value = Mock()
        
        # Mock PIL Image
        mock_image = Mock()
        mock_image_module.open.return_value = mock_image
        
        # Mock pytesseract
        mock_pytesseract.image_to_string.return_value = "OCR extracted text"
        
        processor = PDFProcessor()
        processor._ocr_available = True
        
        text = processor._extract_text_with_ocr(str(self.mock_pdf_path))
        
        assert text == "OCR extracted text"
        mock_pytesseract.image_to_string.assert_called_once()
        mock_doc.close.assert_called_once()
    
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_process_with_good_quality_text(self, mock_fitz):
        """Test processing with good quality text (no OCR needed)."""
        # Mock high-quality text extraction
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "This is high quality text from a PDF document with proper formatting."
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        
        processor = PDFProcessor(quality_threshold=0.3)
        processor._fitz_available = True
        
        result = processor.process(str(self.mock_pdf_path))
        
        assert "high quality text" in result
        # Should not attempt OCR for good quality text
        mock_doc.close.assert_called_once()
    
    @patch('llmbuilder.data.pdf_processor.pytesseract')
    @patch('llmbuilder.data.pdf_processor.Image')
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_process_with_ocr_fallback(self, mock_fitz, mock_image_module, mock_pytesseract):
        """Test processing with OCR fallback for poor quality text."""
        # Mock low-quality text extraction that triggers OCR
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "... @@@ ### ..."  # Low quality text
        mock_pix = Mock()
        mock_pix.tobytes.return_value = b"mock image data"
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        mock_fitz.Matrix.return_value = Mock()
        
        # Mock OCR success
        mock_image = Mock()
        mock_image_module.open.return_value = mock_image
        mock_pytesseract.image_to_string.return_value = "OCR corrected text"
        
        processor = PDFProcessor(quality_threshold=0.8)  # High threshold to trigger OCR
        processor._fitz_available = True
        processor._ocr_available = True
        
        result = processor.process(str(self.mock_pdf_path))
        
        assert result == "OCR corrected text"
        mock_pytesseract.image_to_string.assert_called()
    
    def test_process_with_invalid_file(self):
        """Test processing with invalid file."""
        processor = PDFProcessor()
        
        with pytest.raises(ValueError, match="Invalid PDF file"):
            processor.process("non_existent.pdf")
    
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_process_with_no_text_extracted(self, mock_fitz):
        """Test processing when no text can be extracted."""
        # Mock empty text extraction
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = ""
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        
        processor = PDFProcessor(ocr_enabled=False)  # Disable OCR
        processor._fitz_available = True
        
        with pytest.raises(RuntimeError, match="Failed to extract text from PDF"):
            processor.process(str(self.mock_pdf_path))
    
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_get_pdf_info(self, mock_fitz):
        """Test PDF information extraction."""
        # Mock PDF document info
        mock_doc = Mock()
        mock_doc.__len__.return_value = 5
        mock_doc.metadata = {"title": "Test PDF", "author": "Test Author"}
        mock_doc.needs_pass = False
        mock_doc.is_pdf = True
        
        # Mock page with images
        mock_page = Mock()
        mock_page.get_images.return_value = [{"image": "data"}]
        mock_doc.load_page.return_value = mock_page
        
        mock_fitz.open.return_value = mock_doc
        
        processor = PDFProcessor()
        processor._fitz_available = True
        
        info = processor.get_pdf_info(str(self.mock_pdf_path))
        
        assert info["page_count"] == 5
        assert info["metadata"]["title"] == "Test PDF"
        assert info["is_encrypted"] is False
        assert info["is_pdf"] is True
        assert info["has_images"] is True
        assert "file_size" in info
    
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_extract_with_options_specific_pages(self, mock_fitz):
        """Test extraction with specific page options."""
        # Mock multi-page document
        mock_doc = Mock()
        mock_doc.__len__.return_value = 5
        
        def mock_load_page(page_num):
            mock_page = Mock()
            mock_page.get_text.return_value = f"Page {page_num} content"
            return mock_page
        
        mock_doc.load_page.side_effect = mock_load_page
        mock_fitz.open.return_value = mock_doc
        
        processor = PDFProcessor()
        processor._fitz_available = True
        
        # Extract specific pages
        result = processor.extract_with_options(str(self.mock_pdf_path), pages=[0, 2, 4])
        
        expected = "Page 0 content\nPage 2 content\nPage 4 content"
        assert result == expected
    
    @patch('llmbuilder.data.pdf_processor.pytesseract')
    @patch('llmbuilder.data.pdf_processor.Image')
    @patch('llmbuilder.data.pdf_processor.fitz')
    def test_extract_with_options_force_ocr(self, mock_fitz, mock_image_module, mock_pytesseract):
        """Test extraction with forced OCR."""
        # Mock fitz components for OCR
        mock_doc = Mock()
        mock_page = Mock()
        mock_pix = Mock()
        mock_pix.tobytes.return_value = b"mock image data"
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        mock_fitz.Matrix.return_value = Mock()
        
        # Mock OCR
        mock_image = Mock()
        mock_image_module.open.return_value = mock_image
        mock_pytesseract.image_to_string.return_value = "Forced OCR text"
        
        processor = PDFProcessor()
        processor._ocr_available = True
        
        result = processor.extract_with_options(str(self.mock_pdf_path), force_ocr=True)
        
        assert result == "Forced OCR text"
        mock_pytesseract.image_to_string.assert_called()
    
    def test_processor_without_dependencies(self):
        """Test processor behavior when dependencies are not available."""
        with patch('llmbuilder.data.pdf_processor.fitz', side_effect=ImportError):
            processor = PDFProcessor()
            assert processor._fitz_available is False
            
            with pytest.raises(RuntimeError, match="PyMuPDF \\(fitz\\) not available"):
                processor._extract_text_with_fitz(str(self.mock_pdf_path))
    
    def test_quality_threshold_edge_cases(self):
        """Test quality threshold edge cases."""
        processor = PDFProcessor()
        
        # Test with various text patterns
        test_cases = [
            ("", 0, 0, 0.0),  # Empty text
            ("a", 1, 1, 0.0),  # Single character
            ("hello world", 11, 10, None),  # Normal text (should be > 0)
            ("123 456 789", 11, 9, None),  # Numbers
            ("!@# $%^ &*()", 11, 0, None),  # Only symbols
        ]
        
        for text, total_chars, text_chars, expected in test_cases:
            quality = processor._calculate_text_quality(text, total_chars, text_chars)
            if expected is not None:
                assert quality == expected
            else:
                assert 0.0 <= quality <= 1.0