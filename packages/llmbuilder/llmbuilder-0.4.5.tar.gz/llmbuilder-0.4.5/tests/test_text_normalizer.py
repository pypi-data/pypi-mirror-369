"""
Unit tests for TextNormalizer class.

This module tests the text normalization functionality including
line normalization, semantic comparison preparation, and hash computation.
"""

import pytest
import hashlib
from llmbuilder.data.dedup import TextNormalizer


class TestTextNormalizer:
    """Test cases for text normalization utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.normalizer = TextNormalizer()
    
    def test_normalize_line_basic(self):
        """Test basic line normalization."""
        # Test basic normalization
        text = "  Hello   World  "
        result = self.normalizer.normalize_line(text)
        assert result == "hello world"
        
        # Test empty string
        assert self.normalizer.normalize_line("") == ""
        assert self.normalizer.normalize_line(None) == ""
    
    def test_normalize_line_unicode(self):
        """Test Unicode normalization."""
        # Test Unicode normalization (NFKC)
        text = "café naïve résumé"  # Contains accented characters
        result = self.normalizer.normalize_line(text)
        assert "café" in result
        assert "naïve" in result
        assert "résumé" in result
        
        # Test Unicode compatibility characters
        text = "ﬁle"  # Contains ligature fi (U+FB01)
        result = self.normalizer.normalize_line(text)
        assert "file" in result  # Should be normalized to separate characters
    
    def test_normalize_line_case_conversion(self):
        """Test case conversion."""
        text = "Hello WORLD Mixed CaSe"
        result = self.normalizer.normalize_line(text)
        assert result == "hello world mixed case"
    
    def test_normalize_line_whitespace_handling(self):
        """Test whitespace normalization."""
        # Multiple spaces
        text = "word1    word2     word3"
        result = self.normalizer.normalize_line(text)
        assert result == "word1 word2 word3"
        
        # Mixed whitespace (tabs, newlines)
        text = "word1\t\tword2\n\nword3"
        result = self.normalizer.normalize_line(text)
        assert result == "word1 word2 word3"
        
        # Leading/trailing whitespace
        text = "\n\t  Hello World  \t\n"
        result = self.normalizer.normalize_line(text)
        assert result == "hello world"
    
    def test_normalize_for_semantic_comparison_basic(self):
        """Test basic semantic normalization."""
        text = "Hello, World! How are you?"
        result = self.normalizer.normalize_for_semantic_comparison(text)
        
        # Should be lowercase
        assert result.islower()
        
        # Should not contain punctuation
        assert "," not in result
        assert "!" not in result
        assert "?" not in result
        
        # Should contain the words
        assert "hello" in result
        assert "world" in result
        assert "how" in result
        assert "are" in result
        assert "you" in result
    
    def test_normalize_for_semantic_comparison_numbers(self):
        """Test number normalization in semantic comparison."""
        text = "I have 5 apples and 10 oranges, total 15 fruits."
        result = self.normalizer.normalize_for_semantic_comparison(text)
        
        # Numbers should be replaced with NUM
        assert "5" not in result
        assert "10" not in result
        assert "15" not in result
        assert "NUM" in result
        
        # Text should remain
        assert "apples" in result
        assert "oranges" in result
        assert "fruits" in result
    
    def test_normalize_for_semantic_comparison_punctuation(self):
        """Test punctuation removal in semantic comparison."""
        text = "Hello! How are you? I'm fine, thanks."
        result = self.normalizer.normalize_for_semantic_comparison(text)
        
        # Punctuation should be removed
        assert "!" not in result
        assert "?" not in result
        assert "," not in result
        assert "'" not in result
        
        # Words should remain
        assert "hello" in result
        assert "how" in result
        assert "fine" in result
        assert "thanks" in result
    
    def test_compute_line_hash_sha256(self):
        """Test SHA-256 hash computation."""
        text = "Hello World"
        result = self.normalizer.compute_line_hash(text, "sha256")
        
        # Should be a valid SHA-256 hash (64 hex characters)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)
        
        # Same input should produce same hash
        result2 = self.normalizer.compute_line_hash(text, "sha256")
        assert result == result2
        
        # Different input should produce different hash
        result3 = self.normalizer.compute_line_hash("Different text", "sha256")
        assert result != result3
    
    def test_compute_line_hash_md5(self):
        """Test MD5 hash computation."""
        text = "Hello World"
        result = self.normalizer.compute_line_hash(text, "md5")
        
        # Should be a valid MD5 hash (32 hex characters)
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)
        
        # Same input should produce same hash
        result2 = self.normalizer.compute_line_hash(text, "md5")
        assert result == result2
    
    def test_compute_line_hash_normalization_consistency(self):
        """Test that hash computation uses normalization."""
        # These should produce the same hash due to normalization
        text1 = "  Hello   World  "
        text2 = "hello world"
        text3 = "HELLO WORLD"
        
        hash1 = self.normalizer.compute_line_hash(text1)
        hash2 = self.normalizer.compute_line_hash(text2)
        hash3 = self.normalizer.compute_line_hash(text3)
        
        assert hash1 == hash2 == hash3
    
    def test_compute_line_hash_unsupported_algorithm(self):
        """Test error handling for unsupported hash algorithms."""
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            self.normalizer.compute_line_hash("test", "unsupported")
    
    def test_normalization_edge_cases(self):
        """Test edge cases in normalization."""
        # Empty strings
        assert self.normalizer.normalize_line("") == ""
        assert self.normalizer.normalize_for_semantic_comparison("") == ""
        
        # Only whitespace
        assert self.normalizer.normalize_line("   \t\n   ") == ""
        assert self.normalizer.normalize_for_semantic_comparison("   \t\n   ") == ""
        
        # Only punctuation
        result = self.normalizer.normalize_for_semantic_comparison("!@#$%^&*()")
        assert result.strip() == ""
        
        # Only numbers
        result = self.normalizer.normalize_for_semantic_comparison("123 456 789")
        assert "NUM" in result
        assert "123" not in result
    
    def test_normalization_consistency(self):
        """Test that normalization is consistent across calls."""
        text = "Hello, World! 123"
        
        # Multiple calls should produce same result
        result1 = self.normalizer.normalize_line(text)
        result2 = self.normalizer.normalize_line(text)
        assert result1 == result2
        
        semantic1 = self.normalizer.normalize_for_semantic_comparison(text)
        semantic2 = self.normalizer.normalize_for_semantic_comparison(text)
        assert semantic1 == semantic2
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        # Test various special characters
        text = "Hello@world.com #hashtag $money 50% off"
        result = self.normalizer.normalize_line(text)
        
        # Should preserve special characters in line normalization
        assert "@" in result
        assert "." in result
        assert "#" in result
        assert "$" in result
        assert "%" in result
        
        # But remove them in semantic normalization
        semantic_result = self.normalizer.normalize_for_semantic_comparison(text)
        assert "@" not in semantic_result
        assert "#" not in semantic_result
        assert "$" not in semantic_result
        assert "%" not in semantic_result
    
    def test_multilingual_text(self):
        """Test normalization with multilingual text."""
        # Test with various languages
        texts = [
            "Hello world",  # English
            "Hola mundo",   # Spanish
            "Bonjour monde", # French
            "你好世界",      # Chinese
            "こんにちは世界",  # Japanese
            "Привет мир",   # Russian
        ]
        
        for text in texts:
            # Should not raise exceptions
            normalized = self.normalizer.normalize_line(text)
            assert isinstance(normalized, str)
            
            semantic = self.normalizer.normalize_for_semantic_comparison(text)
            assert isinstance(semantic, str)
            
            # Should be able to compute hash
            hash_result = self.normalizer.compute_line_hash(text)
            assert len(hash_result) == 64  # SHA-256 length
    
    def test_very_long_text(self):
        """Test normalization with very long text."""
        # Create a long text
        long_text = "This is a test sentence. " * 1000
        
        # Should handle long text without issues
        normalized = self.normalizer.normalize_line(long_text)
        assert isinstance(normalized, str)
        assert len(normalized) > 0
        
        semantic = self.normalizer.normalize_for_semantic_comparison(long_text)
        assert isinstance(semantic, str)
        
        hash_result = self.normalizer.compute_line_hash(long_text)
        assert len(hash_result) == 64
    
    def test_regex_pattern_efficiency(self):
        """Test that regex patterns are compiled and reused."""
        # Patterns should be compiled once during initialization
        assert hasattr(self.normalizer, 'whitespace_pattern')
        assert hasattr(self.normalizer, 'punctuation_pattern')
        assert hasattr(self.normalizer, 'number_pattern')
        
        # Should be compiled regex objects
        import re
        assert isinstance(self.normalizer.whitespace_pattern, re.Pattern)
        assert isinstance(self.normalizer.punctuation_pattern, re.Pattern)
        assert isinstance(self.normalizer.number_pattern, re.Pattern)
    
    def test_hash_algorithm_verification(self):
        """Test that hash algorithms produce expected results."""
        text = "test"
        
        # Test SHA-256
        sha256_hash = self.normalizer.compute_line_hash(text, "sha256")
        expected_sha256 = hashlib.sha256(text.encode('utf-8')).hexdigest()
        assert sha256_hash == expected_sha256
        
        # Test MD5
        md5_hash = self.normalizer.compute_line_hash(text, "md5")
        expected_md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        assert md5_hash == expected_md5
    
    def test_normalization_preserves_meaning(self):
        """Test that normalization preserves semantic meaning."""
        original = "The quick brown fox jumps over the lazy dog."
        normalized = self.normalizer.normalize_for_semantic_comparison(original)
        
        # Should contain all meaningful words
        meaningful_words = ["quick", "brown", "fox", "jumps", "over", "lazy", "dog"]
        for word in meaningful_words:
            assert word in normalized
        
        # Should not contain punctuation
        assert "." not in normalized
    
    def test_whitespace_normalization_types(self):
        """Test different types of whitespace normalization."""
        # Test various whitespace characters
        whitespace_chars = [
            " ",      # Regular space
            "\t",     # Tab
            "\n",     # Newline
            "\r",     # Carriage return
            "\f",     # Form feed
            "\v",     # Vertical tab
            "\u00A0", # Non-breaking space
            "\u2000", # En quad
            "\u2001", # Em quad
        ]
        
        for ws in whitespace_chars:
            text = f"word1{ws}{ws}word2"
            result = self.normalizer.normalize_line(text)
            assert result == "word1 word2"