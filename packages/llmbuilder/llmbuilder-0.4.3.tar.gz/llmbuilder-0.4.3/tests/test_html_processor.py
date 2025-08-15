"""
Unit tests for HTML text extraction processor.

This module tests the HTMLProcessor class functionality including
text extraction, encoding handling, and error scenarios.
"""

import pytest
import tempfile
import os
from pathlib import Path

from llmbuilder.data.ingest import HTMLProcessor


class TestHTMLProcessor:
    """Test cases for HTML text extraction."""
    
    def setup_method(self):
        """Set up test environment."""
        self.processor = HTMLProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_html_file(self, content: str, filename: str = "test.html") -> str:
        """Create a temporary HTML file with given content."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_supports_format(self):
        """Test format support detection."""
        assert self.processor.supports_format('.html') is True
        assert self.processor.supports_format('.htm') is True
        assert self.processor.supports_format('.HTML') is True
        assert self.processor.supports_format('.txt') is False
        assert self.processor.supports_format('.pdf') is False
    
    def test_simple_html_extraction(self):
        """Test extraction from simple HTML."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Main Title</h1>
            <p>This is a paragraph with some text.</p>
            <p>Another paragraph here.</p>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "Main Title" in result
        assert "This is a paragraph with some text." in result
        assert "Another paragraph here." in result
        assert "<html>" not in result
        assert "<p>" not in result
    
    def test_html_with_scripts_and_styles(self):
        """Test that scripts and styles are removed."""
        html_content = """
        <html>
        <head>
            <style>
                body { color: red; }
            </style>
            <script>
                console.log("This should not appear");
            </script>
        </head>
        <body>
            <p>Visible content</p>
            <script>alert("Another script");</script>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "Visible content" in result
        assert "color: red" not in result
        assert "console.log" not in result
        assert "alert" not in result
    
    def test_html_with_comments(self):
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
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "Visible text" in result
        assert "This is a comment" not in result
        assert "Another comment" not in result
    
    def test_html_with_nested_elements(self):
        """Test extraction from nested HTML elements."""
        html_content = """
        <html>
        <body>
            <div>
                <h2>Section Title</h2>
                <div>
                    <p>Nested paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
                    <ul>
                        <li>List item 1</li>
                        <li>List item 2</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "Section Title" in result
        assert "bold text" in result
        assert "italic text" in result
        assert "List item 1" in result
        assert "List item 2" in result
    
    def test_malformed_html(self):
        """Test handling of malformed HTML."""
        html_content = """
        <html>
        <body>
            <p>Unclosed paragraph
            <div>Missing closing div
            <p>Another paragraph</p>
        </body>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        # BeautifulSoup should handle malformed HTML gracefully
        assert "Unclosed paragraph" in result
        assert "Another paragraph" in result
    
    def test_empty_html(self):
        """Test handling of empty or minimal HTML."""
        html_content = """
        <html>
        <head></head>
        <body></body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        
        # Should raise ValueError for no content
        with pytest.raises(ValueError, match="No text content found"):
            self.processor.process(file_path)
    
    def test_html_with_special_characters(self):
        """Test handling of special characters and entities."""
        html_content = """
        <html>
        <body>
            <p>Special characters: &amp; &lt; &gt; &quot; &#39;</p>
            <p>Unicode: café naïve résumé</p>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert "café" in result
        assert "naïve" in result
        assert "résumé" in result
    
    def test_encoding_handling(self):
        """Test handling of different encodings."""
        # Test with UTF-8 BOM
        html_content = """
        <html>
        <body>
            <p>UTF-8 content with special chars: ñáéíóú</p>
        </body>
        </html>
        """
        
        file_path = os.path.join(self.temp_dir, "utf8_test.html")
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(html_content)
        
        result = self.processor.process(file_path)
        assert "ñáéíóú" in result
    
    def test_large_html_document(self):
        """Test processing of larger HTML documents."""
        # Create a larger HTML document
        html_content = """
        <html>
        <head><title>Large Document</title></head>
        <body>
        """
        
        # Add many paragraphs
        for i in range(100):
            html_content += f"<p>This is paragraph number {i} with some content.</p>\n"
        
        html_content += """
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "paragraph number 0" in result
        assert "paragraph number 99" in result
        assert len(result) > 1000  # Should be substantial content
    
    def test_html_with_tables(self):
        """Test extraction from HTML tables."""
        html_content = """
        <html>
        <body>
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
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
    
    def test_file_validation(self):
        """Test file validation functionality."""
        # Test with existing file
        html_content = "<html><body><p>Test</p></body></html>"
        file_path = self._create_html_file(html_content)
        assert self.processor.validate_file(file_path) is True
        
        # Test with non-existent file
        assert self.processor.validate_file("non_existent.html") is False
    
    @pytest.mark.skipif(True, reason="Requires BeautifulSoup4 to be unavailable")
    def test_missing_beautifulsoup_dependency(self):
        """Test behavior when BeautifulSoup is not available."""
        # This test would need to mock the import failure
        # Skipped by default as it requires special setup
        pass
    
    def test_whitespace_normalization(self):
        """Test that whitespace is properly normalized."""
        html_content = """
        <html>
        <body>
            <p>Text   with    multiple     spaces</p>
            <p>
                Text
                with
                newlines
            </p>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        # Multiple spaces should be normalized to single spaces
        assert "multiple     spaces" not in result
        assert "multiple spaces" in result or "Text with multiple spaces" in result
    
    def test_block_element_structure_preservation(self):
        """Test that block elements create appropriate text structure."""
        html_content = """
        <html>
        <body>
            <h1>Title</h1>
            <p>First paragraph</p>
            <p>Second paragraph</p>
            <div>Division content</div>
        </body>
        </html>
        """
        
        file_path = self._create_html_file(html_content)
        result = self.processor.process(file_path)
        
        # Should have some structure (newlines between blocks)
        lines = result.split('\n')
        assert len(lines) > 1  # Should have multiple lines
        
        # Content should be present
        assert "Title" in result
        assert "First paragraph" in result
        assert "Second paragraph" in result
        assert "Division content" in result