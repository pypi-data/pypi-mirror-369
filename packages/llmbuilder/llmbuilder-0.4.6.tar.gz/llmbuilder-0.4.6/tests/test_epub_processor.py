"""
Unit tests for EPUB text extraction processor.

This module tests the EPUBProcessor class functionality including
text extraction, chapter handling, and error scenarios.
"""

import pytest
import tempfile
import os
from pathlib import Path

from llmbuilder.data.ingest import EPUBProcessor


class TestEPUBProcessor:
    """Test cases for EPUB text extraction."""
    
    def setup_method(self):
        """Set up test environment."""
        self.processor = EPUBProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_supports_format(self):
        """Test format support detection."""
        assert self.processor.supports_format('.epub') is True
        assert self.processor.supports_format('.EPUB') is True
        assert self.processor.supports_format('.txt') is False
        assert self.processor.supports_format('.pdf') is False
        assert self.processor.supports_format('.html') is False
    
    def test_html_to_text_basic(self):
        """Test basic HTML to text conversion."""
        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Chapter Title</h1>
            <p>This is a paragraph with <strong>bold</strong> text.</p>
            <p>Another paragraph here.</p>
        </body>
        </html>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Chapter Title" in result
        assert "This is a paragraph with bold text." in result
        assert "Another paragraph here." in result
        # HTML tags should be removed
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "<strong>" not in result
    
    def test_html_entity_decoding(self):
        """Test HTML entity decoding."""
        text_with_entities = "Text with &amp; &lt; &gt; &quot; &#39; &nbsp; entities"
        
        result = self.processor._decode_html_entities(text_with_entities)
        
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert '"' in result
        assert "'" in result
        assert " " in result  # nbsp should become space
        # Entities should be decoded
        assert "&amp;" not in result
        assert "&lt;" not in result
        assert "&gt;" not in result
    
    def test_html_script_and_style_removal(self):
        """Test that scripts and styles are removed from HTML."""
        html_content = """
        <html>
        <head>
            <style>body { color: red; }</style>
            <script>console.log("test");</script>
        </head>
        <body>
            <p>Visible content</p>
            <script>alert("another script");</script>
        </body>
        </html>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Visible content" in result
        assert "color: red" not in result
        assert "console.log" not in result
        assert "alert" not in result
    
    def test_html_comments_removal(self):
        """Test that HTML comments are removed."""
        html_content = """
        <html>
        <body>
            <!-- This is a comment -->
            <p>Visible text</p>
            <!-- Another comment -->
        </body>
        </html>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Visible text" in result
        assert "This is a comment" not in result
        assert "Another comment" not in result
    
    def test_text_cleaning(self):
        """Test text cleaning and normalization."""
        raw_text = """
        
        Line 1   with   extra   spaces
        
        
        Line 2
        
        Line 3
        
        
        """
        
        result = self.processor._clean_text(raw_text)
        
        # Should normalize whitespace and remove excessive newlines
        assert "Line 1 with extra spaces" in result
        assert "Line 2" in result
        assert "Line 3" in result
        # Should not have excessive whitespace
        assert "   " not in result
        # Should not start or end with whitespace
        assert not result.startswith(' ')
        assert not result.endswith(' ')
    
    def test_file_validation(self):
        """Test file validation functionality."""
        # Create a dummy file for testing
        test_file = os.path.join(self.temp_dir, "test.epub")
        with open(test_file, 'w') as f:
            f.write("dummy content")
        
        assert self.processor.validate_file(test_file) is True
        assert self.processor.validate_file("non_existent.epub") is False
    
    @pytest.mark.skipif(True, reason="Requires ebooklib dependency and sample EPUB file")
    def test_epub_processing_with_real_file(self):
        """Test processing a real EPUB file."""
        # This test would require a sample EPUB file and ebooklib
        # Skipped by default to avoid dependency issues
        pass
    
    @pytest.mark.skipif(True, reason="Requires ebooklib to be unavailable")
    def test_missing_ebooklib_dependency(self):
        """Test behavior when ebooklib is not available."""
        # This test would need to mock the import failure
        # Skipped by default as it requires special setup
        pass
    
    def test_html_block_elements_conversion(self):
        """Test that block elements are converted to newlines."""
        html_content = """
        <div>Division content</div>
        <p>Paragraph content</p>
        <h1>Header content</h1>
        <li>List item</li>
        <br>
        More content
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Division content" in result
        assert "Paragraph content" in result
        assert "Header content" in result
        assert "List item" in result
        assert "More content" in result
        
        # Should have some structure (newlines)
        lines = result.strip().split('\n')
        assert len(lines) > 1
    
    def test_nested_html_elements(self):
        """Test handling of nested HTML elements."""
        html_content = """
        <div>
            <h2>Section Title</h2>
            <div>
                <p>Nested paragraph with <em>emphasis</em> and <strong>strong</strong> text.</p>
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                </ul>
            </div>
        </div>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Section Title" in result
        assert "emphasis" in result
        assert "strong" in result
        assert "List item 1" in result
        assert "List item 2" in result
        # HTML tags should be removed
        assert "<div>" not in result
        assert "<em>" not in result
        assert "<strong>" not in result
    
    def test_empty_html_content(self):
        """Test handling of empty HTML content."""
        html_content = "<html><head></head><body></body></html>"
        
        result = self.processor._html_to_text_basic(html_content)
        
        # Should return empty or minimal content
        assert len(result.strip()) == 0
    
    def test_html_with_special_characters(self):
        """Test handling of HTML with special characters."""
        html_content = """
        <html>
        <body>
            <p>Special characters: &amp; &lt; &gt; &quot; &#39;</p>
            <p>Unicode: café naïve résumé</p>
        </body>
        </html>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert '"' in result
        assert "'" in result
        assert "café" in result
        assert "naïve" in result
        assert "résumé" in result
    
    def test_multiple_chapters_simulation(self):
        """Test handling multiple chapters (simulated)."""
        # Simulate what would happen with multiple chapters
        chapter1_html = "<html><body><h1>Chapter 1</h1><p>Content of chapter 1.</p></body></html>"
        chapter2_html = "<html><body><h1>Chapter 2</h1><p>Content of chapter 2.</p></body></html>"
        
        text1 = self.processor._html_to_text_basic(chapter1_html)
        text2 = self.processor._html_to_text_basic(chapter2_html)
        
        # Simulate combining chapters
        combined_text = text1 + '\n\n' + text2
        cleaned_text = self.processor._clean_text(combined_text)
        
        assert "Chapter 1" in cleaned_text
        assert "Content of chapter 1" in cleaned_text
        assert "Chapter 2" in cleaned_text
        assert "Content of chapter 2" in cleaned_text
    
    def test_html_tables_handling(self):
        """Test handling of HTML tables."""
        html_content = """
        <table>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
            <tr>
                <td>Cell 1</td>
                <td>Cell 2</td>
            </tr>
        </table>
        """
        
        result = self.processor._html_to_text_basic(html_content)
        
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
        # Table tags should be removed
        assert "<table>" not in result
        assert "<tr>" not in result
        assert "<td>" not in result
    
    def test_processor_availability_checks(self):
        """Test that availability checks work correctly."""
        # These should not raise exceptions
        ebooklib_available = self.processor._check_ebooklib_availability()
        bs4_available = self.processor._check_beautifulsoup_availability()
        
        # Should return boolean values
        assert isinstance(ebooklib_available, bool)
        assert isinstance(bs4_available, bool)