"""
Unit tests for Markdown text extraction processor.

This module tests the MarkdownProcessor class functionality including
text extraction, markdown syntax removal, and error scenarios.
"""

import pytest
import tempfile
import os
from pathlib import Path

from llmbuilder.data.ingest import MarkdownProcessor


class TestMarkdownProcessor:
    """Test cases for Markdown text extraction."""
    
    def setup_method(self):
        """Set up test environment."""
        self.processor = MarkdownProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_markdown_file(self, content: str, filename: str = "test.md") -> str:
        """Create a temporary Markdown file with given content."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_supports_format(self):
        """Test format support detection."""
        assert self.processor.supports_format('.md') is True
        assert self.processor.supports_format('.markdown') is True
        assert self.processor.supports_format('.mdown') is True
        assert self.processor.supports_format('.mkd') is True
        assert self.processor.supports_format('.MD') is True
        assert self.processor.supports_format('.txt') is False
        assert self.processor.supports_format('.html') is False
    
    def test_simple_markdown_extraction(self):
        """Test extraction from simple Markdown."""
        markdown_content = """
# Main Title

This is a paragraph with some text.

## Subtitle

Another paragraph here with **bold text** and *italic text*.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Main Title" in result
        assert "This is a paragraph with some text." in result
        assert "Subtitle" in result
        assert "bold text" in result
        assert "italic text" in result
        # Markdown syntax should be removed
        assert "##" not in result
        assert "**" not in result
        assert "*italic*" not in result
    
    def test_headers_conversion(self):
        """Test that headers are converted properly."""
        markdown_content = """
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Header 3" in result
        assert "Header 4" in result
        assert "Header 5" in result
        assert "Header 6" in result
        # Hash symbols should be removed
        assert "#" not in result
    
    def test_lists_conversion(self):
        """Test that lists are converted properly."""
        markdown_content = """
Unordered list:
- Item 1
- Item 2
- Item 3

Ordered list:
1. First item
2. Second item
3. Third item

Mixed list:
* Bullet item
+ Plus item
- Dash item
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result
        assert "First item" in result
        assert "Second item" in result
        assert "Third item" in result
        assert "Bullet item" in result
        assert "Plus item" in result
        assert "Dash item" in result
        # List markers should be removed
        assert "- Item" not in result
        assert "1. First" not in result
    
    def test_links_and_images_conversion(self):
        """Test that links and images are converted properly."""
        markdown_content = """
Here is a [link to example](https://example.com) in text.

Here is an image: ![Alt text](image.jpg)

Reference style [link][1] and ![image][2].

[1]: https://example.com
[2]: image.jpg
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        print(f"DEBUG: Result = {repr(result)}")
        
        assert "link to example" in result
        assert "Alt text" in result
        # URLs and markdown syntax should be removed
        assert "https://example.com" not in result
        assert "![" not in result
        assert "](" not in result
        assert "image.jpg" not in result
    
    def test_code_blocks_conversion(self):
        """Test that code blocks are handled properly."""
        markdown_content = """
Here is some inline `code` in text.

Here is a code block:
```python
def hello():
    print("Hello, world!")
```

Another code block:
```
Some plain text code
```
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "code" in result
        # Code block content should be preserved but backticks removed
        assert "```" not in result
        # The actual code content handling may vary based on implementation
    
    def test_blockquotes_conversion(self):
        """Test that blockquotes are converted properly."""
        markdown_content = """
Normal paragraph.

> This is a blockquote.
> It can span multiple lines.

> Another blockquote here.

Back to normal text.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "This is a blockquote." in result
        assert "It can span multiple lines." in result
        assert "Another blockquote here." in result
        # Blockquote markers should be removed
        assert "> This" not in result
    
    def test_emphasis_conversion(self):
        """Test that emphasis (bold/italic) is converted properly."""
        markdown_content = """
This has **bold text** and *italic text*.

This has __bold text__ and _italic text_.

This has ***bold and italic*** text.

This has ~~strikethrough~~ text.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "bold text" in result
        assert "italic text" in result
        # Emphasis markers should be removed
        assert "**bold**" not in result
        assert "*italic*" not in result
        assert "__bold__" not in result
        assert "_italic_" not in result
    
    def test_tables_conversion(self):
        """Test that tables are handled properly."""
        markdown_content = """
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
        # Table syntax should be removed
        assert "|" not in result or result.count("|") < 5  # Some | might remain as text
    
    def test_horizontal_rules_conversion(self):
        """Test that horizontal rules are removed."""
        markdown_content = """
