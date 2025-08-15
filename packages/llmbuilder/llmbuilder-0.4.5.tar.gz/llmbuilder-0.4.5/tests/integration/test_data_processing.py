"""
Integration tests for data processing pipeline.

This module tests the complete data processing workflow including
ingestion, deduplication, and integration with existing systems.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from llmbuilder.data.ingest import IngestionPipeline, ProcessingStats
from llmbuilder.data.dedup import DeduplicationPipeline, DeduplicationStats


class TestDataProcessingIntegration:
    """Integration tests for data processing components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample test files
        self._create_sample_files()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_files(self):
        """Create sample files for testing."""
        # Create sample text files
        sample_texts = [
            "This is a sample text for testing data processing.",
            "Another sample text with different content for testing.",
            "This is a sample text for testing data processing.",  # Duplicate
            "Some unique content that should not be duplicated.",
        ]
        
        for i, text in enumerate(sample_texts):
            file_path = self.temp_path / f"sample_{i}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
    
    def test_ingestion_pipeline_initialization(self):
        """Test that ingestion pipeline initializes correctly."""
        output_dir = self.temp_path / "cleaned"
        pipeline = IngestionPipeline(str(output_dir))
        
        assert pipeline.output_dir == output_dir
        assert output_dir.exists()
        assert isinstance(pipeline.processors, dict)
        assert isinstance(pipeline.supported_formats, set)
    
    def test_deduplication_pipeline_initialization(self):
        """Test that deduplication pipeline initializes correctly."""
        pipeline = DeduplicationPipeline()
        
        assert pipeline.exact_detector is not None
        assert pipeline.semantic_detector is not None
        assert pipeline.similarity_threshold == 0.85
    
    def test_deduplication_basic_functionality(self):
        """Test basic deduplication functionality."""
        pipeline = DeduplicationPipeline()
        
        # Test text with duplicates
        test_text = """Line 1
Line 2
Line 1
Line 3
Line 2"""
        
        deduplicated_text, stats = pipeline.deduplicate_text(test_text)
        
        assert stats.original_lines > 0
        assert stats.duplicate_lines_removed > 0
        assert stats.final_lines < stats.original_lines
        assert isinstance(deduplicated_text, str)
    
    def test_processing_stats_structure(self):
        """Test that processing statistics have correct structure."""
        stats = ProcessingStats()
        
        assert hasattr(stats, 'files_processed')
        assert hasattr(stats, 'files_failed')
        assert hasattr(stats, 'total_size_bytes')
        assert hasattr(stats, 'processing_time_seconds')
        assert hasattr(stats, 'errors')
        assert isinstance(stats.errors, list)
    
    def test_deduplication_stats_structure(self):
        """Test that deduplication statistics have correct structure."""
        stats = DeduplicationStats()
        
        assert hasattr(stats, 'original_lines')
        assert hasattr(stats, 'duplicate_lines_removed')
        assert hasattr(stats, 'near_duplicate_chunks_removed')
        assert hasattr(stats, 'final_lines')
        assert hasattr(stats, 'similarity_threshold')
        assert hasattr(stats, 'processing_time_seconds')
    
    def test_directory_processing_workflow(self):
        """Test processing a directory of files."""
        pipeline = DeduplicationPipeline()
        
        # Process the directory with sample files
        stats = pipeline.deduplicate_directory(str(self.temp_path))
        
        assert stats.files_processed > 0
        assert stats.original_lines > 0
        assert isinstance(stats.processing_time_seconds, float)
    
    def test_error_handling_graceful_degradation(self):
        """Test that errors are handled gracefully."""
        pipeline = IngestionPipeline()
        
        # Test with non-existent directory
        stats = pipeline.process_directory("non_existent_directory")
        
        assert stats.files_processed == 0
        assert len(stats.errors) > 0
        assert stats.errors[0].error_type == "DirectoryError"
    
    def test_configuration_integration(self):
        """Test integration with configuration system."""
        # This test ensures the new config options are properly structured
        from llmbuilder.config.defaults import DataConfig
        
        config = DataConfig()
        
        # Check new configuration options exist
        assert hasattr(config, 'enable_multi_format_ingestion')
        assert hasattr(config, 'enable_deduplication')
        assert hasattr(config, 'deduplication_similarity_threshold')
        assert hasattr(config, 'deduplication_chunk_size')
        assert hasattr(config, 'ocr_fallback_enabled')
        assert hasattr(config, 'ocr_quality_threshold')
        
        # Check default values
        assert isinstance(config.enable_multi_format_ingestion, bool)
        assert isinstance(config.enable_deduplication, bool)
        assert 0 <= config.deduplication_similarity_threshold <= 1
        assert config.deduplication_chunk_size > 0
    
    @pytest.mark.skipif(True, reason="Requires sentence-transformers dependency")
    def test_semantic_deduplication_integration(self):
        """Test semantic deduplication with actual embeddings."""
        # This test would require sentence-transformers to be installed
        # It's marked as skip by default to avoid dependency issues
        pass
    
    def test_output_directory_creation(self):
        """Test that output directories are created correctly."""
        output_dir = self.temp_path / "new_output_dir"
        pipeline = IngestionPipeline(str(output_dir))
        
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_file_validation_logic(self):
        """Test file validation in processors."""
        from llmbuilder.data.ingest import DocumentProcessor
        
        # Create a mock processor for testing
        class MockProcessor(DocumentProcessor):
            def process(self, file_path: str) -> str:
                return "mock content"
            
            def supports_format(self, file_extension: str) -> bool:
                return file_extension == ".txt"
        
        processor = MockProcessor()
        
        # Test with existing file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test content")
        assert processor.validate_file(str(test_file)) is True
        
        # Test with non-existent file
        assert processor.validate_file("non_existent.txt") is False