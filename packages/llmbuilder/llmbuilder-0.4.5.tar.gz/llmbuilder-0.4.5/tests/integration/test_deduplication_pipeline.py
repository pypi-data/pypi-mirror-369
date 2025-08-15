"""
Integration tests for the deduplication pipeline.

This module tests the complete deduplication workflow including
exact and semantic duplicate detection, pipeline orchestration,
and error handling.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from llmbuilder.data.dedup import DeduplicationPipeline, DeduplicationStats


class TestDeduplicationPipelineIntegration:
    """Integration tests for the complete deduplication pipeline."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample files with duplicates
        self._create_sample_files_with_duplicates()
        
        # Initialize pipeline
        self.pipeline = DeduplicationPipeline(similarity_threshold=0.8)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_sample_files_with_duplicates(self):
        """Create sample files with various types of duplicates."""
        # File 1: Contains exact duplicates
        file1_content = """Line 1 with unique content
Line 2 with some content
Line 3 that is duplicated
Line 2 with some content
Line 4 with different content
Line 3 that is duplicated
Line 5 unique to file 1"""
        
        # File 2: Contains semantic duplicates
        file2_content = """Line 1 with unique content for file 2
This is a sentence about machine learning
Another line with different content
This is a sentence regarding machine learning
Line 5 with some other content
A sentence discussing machine learning concepts
Final line for file 2"""
        
        # File 3: Mixed duplicates
        file3_content = """Exact duplicate line
Some unique content here
Exact duplicate line
This line talks about artificial intelligence
More unique content
This line discusses artificial intelligence
Even more content
This line mentions artificial intelligence"""
        
        # Write files
        (self.temp_path / "file1.txt").write_text(file1_content, encoding='utf-8')
        (self.temp_path / "file2.txt").write_text(file2_content, encoding='utf-8')
        (self.temp_path / "file3.txt").write_text(file3_content, encoding='utf-8')
        
        # Create an empty file to test edge cases
        (self.temp_path / "empty.txt").write_text("", encoding='utf-8')
        
        # Create a file with only whitespace
        (self.temp_path / "whitespace.txt").write_text("   \n  \n  \n", encoding='utf-8')
    
    def test_pipeline_initialization(self):
        """Test that the pipeline initializes correctly."""
        assert self.pipeline.similarity_threshold == 0.8
        assert self.pipeline.exact_detector is not None
        assert self.pipeline.semantic_detector is not None
        assert hasattr(self.pipeline.exact_detector, 'seen_hashes')
    
    def test_single_text_deduplication(self):
        """Test deduplication of a single text string."""
        test_text = """Line 1
Line 2
Line 1
Line 3
Line 2
Line 4"""
        
        deduplicated_text, stats = self.pipeline.deduplicate_text(test_text)
        
        # Check statistics
        assert isinstance(stats, DeduplicationStats)
        assert stats.original_lines == 6
        assert stats.duplicate_lines_removed > 0  # Should remove exact duplicates
        assert stats.final_lines < stats.original_lines
        assert stats.processing_time_seconds >= 0
        
        # Check that duplicates are removed
        lines = deduplicated_text.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())
        assert len(unique_lines) <= 4  # Should have at most 4 unique lines
    
    def test_directory_deduplication(self):
        """Test deduplication of an entire directory."""
        output_dir = self.temp_path / "deduplicated"
        
        stats = self.pipeline.deduplicate_directory(str(self.temp_path), str(output_dir))
        
        # Check statistics
        assert isinstance(stats, DeduplicationStats)
        assert stats.files_processed > 0  # Should process at least some files
        assert stats.original_lines > 0
        assert stats.processing_time_seconds >= 0
        
        # Check that output files were created
        output_files = list(output_dir.glob("*.txt"))
        assert len(output_files) >= 3  # Should have at least the non-empty files
        
        # Check that files have content (except empty ones)
        for output_file in output_files:
            if output_file.name not in ["empty.txt", "whitespace.txt"]:
                content = output_file.read_text(encoding='utf-8')
                assert len(content.strip()) > 0
    
    def test_in_place_deduplication(self):
        """Test in-place deduplication (no output directory specified)."""
        # Create a copy of files for in-place testing
        test_dir = self.temp_path / "in_place_test"
        test_dir.mkdir()
        
        # Copy some files
        original_file = self.temp_path / "file1.txt"
        test_file = test_dir / "test.txt"
        test_file.write_text(original_file.read_text(), encoding='utf-8')
        
        # Get original content
        original_content = test_file.read_text(encoding='utf-8')
        original_lines = len([line for line in original_content.split('\n') if line.strip()])
        
        # Perform in-place deduplication
        stats = self.pipeline.deduplicate_directory(str(test_dir))
        
        # Check that file was modified
        new_content = test_file.read_text(encoding='utf-8')
        new_lines = len([line for line in new_content.split('\n') if line.strip()])
        
        assert stats.files_processed == 1
        assert new_lines <= original_lines  # Should have same or fewer lines
    
    def test_specific_files_deduplication(self):
        """Test deduplication of specific files."""
        output_dir = self.temp_path / "specific_output"
        
        # Select specific files
        file_paths = [
            str(self.temp_path / "file1.txt"),
            str(self.temp_path / "file2.txt")
        ]
        
        stats = self.pipeline.deduplicate_files(file_paths, str(output_dir))
        
        # Check statistics
        assert stats.files_processed == 2
        assert stats.original_lines > 0
        
        # Check output files
        output_files = list(output_dir.glob("*.txt"))
        assert len(output_files) == 2
        assert (output_dir / "file1.txt").exists()
        assert (output_dir / "file2.txt").exists()
    
    def test_empty_directory_handling(self):
        """Test handling of empty directories."""
        empty_dir = self.temp_path / "empty_dir"
        empty_dir.mkdir()
        
        stats = self.pipeline.deduplicate_directory(str(empty_dir))
        
        assert stats.files_processed == 0
        assert stats.original_lines == 0
        assert stats.duplicate_lines_removed == 0
    
    def test_nonexistent_directory_handling(self):
        """Test handling of non-existent directories."""
        nonexistent_dir = str(self.temp_path / "nonexistent")
        
        with pytest.raises(ValueError, match="Input directory does not exist"):
            self.pipeline.deduplicate_directory(nonexistent_dir)
    
    def test_configuration_validation(self):
        """Test pipeline configuration validation."""
        validation_results = self.pipeline.validate_configuration()
        
        assert isinstance(validation_results, dict)
        assert "is_valid" in validation_results
        assert "warnings" in validation_results
        assert "recommendations" in validation_results
        assert "configuration" in validation_results
        
        # Check configuration values
        config = validation_results["configuration"]
        assert config["similarity_threshold"] == 0.8
        assert "chunk_size" in config
        assert "hash_algorithm" in config
    
    def test_processing_time_estimation(self):
        """Test processing time estimation."""
        estimates = self.pipeline.estimate_processing_time(1.0, 5)  # 1MB, 5 files
        
        assert isinstance(estimates, dict)
        assert "estimated_lines" in estimates
        assert "exact_deduplication_seconds" in estimates
        assert "semantic_deduplication_seconds" in estimates
        assert "total_estimated_seconds" in estimates
        assert "io_overhead_seconds" in estimates
        
        # Check that estimates are reasonable
        assert estimates["estimated_lines"] > 0
        assert estimates["total_estimated_seconds"] > 0
    
    def test_pipeline_status(self):
        """Test pipeline status reporting."""
        status = self.pipeline.get_pipeline_status()
        
        assert isinstance(status, dict)
        assert "similarity_threshold" in status
        assert "chunk_size" in status
        assert "hash_algorithm" in status
        assert "exact_detector_state" in status
        assert "configuration_valid" in status
        
        # Initially, no hashes should be seen
        assert status["exact_detector_state"]["seen_hashes_count"] == 0
    
    def test_pipeline_reset(self):
        """Test pipeline reset functionality."""
        # Process some text to populate state
        test_text = "Line 1\nLine 2\nLine 1\nLine 3"
        self.pipeline.deduplicate_text(test_text)
        
        # Check that state is populated
        status_before = self.pipeline.get_pipeline_status()
        assert status_before["exact_detector_state"]["seen_hashes_count"] > 0
        
        # Reset pipeline
        self.pipeline.reset_pipeline()
        
        # Check that state is cleared
        status_after = self.pipeline.get_pipeline_status()
        assert status_after["exact_detector_state"]["seen_hashes_count"] == 0
    
    def test_deduplication_summary_generation(self):
        """Test generation of deduplication summaries."""
        # Process some text
        test_text = "Line 1\nLine 2\nLine 1\nLine 3\nLine 2\nLine 4"
        _, stats = self.pipeline.deduplicate_text(test_text)
        
        # Generate summary
        summary = self.pipeline.get_deduplication_summary(stats)
        
        assert isinstance(summary, dict)
        assert "original_lines" in summary
        assert "final_lines" in summary
        assert "exact_duplicates_removed" in summary
        assert "semantic_duplicates_removed" in summary
        assert "total_removed" in summary
        assert "reduction_percent" in summary
        assert "processing_time_seconds" in summary
        assert "lines_per_second" in summary
        assert "efficiency_score" in summary
        
        # Check that values are reasonable
        assert summary["original_lines"] == stats.original_lines
        assert summary["final_lines"] == stats.final_lines
        assert summary["reduction_percent"] >= 0
        assert summary["efficiency_score"] >= 0
    
    def test_error_handling_corrupted_files(self):
        """Test handling of files that can't be read."""
        # Create a file with problematic content
        problem_file = self.temp_path / "problem.txt"
        
        # Write some content first
        problem_file.write_text("Some content", encoding='utf-8')
        
        # Try to make it unreadable (this might not work on all systems)
        try:
            problem_file.chmod(0o000)  # Remove all permissions
            
            # Try to process directory
            stats = self.pipeline.deduplicate_directory(str(self.temp_path))
            
            # Should handle the error gracefully
            assert isinstance(stats, DeduplicationStats)
            
        except (OSError, PermissionError):
            # If we can't change permissions, skip this test
            pytest.skip("Cannot modify file permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                problem_file.chmod(0o644)
            except:
                pass
    
    def test_unicode_content_handling(self):
        """Test handling of Unicode content in deduplication."""
        unicode_content = """Line with café and naïve
Another line with résumé
Line with café and naïve
Chinese content: 你好世界
Another line with résumé
Emoji content: 🚀 🎉 ✨
Chinese content: 你好世界"""
        
        unicode_file = self.temp_path / "unicode.txt"
        unicode_file.write_text(unicode_content, encoding='utf-8')
        
        # Process the file
        stats = self.pipeline.deduplicate_directory(str(self.temp_path))
        
        # Should handle Unicode content without errors
        assert stats.files_processed > 0
        
        # Check that Unicode content is preserved in output
        output_files = list(self.temp_path.glob("unicode.txt"))
        if output_files:
            content = output_files[0].read_text(encoding='utf-8')
            assert "café" in content
            assert "你好世界" in content
            assert "🚀" in content
    
    def test_large_file_handling(self):
        """Test handling of larger files."""
        # Create a larger file with duplicates
        large_content = []
        for i in range(100):
            large_content.append(f"Line {i} with unique content")
            if i % 10 == 0:  # Add some duplicates
                large_content.append("This is a repeated line")
            if i % 20 == 0:  # Add semantic duplicates
                large_content.append("This line discusses machine learning")
                large_content.append("This line talks about machine learning")
        
        large_file = self.temp_path / "large.txt"
        large_file.write_text('\n'.join(large_content), encoding='utf-8')
        
        # Process the file
        _, stats = self.pipeline.deduplicate_text(large_file.read_text(encoding='utf-8'))
        
        # Should handle large content
        assert stats.original_lines > 100
        assert stats.duplicate_lines_removed > 0  # Should find exact duplicates
        assert stats.processing_time_seconds >= 0
    
    @pytest.mark.skipif(True, reason="Requires sentence-transformers dependency")
    def test_semantic_deduplication_with_embeddings(self):
        """Test semantic deduplication with actual embeddings."""
        # This test would require sentence-transformers to be installed
        # It's marked as skip by default to avoid dependency issues
        pass
    
    def test_different_similarity_thresholds(self):
        """Test pipeline with different similarity thresholds."""
        test_text = """This is about machine learning
This discusses machine learning
This talks about artificial intelligence
This mentions artificial intelligence
Completely different content here"""
        
        # Test with high threshold (less aggressive)
        pipeline_high = DeduplicationPipeline(similarity_threshold=0.95)
        _, stats_high = pipeline_high.deduplicate_text(test_text)
        
        # Test with low threshold (more aggressive)
        pipeline_low = DeduplicationPipeline(similarity_threshold=0.7)
        _, stats_low = pipeline_low.deduplicate_text(test_text)
        
        # Low threshold should potentially remove more content
        # (though this depends on whether semantic detection is available)
        assert stats_high.original_lines == stats_low.original_lines
        assert stats_high.final_lines >= stats_low.final_lines or stats_high.final_lines == stats_low.final_lines
    
    def test_pipeline_with_custom_configuration(self):
        """Test pipeline with custom configuration."""
        # Create pipeline with custom settings
        custom_pipeline = DeduplicationPipeline(
            similarity_threshold=0.9,
            chunk_size=256,
            hash_algorithm="md5"
        )
        
        # Verify configuration
        status = custom_pipeline.get_pipeline_status()
        assert status["similarity_threshold"] == 0.9
        assert status["chunk_size"] == 256
        assert status["hash_algorithm"] == "md5"
        
        # Test that it works
        test_text = "Line 1\nLine 2\nLine 1\nLine 3"
        _, stats = custom_pipeline.deduplicate_text(test_text)
        
        assert stats.original_lines == 4
        assert stats.duplicate_lines_removed > 0