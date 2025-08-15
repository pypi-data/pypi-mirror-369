"""
PDF text extraction processor with OCR fallback for LLMBuilder.

This module provides robust PDF text extraction using PyMuPDF (fitz) as the primary
method with pytesseract OCR fallback for scanned or low-quality PDFs.
"""

import logging
import re
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List
import io

from .ingest import DocumentProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(DocumentProcessor):
    """
    PDF text extraction processor with OCR fallback.
    
    This processor uses PyMuPDF (fitz) for primary text extraction and falls back
    to OCR using pytesseract when the extracted text quality is poor or when
    text extraction fails entirely.
    """
    
    def __init__(self, ocr_enabled: bool = True, quality_threshold: float = 0.5):
        """
        Initialize the PDF processor.
        
        Args:
            ocr_enabled: Whether to enable OCR fallback
            quality_threshold: Minimum quality score to accept extracted text (0.0-1.0)
        """
        self.ocr_enabled = ocr_enabled
        self.quality_threshold = quality_threshold
        
        # Check dependencies
        self._fitz_available = self._check_fitz_availability()
        self._ocr_available = self._check_ocr_availability() if ocr_enabled else False
        
        if not self._fitz_available:
            logger.warning("PyMuPDF (fitz) not available. Install with: pip install PyMuPDF")
        
        if ocr_enabled and not self._ocr_available:
            logger.warning("OCR dependencies not available. Install with: pip install pytesseract pillow")
    
    def _check_fitz_availability(self) -> bool:
        """Check if PyMuPDF (fitz) is available."""
        try:
            import fitz
            return True
        except ImportError:
            return False
    
    def _check_ocr_availability(self) -> bool:
        """Check if OCR dependencies are available."""
        try:
            import pytesseract
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports the given file format.
        
        Args:
            file_extension: File extension (e.g., '.pdf')
            
        Returns:
            True if format is supported, False otherwise
        """
        return file_extension.lower() == '.pdf'
    
    def process(self, file_path: str) -> str:
        """
        Extract text from a PDF file with OCR fallback.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted plain text content
            
        Raises:
            RuntimeError: If PDF processing fails and no fallback is available
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid PDF file: {file_path}")
        
        # Try primary text extraction first
        try:
            text, quality_score = self._extract_text_with_fitz(file_path)
            
            # Check if quality is acceptable
            if quality_score >= self.quality_threshold:
                logger.debug(f"PDF text extraction successful (quality: {quality_score:.2f}): {file_path}")
                return text
            else:
                logger.info(f"PDF text quality too low ({quality_score:.2f}), trying OCR: {file_path}")
                
        except Exception as e:
            logger.warning(f"Primary PDF text extraction failed: {e}")
            text = ""
            quality_score = 0.0
        
        # Fallback to OCR if enabled and primary extraction failed or quality is poor
        if self.ocr_enabled and self._ocr_available:
            try:
                ocr_text = self._extract_text_with_ocr(file_path)
                if ocr_text and ocr_text.strip():
                    logger.info(f"OCR extraction successful: {file_path}")
                    return ocr_text
                else:
                    logger.warning(f"OCR extraction produced no text: {file_path}")
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")
        
        # If we have some text from primary extraction, use it even if quality is low
        if text and text.strip():
            logger.warning(f"Using low-quality text extraction (quality: {quality_score:.2f}): {file_path}")
            return text
        
        # No text could be extracted
        raise RuntimeError(f"Failed to extract text from PDF: {file_path}")
    
    def _extract_text_with_fitz(self, file_path: str) -> Tuple[str, float]:
        """
        Extract text using PyMuPDF (fitz).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, quality_score)
        """
        if not self._fitz_available:
            raise RuntimeError("PyMuPDF (fitz) not available")
        
        import fitz
        
        text_blocks = []
        total_chars = 0
        text_chars = 0
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                page_text = page.get_text()
                
                if page_text:
                    text_blocks.append(page_text)
                    
                    # Calculate quality metrics
                    total_chars += len(page_text)
                    # Count actual text characters (not whitespace/control chars)
                    text_chars += len(re.sub(r'\s+', '', page_text))
            
            doc.close()
            
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF with fitz: {e}")
        
        # Combine all text
        full_text = '\n'.join(text_blocks)
        
        # Calculate quality score
        quality_score = self._calculate_text_quality(full_text, total_chars, text_chars)
        
        return full_text, quality_score
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """
        Extract text using OCR (pytesseract).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            OCR-extracted text
        """
        if not self._ocr_available:
            raise RuntimeError("OCR dependencies not available")
        
        import fitz
        import pytesseract
        from PIL import Image
        
        text_blocks = []
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                try:
                    page_text = pytesseract.image_to_string(img, lang='eng')
                    if page_text and page_text.strip():
                        text_blocks.append(page_text)
                except Exception as e:
                    logger.warning(f"OCR failed for page {page_num}: {e}")
                    continue
            
            doc.close()
            
        except Exception as e:
            raise RuntimeError(f"Failed to process PDF with OCR: {e}")
        
        return '\n'.join(text_blocks)
    
    def _calculate_text_quality(self, text: str, total_chars: int, text_chars: int) -> float:
        """
        Calculate a quality score for extracted text.
        
        Args:
            text: Extracted text
            total_chars: Total character count including whitespace
            text_chars: Count of non-whitespace characters
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not text or total_chars == 0:
            return 0.0
        
        # Factor 1: Ratio of text characters to total characters
        char_ratio = text_chars / total_chars if total_chars > 0 else 0
        
        # Factor 2: Presence of readable words (simple heuristic)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        word_count = len(words)
        
        # Factor 3: Average word length (reasonable words are 3-15 chars)
        if word_count > 0:
            avg_word_length = sum(len(word) for word in words) / word_count
            word_length_score = min(1.0, max(0.0, (avg_word_length - 1) / 10))
        else:
            word_length_score = 0.0
        
        # Factor 4: Ratio of words to total characters
        word_density = word_count / total_chars if total_chars > 0 else 0
        
        # Factor 5: Check for common PDF extraction artifacts
        artifact_patterns = [
            r'[^\x00-\x7F]+',  # Non-ASCII characters (might be encoding issues)
            r'\.{3,}',         # Multiple dots (often from table of contents)
            r'\s{5,}',         # Excessive whitespace
        ]
        
        artifact_penalty = 0.0
        for pattern in artifact_patterns:
            matches = len(re.findall(pattern, text))
            artifact_penalty += min(0.3, matches / total_chars * 10)
        
        # Combine factors (weighted average)
        quality_score = (
            char_ratio * 0.3 +
            min(1.0, word_count / 100) * 0.3 +  # Normalize word count
            word_length_score * 0.2 +
            min(1.0, word_density * 50) * 0.2   # Normalize word density
        ) - artifact_penalty
        
        return max(0.0, min(1.0, quality_score))
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get information about a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        if not self._fitz_available:
            return {"error": "PyMuPDF not available"}
        
        try:
            import fitz
            
            doc = fitz.open(file_path)
            
            info = {
                "page_count": len(doc),
                "metadata": doc.metadata,
                "is_encrypted": doc.needs_pass,
                "is_pdf": doc.is_pdf,
                "file_size": Path(file_path).stat().st_size,
            }
            
            # Check if PDF contains images (might need OCR)
            has_images = False
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc.load_page(page_num)
                image_list = page.get_images()
                if image_list:
                    has_images = True
                    break
            
            info["has_images"] = has_images
            
            doc.close()
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def extract_with_options(self, file_path: str, force_ocr: bool = False,
                           pages: Optional[List[int]] = None) -> str:
        """
        Extract text with specific options.
        
        Args:
            file_path: Path to the PDF file
            force_ocr: Force OCR even if text extraction works
            pages: List of specific page numbers to extract (0-indexed)
            
        Returns:
            Extracted text
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid PDF file: {file_path}")
        
        if force_ocr and self._ocr_available:
            return self._extract_text_with_ocr_pages(file_path, pages)
        else:
            return self._extract_text_with_fitz_pages(file_path, pages)
    
    def _extract_text_with_fitz_pages(self, file_path: str, pages: Optional[List[int]] = None) -> str:
        """Extract text from specific pages using fitz."""
        if not self._fitz_available:
            raise RuntimeError("PyMuPDF (fitz) not available")
        
        import fitz
        
        text_blocks = []
        
        try:
            doc = fitz.open(file_path)
            
            page_range = pages if pages is not None else range(len(doc))
            
            for page_num in page_range:
                if 0 <= page_num < len(doc):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text:
                        text_blocks.append(page_text)
            
            doc.close()
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from specific pages: {e}")
        
        return '\n'.join(text_blocks)
    
    def _extract_text_with_ocr_pages(self, file_path: str, pages: Optional[List[int]] = None) -> str:
        """Extract text from specific pages using OCR."""
        if not self._ocr_available:
            raise RuntimeError("OCR dependencies not available")
        
        import fitz
        import pytesseract
        from PIL import Image
        
        text_blocks = []
        
        try:
            doc = fitz.open(file_path)
            
            page_range = pages if pages is not None else range(len(doc))
            
            for page_num in page_range:
                if 0 <= page_num < len(doc):
                    page = doc.load_page(page_num)
                    
                    # Convert to image and OCR
                    mat = fitz.Matrix(2.0, 2.0)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("ppm")
                    img = Image.open(io.BytesIO(img_data))
                    
                    try:
                        page_text = pytesseract.image_to_string(img, lang='eng')
                        if page_text and page_text.strip():
                            text_blocks.append(page_text)
                    except Exception as e:
                        logger.warning(f"OCR failed for page {page_num}: {e}")
            
            doc.close()
            
        except Exception as e:
            raise RuntimeError(f"Failed to OCR specific pages: {e}")
        
        return '\n'.join(text_blocks)