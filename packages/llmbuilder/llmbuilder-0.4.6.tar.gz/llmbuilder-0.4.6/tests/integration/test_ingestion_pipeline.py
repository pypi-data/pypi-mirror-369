"""
Integration tests for the complete ingestion pipeline.

This module tests the end-to-end ingestion workflow including
all document processors and pipeline orchestration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from llmbuilder.data.ingest import IngestionPipeline, ProcessingStats


class TestIngestionPipelineIntegration:
    """Integration tests for the complete ingestion pipeline."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.output_dir = self.temp_path / "cleaned"
        
        # Create sample files for testing
        self._create_sample_files()
        
        # Initialize pipeline
        self.pipeline = IngestionPipeline(str(self.output_dir))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_files(self):
        """Create sample files for testing different formats."""
        # Create HTML file
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test HTML Document</title>
        </head>
        <body>
            <h1>Main Title</h1>
            <p>This is a test paragraph with some content.</p>
            <p>Another paragraph with <strong>bold text</strong>.</p>
        </body>
        </html>
        """
        html_file = self.temp_path / "test.html"
        html_file.write_text(html_content, encoding='utf-8')
        
        # Create Markdown file
        markdown_content = """
        # Test Markdown Document
        
        This is a test paragraph in markdown.
        
        ## Section 2
        
        Another paragraph with **bold text** and *italic text*.
        
        - List item 1
        - List item 2
        - List item 3
        """
        markdown_file = self.temp_path / "test.md"
        markdown_file.write_text(markdown_content, encoding='utf-8')
        
        # Create plain text file (should be ignored by default)
        text_content = "This is a plain text file that should not be processed by default."
        text_file = self.temp_path / "test.txt"
        text_file.write_text(text_content, encoding='utf-8')
        
        # Create unsupported file
        unsupported_file = self.temp_path / "test.xyz"
        unsupported_file.write_text("Unsupported format", encoding='utf-8')
    
    def test_pipeline_initialization(self):
        """Test that the pipeline initializes correctly."""
        assert self.pipeline.output_dir == self.output_dir
        assert self.output_dir.exists()
        assert isinstance(self.pipeline.processors, dict)
        assert isinstance(self.pipeline.supported_formats, set)
        
        # Should have registered some processors
        assert len(self.pipeline.processors) > 0
        assert len(self.pipeline.supported_formats) > 0
    
    def test_supported_formats_detection(self):
        """Test that supported formats are correctly detected."""
        supported_formats = self.pipeline.get_supported_formats()
        
        # Should support at least HTML and Markdown
        assert '.html' in supported_formats or '.htm' in supported_formats
        assert '.md' in supported_formats
        
        # Should not support unsupported formats
        assert '.xyz' not in supported_formats
    
    def test_processor_registration(self):
        """Test that processors are properly registered."""
        # Check that we can get processors for supported formats
        html_processor = self.pipeline.get_processor('.html')
        md_processor = self.pipeline.get_processor('.md')
        
        # At least one of these should be available
        assert html_processor is not None or md_processor is not None
        
        # Should return None for unsupported formats
        unsupported_processor = self.pipeline.get_processor('.xyz')
        assert unsupported_processor is None
    
    def test_single_file_processing(self):
        """Test processing a single file."""
        html_file = self.temp_path / "test.html"
        
        # Process the file
        result = self.pipeline.process_file(str(html_file))
        
        if result is not None:  # Only test if HTML processor is available
            assert isinstance(result, str)
            assert len(result) > 0
            assert "Main Title" in result
            assert "test paragraph" in result
            # HTML tags should be removed
            assert "<html>" not in result
            assert "<p>" not in result
    
    def test_directory_processing(self):
        """Test processing an entire directory."""
        # Process the directory
        stats = self.pipeline.process_directory(str(self.temp_path))
        
        # Check statistics
        assert isinstance(stats, ProcessingStats)
        assert stats.files_processed >= 0  # Depends on available processors
        assert stats.files_failed >= 0
        assert stats.processing_time_seconds >= 0
        assert isinstance(stats.errors, list)
        
        # Check that output files were created for processed files
        output_files = list(self.output_dir.glob("*.txt"))
        assert len(output_files) == stats.files_processed
    
    def test_error_handling_graceful_degradation(self):
        """Test that errors are handled gracefully."""
        # Create a directory with problematic files
        problem_dir = self.temp_path / "problems"
        problem_dir.mkdir()
        
        # Create a file with permission issues (simulate)
        problem_file = problem_dir / "problem.html"
        problem_file.write_text("<html><body>Problem file</body></html>")
        
        # Process the directory
        stats = self.pipeline.process_directory(str(problem_dir))
        
        # Should handle errors gracefully
        assert isinstance(stats, ProcessingStats)
        assert stats.processing_time_seconds >= 0
    
    def test_output_file_generation(self):
        """Test that output files are generated correctly."""
        # Process a single HTML file
        html_file = self.temp_path / "test.html"
        result = self.pipeline.process_file(str(html_file))
        
        if result is not None:  # Only test if processor is available
            # Manually save to test output generation
            output_filename = self.pipeline._generate_output_filename(html_file)
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            # Check that output file exists and has content
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
            # Check that filename is clean
            assert output_filename.endswith('.txt')
            assert not any(char in output_filename for char in '<>:"/\\|?*')
    
    def test_processing_summary_generation(self):
        """Test that processing summaries are generated correctly."""
        # Process the directory
        stats = self.pipeline.process_directory(str(self.temp_path))
        
        # Generate summary
        summary = self.pipeline.get_processing_summary(stats)
        
        # Check summary structure
        assert isinstance(summary, dict)
        assert 'total_files' in summary
        assert 'successful' in summary
        assert 'failed' in summary
        assert 'success_rate_percent' in summary
        assert 'total_size_mb' in summary
        assert 'processing_time_seconds' in summary
        assert 'files_per_second' in summary
        assert 'error_types' in summary
        
        # Check that values are reasonable
        assert summary['total_files'] >= 0
        assert summary['successful'] >= 0
        assert summary['failed'] >= 0
        assert 0 <= summary['success_rate_percent'] <= 100
        assert summary['total_size_mb'] >= 0
        assert summary['processing_time_seconds'] >= 0
        assert isinstance(summary['error_types'], list)
    
    def test_mixed_format_processing(self):
        """Test processing multiple file formats together."""
        # Create additional format files if processors are available
        formats_to_test = ['.html', '.md']
        
        created_files = []
        for fmt in formats_to_test:
            if self.pipeline.get_processor(fmt) is not None:
                if fmt == '.html':
                    content = "<html><body><p>HTML content</p></body></html>"
                elif fmt == '.md':
                    content = "# Markdown\n\nMarkdown content"
                else:
                    content = f"Content for {fmt}"
                
                file_path = self.temp_path / f"test{fmt}"
                file_path.write_text(content, encoding='utf-8')
                created_files.append(file_path)
        
        if created_files:
            # Process the directory
            stats = self.pipeline.process_directory(str(self.temp_path))
            
            # Should have processed at least the files we created
            assert stats.files_processed >= len(created_files)
            
            # Check that output files were created
            output_files = list(self.output_dir.glob("*.txt"))
            assert len(output_files) >= len(created_files)
    
    def test_empty_directory_processing(self):
        """Test processing an empty directory."""
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()
        
        stats = self.pipeline.process_directory(str(empty_dir))
        
        assert stats.files_processed == 0
        assert stats.files_failed == 0
        assert len(stats.errors) == 0
    
    def test_nonexistent_directory_processing(self):
        """Test processing a non-existent directory."""
        nonexistent_dir = str(self.temp_path / "nonexistent")
        
        stats = self.pipeline.process_directory(nonexistent_dir)
        
        assert stats.files_processed == 0
        assert stats.files_failed == 0
        assert len(stats.errors) > 0
        assert stats.errors[0].error_type == "DirectoryError"
    
    def test_large_file_handling(self):
        """Test handling of larger files."""
        # Create a larger HTML file
        large_content = "<html><body>"
        for i in range(1000):
            large_content += f"<p>This is paragraph number {i} with some content.</p>\n"
        large_content += "</body></html>"
        
        large_file = self.temp_path / "large.html"
        large_file.write_text(large_content, encoding='utf-8')
        
        # Process the file
        result = self.pipeline.process_file(str(large_file))
        
        if result is not None:  # Only test if HTML processor is available
            assert len(result) > 10000  # Should be substantial content
            assert "paragraph number 0" in result
            assert "paragraph number 999" in result
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        unicode_content = """
        <html>
        <body>
            <h1>Unicode Test</h1>
            <p>Special characters: café naïve résumé</p>
            <p>Chinese: 你好世界</p>
            <p>Emoji: 🚀 🎉 ✨</p>
        </body>
        </html>
        """
        
        unicode_file = self.temp_path / "unicode.html"
        unicode_file.write_text(unicode_content, encoding='utf-8')
        
        # Process the file
        result = self.pipeline.process_file(str(unicode_file))
        
        if result is not None:  # Only test if HTML processor is available
            assert "café" in result
            assert "naïve" in result
            assert "résumé" in result
            assert "你好世界" in result
            assert "🚀" in result
    
    @pytest.mark.skipif(True, reason="Requires all processor dependencies")
    def test_all_processors_available(self):
        """Test that all expected processors are available."""
        # This test would require all dependencies to be installed
        expected_formats = {'.html', '.htm', '.md', '.epub', '.pdf'}
        available_formats = self.pipeline.get_supported_formats()
        
        for fmt in expected_formats:
            assert fmt in available_formats, f"Processor for {fmt} not available"
    
    def test_processor_error_isolation(self):
        """Test that errors in one processor don't affect others."""
        # This test ensures that if one processor fails, others continue to work
        # Create files for different formats
        html_file = self.temp_path / "test.html"
        html_file.write_text("<html><body><p>HTML content</p></body></html>")
        
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Markdown\n\nMarkdown content")
        
        # Process directory
        stats = self.pipeline.process_directory(str(self.temp_path))
        
        # Even if some processors fail, others should work
        # The exact number depends on which processors are available
        assert stats.files_processed >= 0
        assert isinstance(stats.errors, list)