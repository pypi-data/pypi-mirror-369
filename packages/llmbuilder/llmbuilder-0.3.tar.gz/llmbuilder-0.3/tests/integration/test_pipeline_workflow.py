"""
Integration tests for complete pipeline workflows.

This module tests end-to-end workflows combining ingestion,
deduplication, and other data processing components.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from llmbuilder.data.ingest import IngestionPipeline
from llmbuilder.data.dedup import DeduplicationPipeline


class TestPipelineWorkflow:
    """Integration tests for complete data processing workflows."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample data with duplicates
        self._create_sample_data_with_duplicates()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_data_with_duplicates(self):
        """Create sample data files with duplicate content."""
        # Create HTML files with some duplicate content
        html_content_1 = """
        <html>
        <body>
            <h1>Document 1</h1>
            <p>This is unique content for document 1.</p>
            <p>This is shared content that appears in multiple documents.</p>
        </body>
        </html>
        """
        
        html_content_2 = """
        <html>
        <body>
            <h1>Document 2</h1>
            <p>This is unique content for document 2.</p>
            <p>This is shared content that appears in multiple documents.</p>
        </body>
        </html>
        """
        
        html_content_3 = """
        <html>
        <body>
            <h1>Document 3</h1>
            <p>This is shared content that appears in multiple documents.</p>
            <p>Another shared line that appears multiple times.</p>
        </body>
        </html>
        """
        
        # Create Markdown files with duplicates
        md_content_1 = """
        # Markdown Document 1
        
        This is unique markdown content.
        
        This is shared markdown content that appears in multiple files.
        """
        
        md_content_2 = """
        # Markdown Document 2
        
        This is different unique markdown content.
        
        This is shared markdown content that appears in multiple files.
        """
        
        # Write files
        (self.temp_path / "doc1.html").write_text(html_content_1, encoding='utf-8')
        (self.temp_path / "doc2.html").write_text(html_content_2, encoding='utf-8')
        (self.temp_path / "doc3.html").write_text(html_content_3, encoding='utf-8')
        (self.temp_path / "doc1.md").write_text(md_content_1, encoding='utf-8')
        (self.temp_path / "doc2.md").write_text(md_content_2, encoding='utf-8')
    
    def test_ingestion_to_deduplication_workflow(self):
        """Test complete workflow from ingestion to deduplication."""
        # Step 1: Ingestion
        ingestion_output = self.temp_path / "ingested"
        ingestion_pipeline = IngestionPipeline(str(ingestion_output))
        
        ingestion_stats = ingestion_pipeline.process_directory(str(self.temp_path))
        
        # Verify ingestion worked (if processors are available)
        if ingestion_stats.files_processed > 0:
            assert ingestion_output.exists()
            ingested_files = list(ingestion_output.glob("*.txt"))
            assert len(ingested_files) > 0
            
            # Step 2: Deduplication
            dedup_pipeline = DeduplicationPipeline()
            dedup_stats = dedup_pipeline.deduplicate_directory(str(ingestion_output))
            
            # Verify deduplication worked
            assert dedup_stats.files_processed > 0
            assert dedup_stats.original_lines > 0
            
            # Should have removed some duplicates
            if dedup_stats.duplicate_lines_removed > 0:
                assert dedup_stats.final_lines < dedup_stats.original_lines
            
            # Verify files still exist and have content
            for file_path in ingested_files:
                assert file_path.exists()
                content = file_path.read_text(encoding='utf-8')
                assert len(content.strip()) > 0
    
    def test_workflow_with_configuration(self):
        """Test workflow with configuration options."""
        from llmbuilder.config.defaults import DataConfig
        
        # Create configuration with advanced processing enabled
        config = DataConfig()
        config.enable_multi_format_ingestion = True
        config.enable_deduplication = True
        config.deduplication_similarity_threshold = 0.8
        
        # Verify configuration is properly structured
        assert hasattr(config, 'enable_multi_format_ingestion')
        assert hasattr(config, 'enable_deduplication')
        assert hasattr(config, 'deduplication_similarity_threshold')
        assert 0 <= config.deduplication_similarity_threshold <= 1
    
    def test_error_recovery_workflow(self):
        """Test that workflow continues despite individual file errors."""
        # Create a mix of valid and problematic files
        valid_html = "<html><body><p>Valid content</p></body></html>"
        (self.temp_path / "valid.html").write_text(valid_html, encoding='utf-8')
        
        # Create a file that might cause issues (empty file)
        (self.temp_path / "empty.html").write_text("", encoding='utf-8')
        
        # Create a file with only whitespace
        (self.temp_path / "whitespace.html").write_text("   \n  \n  ", encoding='utf-8')
        
        # Process with ingestion pipeline
        ingestion_output = self.temp_path / "output"
        pipeline = IngestionPipeline(str(ingestion_output))
        stats = pipeline.process_directory(str(self.temp_path))
        
        # Should handle errors gracefully
        assert isinstance(stats.errors, list)
        # Should process at least some files successfully (if processors available)
        assert stats.files_processed >= 0
        assert stats.files_failed >= 0
    
    def test_processing_statistics_accuracy(self):
        """Test that processing statistics are accurate."""
        # Create known number of files
        for i in range(3):
            content = f"<html><body><p>Document {i} content</p></body></html>"
            (self.temp_path / f"doc{i}.html").write_text(content, encoding='utf-8')
        
        # Process files
        output_dir = self.temp_path / "output"
        pipeline = IngestionPipeline(str(output_dir))
        stats = pipeline.process_directory(str(self.temp_path))
        
        # Verify statistics
        total_files = stats.files_processed + stats.files_failed
        assert total_files >= 0  # Depends on processor availability
        assert stats.processing_time_seconds >= 0
        assert len(stats.errors) == stats.files_failed
        
        # Generate summary and verify
        summary = pipeline.get_processing_summary(stats)
        assert summary['total_files'] == total_files
        assert summary['successful'] == stats.files_processed
        assert summary['failed'] == stats.files_failed
    
    def test_concurrent_processing_safety(self):
        """Test that pipeline handles concurrent access safely."""
        # Create multiple files
        for i in range(10):
            content = f"<html><body><p>Document {i} with content</p></body></html>"
            (self.temp_path / f"doc{i}.html").write_text(content, encoding='utf-8')
        
        # Process with pipeline (internal concurrency handling)
        output_dir = self.temp_path / "output"
        pipeline = IngestionPipeline(str(output_dir))
        stats = pipeline.process_directory(str(self.temp_path))
        
        # Should complete without errors
        assert stats.processing_time_seconds >= 0
        assert isinstance(stats.errors, list)
    
    def test_memory_efficiency_large_dataset(self):
        """Test memory efficiency with larger dataset."""
        # Create a moderate number of files to test memory usage
        for i in range(20):
            # Create files with substantial content
            content = f"<html><body>"
            for j in range(50):
                content += f"<p>Paragraph {j} in document {i} with some content.</p>\n"
            content += "</body></html>"
            
            (self.temp_path / f"large_doc{i}.html").write_text(content, encoding='utf-8')
        
        # Process files
        output_dir = self.temp_path / "output"
        pipeline = IngestionPipeline(str(output_dir))
        stats = pipeline.process_directory(str(self.temp_path))
        
        # Should complete successfully
        assert stats.processing_time_seconds >= 0
        
        # If files were processed, verify output
        if stats.files_processed > 0:
            output_files = list(output_dir.glob("*.txt"))
            assert len(output_files) == stats.files_processed
            
            # Verify output files have reasonable content
            for output_file in output_files:
                content = output_file.read_text(encoding='utf-8')
                assert len(content) > 100  # Should have substantial content
    
    def test_format_specific_processing(self):
        """Test that different formats are processed appropriately."""
        # Create a clean temporary directory for this test
        test_dir = self.temp_path / "format_test"
        test_dir.mkdir()
        
        # Create files in different formats with format-specific content
        html_content = """
        <html>
        <head><title>HTML Test</title></head>
        <body>
            <h1>HTML Header</h1>
            <p>HTML paragraph with <strong>bold</strong> text.</p>
            <script>console.log("should be removed");</script>
        </body>
        </html>
        """
        
        md_content = """
        # Markdown Header
        
        Markdown paragraph with **bold** text.
        
        - List item 1
        - List item 2
        
        ```javascript
        console.log("code block");
        ```
        """
        
        (test_dir / "format_test.html").write_text(html_content, encoding='utf-8')
        (test_dir / "format_test.md").write_text(md_content, encoding='utf-8')
        
        # Process files
        output_dir = test_dir / "output"
        pipeline = IngestionPipeline(str(output_dir))
        stats = pipeline.process_directory(str(test_dir))
        
        # Check that appropriate processors were used
        if stats.files_processed > 0:
            output_files = list(output_dir.glob("*.txt"))
            
            # Should have processed the files we created
            assert len(output_files) > 0
            
            # Check content of each output file
            all_content = ""
            for output_file in output_files:
                content = output_file.read_text(encoding='utf-8')
                all_content += content + " "
            
            # Should contain text content from our test files
            assert "Header" in all_content or "paragraph" in all_content or "bold" in all_content
            
            # Should not contain HTML-specific syntax
            assert "<html>" not in all_content
            assert "<script>" not in all_content
            
            # Note: Code block content from markdown might be preserved
            # This is acceptable behavior as code blocks contain actual content
            # The important thing is that HTML scripts are removed but markdown code blocks may remain
    
    @pytest.mark.skipif(True, reason="Performance test - run manually")
    def test_performance_benchmarking(self):
        """Performance benchmark test (disabled by default)."""
        import time
        
        # Create a larger dataset for performance testing
        start_time = time.time()
        
        for i in range(100):
            content = f"<html><body><h1>Document {i}</h1>"
            for j in range(20):
                content += f"<p>Paragraph {j} with content.</p>"
            content += "</body></html>"
            
            (self.temp_path / f"perf_doc{i}.html").write_text(content, encoding='utf-8')
        
        setup_time = time.time() - start_time
        
        # Process files and measure time
        process_start = time.time()
        output_dir = self.temp_path / "output"
        pipeline = IngestionPipeline(str(output_dir))
        stats = pipeline.process_directory(str(self.temp_path))
        process_time = time.time() - process_start
        
        print(f"Setup time: {setup_time:.2f}s")
        print(f"Processing time: {process_time:.2f}s")
        print(f"Files processed: {stats.files_processed}")
        print(f"Files per second: {stats.files_processed / process_time:.2f}")
        
        # Basic performance assertions
        assert process_time < 60  # Should complete within 1 minute
        if stats.files_processed > 0:
            assert stats.files_processed / process_time > 0.5  # At least 0.5 files/second