Text before rule.

---

Text after rule.

***

More text.

___

Final text.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Text before rule." in result
        assert "Text after rule." in result
        assert "More text." in result
        assert "Final text." in result
        # Horizontal rules should be removed
        assert "---" not in result
        assert "***" not in result
        assert "___" not in result
    
    def test_mixed_markdown_content(self):
        """Test complex markdown with mixed elements."""
        markdown_content = """
# Document Title

This is an introduction paragraph with **bold** and *italic* text.

## Section 1

Here's a list:
- First item with [a link](https://example.com)
- Second item with `inline code`
- Third item

### Subsection

> This is a blockquote with **bold text** inside.

```python
# This is a code block
def example():
    return "Hello"
```

## Section 2

| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |

---

Final paragraph.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        # Check that content is preserved
        assert "Document Title" in result
        assert "introduction paragraph" in result
        assert "bold" in result
        assert "italic" in result
        assert "Section 1" in result
        assert "First item" in result
        assert "a link" in result
        assert "inline code" in result
        assert "This is a blockquote" in result
        assert "John" in result
        assert "Jane" in result
        assert "Final paragraph" in result
        
        # Check that markdown syntax is removed
        assert "#" not in result
        assert "**" not in result
        assert "*italic*" not in result
        assert "- First" not in result
        assert "> This" not in result
        assert "```" not in result
        assert "|---" not in result
    
    def test_empty_markdown(self):
        """Test handling of empty markdown."""
        markdown_content = ""
        
        file_path = self._create_markdown_file(markdown_content)
        
        with pytest.raises(ValueError, match="No text content found"):
            self.processor.process(file_path)
    
    def test_whitespace_only_markdown(self):
        """Test handling of whitespace-only markdown."""
        markdown_content = """
        
        
        
        """
        
        file_path = self._create_markdown_file(markdown_content)
        
        with pytest.raises(ValueError, match="No text content found"):
            self.processor.process(file_path)
    
    def test_markdown_with_html(self):
        """Test handling of markdown with embedded HTML."""
        markdown_content = """
# Title

This is a paragraph with <strong>HTML bold</strong> and <em>HTML italic</em>.

<div>
This is HTML content.
</div>

Back to markdown **bold**.
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Title" in result
        assert "HTML bold" in result
        assert "HTML italic" in result
        assert "This is HTML content." in result
        assert "bold" in result
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        markdown_content = """
# Special Characters

Text with special chars: & < > " ' 

Unicode: café naïve résumé

Escaped characters: \\* \\# \\[
        """
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Special Characters" in result
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert "café" in result
        assert "naïve" in result
        assert "résumé" in result
        assert "*" in result  # Should be unescaped
        assert "#" in result  # Should be unescaped
    
    def test_encoding_handling(self):
        """Test handling of different encodings."""
        markdown_content = """
# UTF-8 Content

Content with special characters: ñáéíóú

Chinese: 你好世界

Emoji: 🚀 🎉 ✨
        """
        
        file_path = os.path.join(self.temp_dir, "utf8_test.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        result = self.processor.process(file_path)
        
        assert "UTF-8 Content" in result
        assert "ñáéíóú" in result
        assert "你好世界" in result
        assert "🚀" in result
    
    def test_file_validation(self):
        """Test file validation functionality."""
        # Test with existing file
        markdown_content = "# Test\n\nContent here."
        file_path = self._create_markdown_file(markdown_content)
        assert self.processor.validate_file(file_path) is True
        
        # Test with non-existent file
        assert self.processor.validate_file("non_existent.md") is False
    
    def test_large_markdown_document(self):
        """Test processing of larger markdown documents."""
        # Create a larger markdown document
        markdown_content = "# Large Document\n\n"
        
        # Add many sections
        for i in range(50):
            markdown_content += f"## Section {i}\n\n"
            markdown_content += f"This is section number {i} with some **bold** content.\n\n"
            markdown_content += f"- List item 1 for section {i}\n"
            markdown_content += f"- List item 2 for section {i}\n\n"
        
        file_path = self._create_markdown_file(markdown_content)
        result = self.processor.process(file_path)
        
        assert "Large Document" in result
        assert "Section 0" in result
        assert "Section 49" in result
        assert len(result) > 1000  # Should be substantial content
        # Markdown syntax should be removed
        assert "##" not in result
        assert "**" not in result
        assert "- List" not in result