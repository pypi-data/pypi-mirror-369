"""
Multi-format document ingestion engine for LLMBuilder.

This module provides classes for extracting clean text from various document formats
including HTML, Markdown, EPUB, and PDF with OCR fallback support.
"""

import os
import logging
import re
import mimetypes
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Set, Any, Callable, Iterator
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class ProcessingError:
    """Represents an error that occurred during document processing."""
    file_path: str
    error_type: str
    message: str
    timestamp: float


@dataclass
class ProcessingStats:
    """Statistics from document processing operations."""
    files_processed: int = 0
    files_failed: int = 0
    total_size_bytes: int = 0
    processing_time_seconds: float = 0.0
    errors: List[ProcessingError] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class DocumentProcessor(ABC):
    """Abstract base class for format-specific document processors."""
    
    @abstractmethod
    def process(self, file_path: str) -> str:
        """
        Extract clean text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted plain text content
            
        Raises:
            ProcessingError: If document processing fails
        """
        pass
    
    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports the given file format.
        
        Args:
            file_extension: File extension (e.g., '.html', '.pdf')
            
        Returns:
            True if format is supported, False otherwise
        """
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file exists and is readable.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and os.access(file_path, os.R_OK)
        except Exception as e:
            logger.warning(f"File validation failed for {file_path}: {e}")
            return False


class HTMLProcessor(DocumentProcessor):
    """
    HTML document processor using BeautifulSoup for clean text extraction.
    
    This processor extracts clean text from HTML documents, removing
    scripts, styles, and other non-content elements while preserving
    text structure and handling encoding issues gracefully.
    """
    
    def __init__(self):
        """Initialize the HTML processor."""
        self._bs4_available = self._check_beautifulsoup_availability()
        
        # Common HTML tags that should be treated as block elements (add newlines)
        self.block_tags = {
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'li', 'br', 'hr', 'blockquote', 'pre', 'article',
            'section', 'header', 'footer', 'main', 'aside'
        }
        
        # Tags to completely remove (including content)
        self.remove_tags = {'script', 'style', 'meta', 'link', 'noscript'}
        
        # Regex patterns for cleaning
        self.whitespace_pattern = re.compile(r'\s+')
        self.multiple_newlines_pattern = re.compile(r'\n\s*\n\s*\n+')
    
    def _check_beautifulsoup_availability(self) -> bool:
        """Check if BeautifulSoup is available."""
        try:
            import bs4
            return True
        except ImportError:
            logger.error("BeautifulSoup4 not available. Install with: pip install beautifulsoup4")
            return False
    
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports HTML formats.
        
        Args:
            file_extension: File extension to check
            
        Returns:
            True if HTML format is supported
        """
        return file_extension.lower() in ['.html', '.htm']
    
    def process(self, file_path: str) -> str:
        """
        Extract clean text from an HTML file.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            Extracted plain text content
            
        Raises:
            ImportError: If BeautifulSoup is not available
            ValueError: If file processing fails
        """
        if not self._bs4_available:
            raise ImportError("BeautifulSoup4 required for HTML processing")
        
        try:
            from bs4 import BeautifulSoup
            
            # Read the HTML file with encoding detection
            html_content = self._read_html_file(file_path)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract text with structure preservation
            text_content = self._extract_structured_text(soup)
            
            # Clean and normalize the text
            cleaned_text = self._clean_text(text_content)
            
            if not cleaned_text.strip():
                raise ValueError("No text content found in HTML file")
            
            logger.debug(f"Extracted {len(cleaned_text)} characters from {file_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to process HTML file {file_path}: {e}")
            raise ValueError(f"HTML processing failed: {e}")
    
    def _read_html_file(self, file_path: str) -> str:
        """
        Read HTML file with encoding detection and error handling.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            HTML content as string
        """
        # Try common encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        # If all encodings fail, try with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            logger.warning(f"Read {file_path} with UTF-8 and error replacement")
            return content
        except Exception as e:
            raise ValueError(f"Could not read HTML file {file_path}: {e}")
    
    def _remove_unwanted_elements(self, soup):
        """
        Remove script, style, and other unwanted elements from soup.
        
        Args:
            soup: BeautifulSoup object to clean
        """
        # Remove unwanted tags and their content
        for tag_name in self.remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Remove comments
        from bs4 import Comment
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
    
    def _extract_structured_text(self, soup) -> str:
        """
        Extract text while preserving document structure.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Structured text content
        """
        # Use a simpler, more reliable approach
        # Get text with separators for block elements
        text_content = soup.get_text(separator='\n', strip=True)
        
        # If no content found, try alternative extraction
        if not text_content.strip():
            # Try extracting from body only
            body = soup.find('body')
            if body:
                text_content = body.get_text(separator='\n', strip=True)
        
        return text_content
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize whitespace within each line
            cleaned_line = self.whitespace_pattern.sub(' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        result = '\n'.join(cleaned_lines)
        
        # Handle multiple consecutive newlines (reduce to double newlines max)
        result = self.multiple_newlines_pattern.sub('\n\n', result)
        
        return result.strip()


class MarkdownProcessor(DocumentProcessor):
    """
    Markdown document processor for converting markdown to plain text.
    
    This processor converts Markdown documents to clean plain text,
    removing markdown syntax while preserving text content and structure.
    """
    
    def __init__(self):
        """Initialize the Markdown processor."""
        self._markdown_available = self._check_markdown_availability()
        
        # Regex patterns for manual markdown processing if library not available
        self.header_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
        self.bold_pattern = re.compile(r'\*\*(.*?)\*\*|__(.*?)__')
        self.italic_pattern = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\([^\)]+\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\([^\)]+\)')
        self.ref_link_pattern = re.compile(r'\[([^\]]+)\]\[[^\]]*\]')
        self.ref_image_pattern = re.compile(r'!\[([^\]]*)\]\[[^\]]*\]')
        self.list_pattern = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
        self.numbered_list_pattern = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
        self.blockquote_pattern = re.compile(r'^>\s*(.+)$', re.MULTILINE)
        self.horizontal_rule_pattern = re.compile(r'^[-*_]{3,}$', re.MULTILINE)
        
        # Whitespace cleanup patterns
        self.whitespace_pattern = re.compile(r'\s+')
        self.multiple_newlines_pattern = re.compile(r'\n\s*\n\s*\n+')
    
    def _check_markdown_availability(self) -> bool:
        """Check if markdown library is available."""
        try:
            import markdown
            return True
        except ImportError:
            logger.warning("markdown library not available. Using manual processing. Install with: pip install markdown")
            return False
    
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports Markdown formats.
        
        Args:
            file_extension: File extension to check
            
        Returns:
            True if Markdown format is supported
        """
        return file_extension.lower() in ['.md', '.markdown', '.mdown', '.mkd']
    
    def process(self, file_path: str) -> str:
        """
        Extract clean text from a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            Extracted plain text content
            
        Raises:
            ValueError: If file processing fails
        """
        try:
            # Read the markdown file
            markdown_content = self._read_markdown_file(file_path)
            
            if self._markdown_available:
                # Use markdown library for conversion
                text_content = self._convert_with_markdown_library(markdown_content)
            else:
                # Use manual conversion
                text_content = self._convert_manually(markdown_content)
            
            # Clean and normalize the text
            cleaned_text = self._clean_text(text_content)
            
            if not cleaned_text.strip():
                raise ValueError("No text content found in Markdown file")
            
            logger.debug(f"Extracted {len(cleaned_text)} characters from {file_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to process Markdown file {file_path}: {e}")
            raise ValueError(f"Markdown processing failed: {e}")
    
    def _read_markdown_file(self, file_path: str) -> str:
        """
        Read Markdown file with encoding detection.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            Markdown content as string
        """
        # Try common encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        # If all encodings fail, try with error handling
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            logger.warning(f"Read {file_path} with UTF-8 and error replacement")
            return content
        except Exception as e:
            raise ValueError(f"Could not read Markdown file {file_path}: {e}")
    
    def _convert_with_markdown_library(self, markdown_content: str) -> str:
        """
        Convert markdown to text using the markdown library.
        
        Args:
            markdown_content: Raw markdown content
            
        Returns:
            Plain text content
        """
        try:
            import markdown
            from bs4 import BeautifulSoup
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['extra', 'codehilite'])
            html_content = md.convert(markdown_content)
            
            # Convert HTML to text using BeautifulSoup if available
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text(separator='\n', strip=True)
            except ImportError:
                # Fallback: simple HTML tag removal
                import re
                html_tag_pattern = re.compile(r'<[^>]+>')
                text_content = html_tag_pattern.sub('', html_content)
            
            return text_content
            
        except Exception as e:
            logger.warning(f"Markdown library conversion failed: {e}. Falling back to manual processing.")
            return self._convert_manually(markdown_content)
    
    def _convert_manually(self, markdown_content: str) -> str:
        """
        Manually convert markdown to text using regex patterns.
        
        Args:
            markdown_content: Raw markdown content
            
        Returns:
            Plain text content
        """
        text = markdown_content
        
        # Remove code blocks first (to avoid processing markdown inside them)
        text = self.code_block_pattern.sub('', text)
        
        # Remove inline code (keep content)
        text = self.inline_code_pattern.sub(r'\1', text)
        
        # Convert headers (remove # symbols)
        text = self.header_pattern.sub(r'\1', text)
        
        # Convert bold and italic (keep text, remove formatting)
        text = self.bold_pattern.sub(lambda m: m.group(1) or m.group(2), text)
        text = self.italic_pattern.sub(lambda m: m.group(1) or m.group(2), text)
        
        # Convert links (keep link text, remove URL)
        text = self.link_pattern.sub(r'\1', text)
        text = self.ref_link_pattern.sub(r'\1', text)
        
        # Convert images (keep alt text, remove ! and brackets)
        text = self.image_pattern.sub(r'\1', text)
        text = self.ref_image_pattern.sub(r'\1', text)
        
        # Convert lists (remove list markers)
        text = self.list_pattern.sub(r'\1', text)
        text = self.numbered_list_pattern.sub(r'\1', text)
        
        # Convert blockquotes (remove > marker)
        text = self.blockquote_pattern.sub(r'\1', text)
        
        # Remove horizontal rules
        text = self.horizontal_rule_pattern.sub('', text)
        
        # Remove any remaining markdown artifacts
        text = self._remove_remaining_markdown_artifacts(text)
        
        return text
    
    def _remove_remaining_markdown_artifacts(self, text: str) -> str:
        """
        Remove any remaining markdown syntax artifacts.
        
        Args:
            text: Text with potential markdown artifacts
            
        Returns:
            Cleaned text
        """
        # Remove table syntax
        text = re.sub(r'\|', ' ', text)
        text = re.sub(r'^[-:|\s]+$', '', text, flags=re.MULTILINE)
        
        # Remove reference-style link definitions (but not the references themselves)
        text = re.sub(r'^\[[^\]]+\]:\s*.+$', '', text, flags=re.MULTILINE)
        
        # Remove HTML comments that might be in markdown
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove escape characters
        text = re.sub(r'\\(.)', r'\1', text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize whitespace within each line
            cleaned_line = self.whitespace_pattern.sub(' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        result = '\n'.join(cleaned_lines)
        
        # Handle multiple consecutive newlines (reduce to double newlines max)
        result = self.multiple_newlines_pattern.sub('\n\n', result)
        
        return result.strip()


class EPUBProcessor(DocumentProcessor):
    """
    EPUB document processor using ebooklib for text extraction.
    
    This processor extracts text content from EPUB files, handling
    chapter organization and metadata while converting HTML content to plain text.
    """
    
    def __init__(self):
        """Initialize the EPUB processor."""
        self._ebooklib_available = self._check_ebooklib_availability()
        self._bs4_available = self._check_beautifulsoup_availability()
        
        # HTML cleaning patterns (reuse from HTMLProcessor)
        self.whitespace_pattern = re.compile(r'\s+')
        self.multiple_newlines_pattern = re.compile(r'\n\s*\n\s*\n+')
    
    def _check_ebooklib_availability(self) -> bool:
        """Check if ebooklib is available."""
        try:
            import ebooklib
            return True
        except ImportError:
            logger.error("ebooklib not available. Install with: pip install ebooklib")
            return False
    
    def _check_beautifulsoup_availability(self) -> bool:
        """Check if BeautifulSoup is available."""
        try:
            import bs4
            return True
        except ImportError:
            logger.warning("BeautifulSoup4 not available. HTML cleaning will be basic. Install with: pip install beautifulsoup4")
            return False
    
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports EPUB formats.
        
        Args:
            file_extension: File extension to check
            
        Returns:
            True if EPUB format is supported
        """
        return file_extension.lower() in ['.epub']
    
    def process(self, file_path: str) -> str:
        """
        Extract clean text from an EPUB file.
        
        Args:
            file_path: Path to the EPUB file
            
        Returns:
            Extracted plain text content
            
        Raises:
            ImportError: If ebooklib is not available
            ValueError: If file processing fails
        """
        if not self._ebooklib_available:
            raise ImportError("ebooklib required for EPUB processing")
        
        try:
            import ebooklib
            from ebooklib import epub
            
            # Read the EPUB file
            book = epub.read_epub(file_path)
            
            # Extract text from all chapters
            text_content = self._extract_text_from_book(book)
            
            # Clean and normalize the text
            cleaned_text = self._clean_text(text_content)
            
            if not cleaned_text.strip():
                raise ValueError("No text content found in EPUB file")
            
            logger.debug(f"Extracted {len(cleaned_text)} characters from {file_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to process EPUB file {file_path}: {e}")
            raise ValueError(f"EPUB processing failed: {e}")
    
    def _extract_text_from_book(self, book) -> str:
        """
        Extract text content from all chapters in the EPUB book.
        
        Args:
            book: EPUB book object
            
        Returns:
            Combined text content from all chapters
        """
        import ebooklib
        from ebooklib import epub
        
        text_parts = []
        
        # Get all items that contain text content
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    # Get the HTML content
                    html_content = item.get_content().decode('utf-8')
                    
                    # Convert HTML to text
                    chapter_text = self._html_to_text(html_content)
                    
                    if chapter_text.strip():
                        text_parts.append(chapter_text)
                        text_parts.append('\n\n')  # Separate chapters
                        
                except Exception as e:
                    logger.warning(f"Failed to extract text from chapter {item.get_name()}: {e}")
                    continue
        
        return ''.join(text_parts)
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML content to plain text.
        
        Args:
            html_content: HTML content string
            
        Returns:
            Plain text content
        """
        if self._bs4_available:
            return self._html_to_text_with_bs4(html_content)
        else:
            return self._html_to_text_basic(html_content)
    
    def _html_to_text_with_bs4(self, html_content: str) -> str:
        """
        Convert HTML to text using BeautifulSoup.
        
        Args:
            html_content: HTML content string
            
        Returns:
            Plain text content
        """
        try:
            from bs4 import BeautifulSoup, Comment
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for tag_name in ['script', 'style', 'meta', 'link', 'noscript']:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Extract text with structure
            text = soup.get_text(separator='\n', strip=True)
            
            return text
            
        except Exception as e:
            logger.warning(f"BeautifulSoup HTML conversion failed: {e}. Using basic conversion.")
            return self._html_to_text_basic(html_content)
    
    def _html_to_text_basic(self, html_content: str) -> str:
        """
        Basic HTML to text conversion using regex.
        
        Args:
            html_content: HTML content string
            
        Returns:
            Plain text content
        """
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # Convert common block elements to newlines
        block_elements = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']
        for element in block_elements:
            html_content = re.sub(f'<{element}[^>]*>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(f'</{element}>', '\n', html_content, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        html_content = self._decode_html_entities(html_content)
        
        return html_content
    
    def _decode_html_entities(self, text: str) -> str:
        """
        Decode common HTML entities.
        
        Args:
            text: Text with HTML entities
            
        Returns:
            Text with decoded entities
        """
        try:
            import html
            return html.unescape(text)
        except ImportError:
            # Manual decoding for common entities
            entities = {
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"',
                '&#39;': "'",
                '&nbsp;': ' ',
            }
            
            for entity, char in entities.items():
                text = text.replace(entity, char)
            
            return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize whitespace within each line
            cleaned_line = self.whitespace_pattern.sub(' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        result = '\n'.join(cleaned_lines)
        
        # Handle multiple consecutive newlines (reduce to double newlines max)
        result = self.multiple_newlines_pattern.sub('\n\n', result)
        
        return result.strip()


class PDFProcessor(DocumentProcessor):
    """
    PDF document processor using PyMuPDF for text extraction with OCR fallback.
    
    This processor extracts text from PDF files using PyMuPDF (fitz) as the primary
    method, with OCR fallback using pytesseract for scanned or low-quality PDFs.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self._fitz_available = self._check_fitz_availability()
        self._tesseract_available = self._check_tesseract_availability()
        self._pillow_available = self._check_pillow_availability()
        
        # Text quality thresholds for OCR fallback
        self.min_text_length = 50  # Minimum characters to consider text extraction successful
        self.min_text_density = 0.1  # Minimum text-to-page ratio
        
        # Regex patterns for text cleaning
        self.whitespace_pattern = re.compile(r'\s+')
        self.multiple_newlines_pattern = re.compile(r'\n\s*\n\s*\n+')
    
    def _check_fitz_availability(self) -> bool:
        """Check if PyMuPDF (fitz) is available."""
        try:
            import fitz
            return True
        except ImportError:
            logger.error("PyMuPDF (fitz) not available. Install with: pip install PyMuPDF")
            return False
    
    def _check_tesseract_availability(self) -> bool:
        """Check if pytesseract is available."""
        try:
            import pytesseract
            # Try to get tesseract version to verify it's properly installed
            pytesseract.get_tesseract_version()
            return True
        except ImportError:
            logger.warning("pytesseract not available. Install with: pip install pytesseract")
            return False
        except Exception as e:
            logger.warning(f"Tesseract OCR not properly configured: {e}")
            return False
    
    def _check_pillow_availability(self) -> bool:
        """Check if Pillow is available for image processing."""
        try:
            from PIL import Image
            return True
        except ImportError:
            logger.warning("Pillow not available. Install with: pip install Pillow")
            return False
    
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this processor supports PDF formats.
        
        Args:
            file_extension: File extension to check
            
        Returns:
            True if PDF format is supported
        """
        return file_extension.lower() in ['.pdf']
    
    def process(self, file_path: str) -> str:
        """
        Extract clean text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted plain text content
            
        Raises:
            ImportError: If PyMuPDF is not available
            ValueError: If file processing fails
        """
        if not self._fitz_available:
            raise ImportError("PyMuPDF (fitz) required for PDF processing")
        
        try:
            # First, try text extraction with PyMuPDF
            text_content = self._extract_text_with_fitz(file_path)
            
            # Assess text quality and use OCR fallback if needed
            if self._should_use_ocr_fallback(text_content, file_path):
                logger.info(f"Text quality low for {file_path}, attempting OCR fallback")
                ocr_text = self._extract_text_with_ocr(file_path)
                if ocr_text and len(ocr_text.strip()) > len(text_content.strip()):
                    text_content = ocr_text
                    logger.info(f"OCR extraction successful for {file_path}")
            
            # Clean and normalize the text
            cleaned_text = self._clean_text(text_content)
            
            if not cleaned_text.strip():
                raise ValueError("No text content found in PDF file")
            
            logger.debug(f"Extracted {len(cleaned_text)} characters from {file_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to process PDF file {file_path}: {e}")
            raise ValueError(f"PDF processing failed: {e}")
    
    def _extract_text_with_fitz(self, file_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            import fitz
        except ImportError:
            logger.error("PyMuPDF (fitz) not available for text extraction")
            return ""
        
        text_parts = []
        
        try:
            # Open the PDF document
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text from the page
                page_text = page.get_text()
                
                if page_text.strip():
                    text_parts.append(page_text)
                    text_parts.append('\n\n')  # Separate pages
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"PyMuPDF text extraction failed for {file_path}: {e}")
            return ""
        
        return ''.join(text_parts)
    
    def _should_use_ocr_fallback(self, text_content: str, file_path: str) -> bool:
        """
        Determine if OCR fallback should be used based on text quality.
        
        Args:
            text_content: Extracted text content
            file_path: Path to the PDF file
            
        Returns:
            True if OCR fallback should be used
        """
        if not self._tesseract_available or not self._pillow_available:
            return False
        
        # Check text length
        if len(text_content.strip()) < self.min_text_length:
            logger.debug(f"Text too short for {file_path}, considering OCR")
            return True
        
        # Check for signs of poor text extraction (lots of garbled characters)
        # Count ratio of alphanumeric characters to total characters
        alphanumeric_chars = sum(1 for c in text_content if c.isalnum())
        total_chars = len(text_content.strip())
        
        if total_chars > 0:
            text_quality_ratio = alphanumeric_chars / total_chars
            if text_quality_ratio < self.min_text_density:
                logger.debug(f"Low text quality ratio ({text_quality_ratio:.2f}) for {file_path}, considering OCR")
                return True
        
        return False
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """
        Extract text from PDF using OCR as fallback.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            OCR-extracted text content
        """
        if not self._tesseract_available or not self._pillow_available:
            logger.warning("OCR dependencies not available, skipping OCR fallback")
            return ""
        
        try:
            import fitz
            import pytesseract
            from PIL import Image
            import io
            
            text_parts = []
            
            # Open the PDF document
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    
                    # Convert page to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Perform OCR
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    
                    if page_text.strip():
                        text_parts.append(page_text)
                        text_parts.append('\n\n')  # Separate pages
                    
                except Exception as e:
                    logger.warning(f"OCR failed for page {page_num} in {file_path}: {e}")
                    continue
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"OCR text extraction failed for {file_path}: {e}")
            return ""
        
        return ''.join(text_parts)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize whitespace within each line
            cleaned_line = self.whitespace_pattern.sub(' ', line).strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join lines with single newlines
        result = '\n'.join(cleaned_lines)
        
        # Handle multiple consecutive newlines (reduce to double newlines max)
        result = self.multiple_newlines_pattern.sub('\n\n', result)
        
        return result.strip()


class IngestionPipeline:
    """
    Orchestrates multi-format document processing across multiple files.
    
    This class coordinates the processing of various document formats,
    handles errors gracefully, and provides comprehensive statistics.
    """
    
    def __init__(self, output_dir: str = "data/cleaned"):
        """
        Initialize the ingestion pipeline.
        
        Args:
            output_dir: Directory to save processed text files
        """
        self.output_dir = Path(output_dir)
        self.processors: Dict[str, DocumentProcessor] = {}
        self.supported_formats: Set[str] = set()
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processors (will be implemented in subsequent tasks)
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize all available document processors."""
        # Initialize HTML processor
        try:
            html_processor = HTMLProcessor()
            self.register_processor(html_processor)
        except ImportError as e:
            logger.warning(f"HTML processor not available: {e}")
        
        # Initialize Markdown processor
        try:
            markdown_processor = MarkdownProcessor()
            self.register_processor(markdown_processor)
        except Exception as e:
            logger.warning(f"Markdown processor not available: {e}")
        
        # Initialize EPUB processor
        try:
            epub_processor = EPUBProcessor()
            self.register_processor(epub_processor)
        except ImportError as e:
            logger.warning(f"EPUB processor not available: {e}")
        
        # Initialize PDF processor
        try:
            pdf_processor = PDFProcessor()
            self.register_processor(pdf_processor)
            logger.debug("PDF processor initialized successfully")
        except Exception as e:
            logger.warning(f"PDF processor not available: {e}")
        
        # Additional processors will be added in subsequent tasks
        logger.info("Initialized available document processors")
    
    def register_processor(self, processor: DocumentProcessor):
        """
        Register a document processor for specific file formats.
        
        Args:
            processor: DocumentProcessor instance to register
        """
        # Determine supported formats for this processor
        common_formats = ['.html', '.htm', '.md', '.epub', '.pdf', '.txt']
        
        for fmt in common_formats:
            if processor.supports_format(fmt):
                self.processors[fmt] = processor
                self.supported_formats.add(fmt)
                logger.debug(f"Registered processor for {fmt} format")
    
    def get_processor(self, file_extension: str) -> Optional[DocumentProcessor]:
        """
        Get the appropriate processor for a file extension.
        
        Args:
            file_extension: File extension (e.g., '.html', '.pdf')
            
        Returns:
            DocumentProcessor instance or None if format not supported
        """
        return self.processors.get(file_extension.lower())
    
    def process_file(self, file_path: str) -> Optional[str]:
        """
        Process a single file and extract text content.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Extracted text content or None if processing failed
        """
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            processor = self.get_processor(extension)
            if not processor:
                raise ValueError(f"No processor available for format: {extension}")
            
            if not processor.validate_file(file_path):
                raise ValueError(f"File validation failed: {file_path}")
            
            logger.debug(f"Processing file: {file_path}")
            text_content = processor.process(file_path)
            
            if not text_content or not text_content.strip():
                logger.warning(f"No text content extracted from: {file_path}")
                return None
            
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return None
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None) -> ProcessingStats:
        """
        Process all supported files in a directory.
        
        Args:
            input_dir: Directory containing files to process
            output_dir: Optional output directory (uses default if not specified)
            
        Returns:
            ProcessingStats with detailed processing information
        """
        start_time = time.time()
        stats = ProcessingStats()
        
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            error = ProcessingError(
                file_path=input_dir,
                error_type="DirectoryError",
                message="Input directory does not exist or is not a directory",
                timestamp=time.time()
            )
            stats.errors.append(error)
            return stats
        
        # Find all supported files
        supported_files = []
        for file_path in input_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                supported_files.append(file_path)
        
        logger.info(f"Found {len(supported_files)} supported files to process")
        
        # Process each file
        for file_path in supported_files:
            try:
                # Get file size for statistics
                file_size = file_path.stat().st_size
                stats.total_size_bytes += file_size
                
                # Process the file
                text_content = self.process_file(str(file_path))
                
                if text_content:
                    # Save processed text
                    output_filename = self._generate_output_filename(file_path)
                    output_path = self.output_dir / output_filename
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    
                    stats.files_processed += 1
                    logger.debug(f"Successfully processed: {file_path}")
                else:
                    stats.files_failed += 1
                    error = ProcessingError(
                        file_path=str(file_path),
                        error_type="ProcessingError",
                        message="No text content extracted",
                        timestamp=time.time()
                    )
                    stats.errors.append(error)
                    
            except Exception as e:
                stats.files_failed += 1
                error = ProcessingError(
                    file_path=str(file_path),
                    error_type=type(e).__name__,
                    message=str(e),
                    timestamp=time.time()
                )
                stats.errors.append(error)
                logger.error(f"Error processing {file_path}: {e}")
        
        stats.processing_time_seconds = time.time() - start_time
        
        logger.info(f"Processing complete. Processed: {stats.files_processed}, "
                   f"Failed: {stats.files_failed}, Time: {stats.processing_time_seconds:.2f}s")
        
        return stats
    
    def _generate_output_filename(self, input_path: Path) -> str:
        """
        Generate a standardized output filename for processed text.
        
        Args:
            input_path: Original file path
            
        Returns:
            Standardized output filename
        """
        # Create a clean filename based on the original, including extension to avoid conflicts
        base_name = input_path.stem
        extension = input_path.suffix.lower().lstrip('.')  # Remove the dot and normalize case
        
        # Replace any problematic characters in base name
        clean_base = "".join(c for c in base_name if c.isalnum() or c in "._-")
        clean_ext = "".join(c for c in extension if c.isalnum())
        
        # Combine base name with original extension to ensure uniqueness
        if clean_ext:
            return f"{clean_base}_{clean_ext}.txt"
        else:
            return f"{clean_base}.txt"
    
    def get_supported_formats(self) -> Set[str]:
        """
        Get the set of supported file formats.
        
        Returns:
            Set of supported file extensions
        """
        return self.supported_formats.copy()
    
    def get_processing_summary(self, stats: ProcessingStats) -> Dict[str, Any]:
        """
        Generate a human-readable summary of processing results.
        
        Args:
            stats: ProcessingStats from a processing operation
            
        Returns:
            Dictionary with summary information
        """
        total_files = stats.files_processed + stats.files_failed
        success_rate = (stats.files_processed / total_files * 100) if total_files > 0 else 0
        
        return {
            "total_files": total_files,
            "successful": stats.files_processed,
            "failed": stats.files_failed,
            "success_rate_percent": round(success_rate, 2),
            "total_size_mb": round(stats.total_size_bytes / (1024 * 1024), 2),
            "processing_time_seconds": round(stats.processing_time_seconds, 2),
            "files_per_second": round(total_files / stats.processing_time_seconds, 2) if stats.processing_time_seconds > 0 else 0,
            "error_types": list(set(error.error_type for error in stats.errors))
        }