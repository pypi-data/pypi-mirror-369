"""
Deduplication and normalization engine for LLMBuilder.

This module provides robust deduplication capabilities using both exact
and semantic similarity detection to remove duplicate content from training data.
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional, Any
import unicodedata

logger = logging.getLogger(__name__)


@dataclass
class DeduplicationStats:
    """Statistics from deduplication operations."""
    original_lines: int = 0
    duplicate_lines_removed: int = 0
    near_duplicate_chunks_removed: int = 0
    final_lines: int = 0
    similarity_threshold: float = 0.85
    processing_time_seconds: float = 0.0
    files_processed: int = 0


class TextNormalizer:
    """
    Standardizes text for consistent hashing and comparison.
    
    This class provides various normalization methods to ensure
    consistent text processing across different sources.
    """
    
    def __init__(self, preserve_case: bool = False, preserve_numbers: bool = False):
        """
        Initialize the text normalizer.
        
        Args:
            preserve_case: If True, preserve original case in line normalization
            preserve_numbers: If True, preserve numbers in semantic normalization
        """
        self.preserve_case = preserve_case
        self.preserve_numbers = preserve_numbers
        
        # Compile regex patterns for efficiency
        self.whitespace_pattern = re.compile(r'\s+')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        self.number_pattern = re.compile(r'\d+')
        
        # Additional patterns for advanced normalization
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[1-9]?[0-9]{7,15}')
        self.currency_pattern = re.compile(r'[$£€¥₹]\s*\d+(?:\.\d{2})?')
        self.date_pattern = re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
        self.time_pattern = re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b')
        
        # HTML entity patterns
        self.html_entity_pattern = re.compile(r'&[a-zA-Z][a-zA-Z0-9]*;|&#\d+;|&#x[0-9a-fA-F]+;')
        
        # Common contractions for expansion
        self.contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am",
            "'s": " is",  # Note: This is ambiguous (could be possessive)
        }
    
    def normalize_line(self, text: str) -> str:
        """
        Normalize a single line of text for consistent hashing.
        
        Args:
            text: Input text line
            
        Returns:
            Normalized text suitable for hashing
        """
        if not text:
            return ""
        
        # Unicode normalization (NFKC - canonical decomposition + canonical composition)
        normalized = unicodedata.normalize('NFKC', text)
        
        # Decode HTML entities if present
        normalized = self._decode_html_entities(normalized)
        
        # Convert to lowercase unless preserving case
        if not self.preserve_case:
            normalized = normalized.lower()
        
        # Normalize whitespace (collapse multiple spaces/tabs/newlines to single space)
        normalized = self.whitespace_pattern.sub(' ', normalized)
        
        # Strip leading/trailing whitespace
        normalized = normalized.strip()
        
        return normalized
    
    def normalize_for_semantic_comparison(self, text: str) -> str:
        """
        Normalize text for semantic similarity comparison.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text for semantic comparison
        """
        # Start with line normalization
        normalized = self.normalize_line(text)
        
        # Expand contractions for better semantic matching
        normalized = self._expand_contractions(normalized)
        
        # Normalize structured data patterns
        normalized = self._normalize_structured_data(normalized)
        
        # Remove punctuation for semantic comparison
        normalized = self.punctuation_pattern.sub(' ', normalized)
        
        # Normalize numbers (replace with placeholder) unless preserving
        if not self.preserve_numbers:
            normalized = self.number_pattern.sub('NUM', normalized)
        
        # Final whitespace cleanup
        normalized = self.whitespace_pattern.sub(' ', normalized).strip()
        
        return normalized
    
    def compute_line_hash(self, text: str, algorithm: str = "sha256") -> str:
        """
        Compute a hash for a normalized text line.
        
        Args:
            text: Input text
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal hash string
        """
        normalized = self.normalize_line(text)
        
        if algorithm == "sha256":
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(normalized.encode('utf-8')).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    def normalize_aggressive(self, text: str) -> str:
        """
        Perform aggressive normalization for maximum deduplication.
        
        This method applies all normalization techniques for cases where
        maximum duplicate detection is desired, potentially at the cost
        of some semantic precision.
        
        Args:
            text: Input text
            
        Returns:
            Aggressively normalized text
        """
        if not text:
            return ""
        
        # Start with semantic normalization
        normalized = self.normalize_for_semantic_comparison(text)
        
        # Remove common stop words for aggressive matching
        normalized = self._remove_common_stopwords(normalized)
        
        # Normalize word forms (simple stemming-like operations)
        normalized = self._normalize_word_forms(normalized)
        
        # Final cleanup
        normalized = self.whitespace_pattern.sub(' ', normalized).strip()
        
        return normalized
    
    def _decode_html_entities(self, text: str) -> str:
        """
        Decode HTML entities in text.
        
        Args:
            text: Text potentially containing HTML entities
            
        Returns:
            Text with HTML entities decoded
        """
        try:
            import html
            return html.unescape(text)
        except ImportError:
            # Fallback: manual decoding for common entities
            entities = {
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"',
                '&#39;': "'",
                '&nbsp;': ' ',
                '&copy;': '©',
                '&reg;': '®',
                '&trade;': '™',
            }
            
            for entity, char in entities.items():
                text = text.replace(entity, char)
            
            return text
    
    def _expand_contractions(self, text: str) -> str:
        """
        Expand common English contractions.
        
        Args:
            text: Text potentially containing contractions
            
        Returns:
            Text with contractions expanded
        """
        expanded = text
        
        for contraction, expansion in self.contractions.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(contraction) + r'\b'
            expanded = re.sub(pattern, expansion, expanded, flags=re.IGNORECASE)
        
        return expanded
    
    def _normalize_structured_data(self, text: str) -> str:
        """
        Normalize structured data patterns like URLs, emails, dates, etc.
        
        Args:
            text: Input text
            
        Returns:
            Text with structured data normalized
        """
        normalized = text
        
        # Replace URLs with placeholder
        normalized = self.url_pattern.sub('URL', normalized)
        
        # Replace email addresses with placeholder
        normalized = self.email_pattern.sub('EMAIL', normalized)
        
        # Replace phone numbers with placeholder
        normalized = self.phone_pattern.sub('PHONE', normalized)
        
        # Replace currency amounts with placeholder
        normalized = self.currency_pattern.sub('CURRENCY', normalized)
        
        # Replace dates with placeholder
        normalized = self.date_pattern.sub('DATE', normalized)
        
        # Replace times with placeholder
        normalized = self.time_pattern.sub('TIME', normalized)
        
        return normalized
    
    def _remove_common_stopwords(self, text: str) -> str:
        """
        Remove common English stop words for aggressive normalization.
        
        Args:
            text: Input text
            
        Returns:
            Text with common stop words removed
        """
        # Common English stop words
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'have', 'had',
            'this', 'these', 'they', 'were', 'been', 'their', 'said', 'each',
            'which', 'she', 'do', 'how', 'if', 'up', 'out', 'many', 'then',
            'them', 'can', 'could', 'should', 'would', 'may', 'might', 'must',
            'shall', 'will', 'am', 'is', 'are', 'was', 'were', 'being', 'been'
        }
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stopwords]
        
        return ' '.join(filtered_words)
    
    def _normalize_word_forms(self, text: str) -> str:
        """
        Apply simple word form normalization (basic stemming-like operations).
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized word forms
        """
        # Simple suffix removal rules (basic stemming)
        suffix_rules = [
            ('ies', 'y'),    # cities -> city
            ('ied', 'y'),    # tried -> try
            ('ying', 'y'),   # trying -> try
            ('ing', ''),     # running -> run
            ('ed', ''),      # walked -> walk
            ('er', ''),      # bigger -> big
            ('est', ''),     # biggest -> big
            ('ly', ''),      # quickly -> quick
            ('tion', ''),    # action -> act
            ('sion', ''),    # decision -> decis
            ('ness', ''),    # happiness -> happy
            ('ment', ''),    # development -> develop
            ('ful', ''),     # helpful -> help
            ('less', ''),    # helpless -> help
            ('able', ''),    # readable -> read
            ('ible', ''),    # visible -> vis
        ]
        
        words = text.split()
        normalized_words = []
        
        for word in words:
            if len(word) > 4:  # Only apply to longer words
                normalized_word = word
                for suffix, replacement in suffix_rules:
                    if word.endswith(suffix):
                        normalized_word = word[:-len(suffix)] + replacement
                        break
                normalized_words.append(normalized_word)
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def get_normalization_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about text normalization.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with normalization statistics
        """
        if not text:
            return {
                'original_length': 0,
                'normalized_length': 0,
                'semantic_length': 0,
                'aggressive_length': 0,
                'reduction_ratio': 0.0,
                'contains_urls': False,
                'contains_emails': False,
                'contains_numbers': False,
                'contains_html_entities': False,
            }
        
        normalized = self.normalize_line(text)
        semantic = self.normalize_for_semantic_comparison(text)
        aggressive = self.normalize_aggressive(text)
        
        return {
            'original_length': len(text),
            'normalized_length': len(normalized),
            'semantic_length': len(semantic),
            'aggressive_length': len(aggressive),
            'reduction_ratio': 1.0 - (len(aggressive) / len(text)) if len(text) > 0 else 0.0,
            'contains_urls': bool(self.url_pattern.search(text)),
            'contains_emails': bool(self.email_pattern.search(text)),
            'contains_numbers': bool(self.number_pattern.search(text)),
            'contains_html_entities': bool(self.html_entity_pattern.search(text)),
        }


class ExactDuplicateDetector:
    """
    Detects and removes exact duplicates using normalized hashing.
    
    This class uses line-level hashing to efficiently identify
    and remove exact duplicate content.
    """
    
    def __init__(self, hash_algorithm: str = "sha256"):
        """
        Initialize the exact duplicate detector.
        
        Args:
            hash_algorithm: Hash algorithm to use for duplicate detection
        """
        self.normalizer = TextNormalizer()
        self.hash_algorithm = hash_algorithm
        self.seen_hashes: Set[str] = set()
    
    def compute_line_hashes(self, text: str) -> Set[str]:
        """
        Compute hashes for all lines in a text.
        
        Args:
            text: Input text with multiple lines
            
        Returns:
            Set of line hashes
        """
        hashes = set()
        for line in text.split('\n'):
            if line.strip():  # Skip empty lines
                line_hash = self.normalizer.compute_line_hash(line, self.hash_algorithm)
                hashes.add(line_hash)
        return hashes
    
    def is_duplicate_line(self, line: str) -> bool:
        """
        Check if a line is a duplicate of previously seen content.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line is a duplicate, False otherwise
        """
        if not line.strip():
            return False
        
        line_hash = self.normalizer.compute_line_hash(line, self.hash_algorithm)
        
        if line_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(line_hash)
        return False
    
    def remove_duplicate_lines(self, text: str) -> Tuple[str, int]:
        """
        Remove duplicate lines from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (deduplicated_text, num_duplicates_removed)
        """
        lines = text.split('\n')
        unique_lines = []
        duplicates_removed = 0
        
        for line in lines:
            if not self.is_duplicate_line(line):
                unique_lines.append(line)
            else:
                duplicates_removed += 1
        
        return '\n'.join(unique_lines), duplicates_removed
    
    def reset(self):
        """Reset the detector state for processing new content."""
        self.seen_hashes.clear()


class SemanticDuplicateDetector:
    """
    Detects near-duplicate content using embedding-based similarity.
    
    This class uses sentence transformers to identify semantically
    similar content that may not be exact duplicates.
    """
    
    def __init__(self, similarity_threshold: float = 0.85, chunk_size: int = 512):
        """
        Initialize the semantic duplicate detector.
        
        Args:
            similarity_threshold: Minimum similarity score to consider as duplicate
            chunk_size: Size of text chunks for embedding computation
        """
        self.similarity_threshold = similarity_threshold
        self.chunk_size = chunk_size
        self.normalizer = TextNormalizer()
        
        # Lazy import to avoid dependency issues if not used
        self._model = None
        self._embeddings_cache: List[Tuple[str, Any]] = []
    
    def _get_model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model for semantic deduplication")
            except ImportError:
                logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
                raise ImportError("sentence-transformers package required for semantic deduplication")
        return self._model
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for embedding computation.
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def compute_embeddings(self, text_chunks: List[str]):
        """
        Compute embeddings for text chunks.
        
        Args:
            text_chunks: List of text chunks
            
        Returns:
            Numpy array of embeddings
        """
        model = self._get_model()
        
        # Normalize chunks for better comparison
        normalized_chunks = [
            self.normalizer.normalize_for_semantic_comparison(chunk)
            for chunk in text_chunks
        ]
        
        # Filter out empty chunks
        valid_chunks = [chunk for chunk in normalized_chunks if chunk.strip()]
        
        if not valid_chunks:
            import numpy as np
            return np.array([])
        
        embeddings = model.encode(valid_chunks)
        return embeddings
    
    def find_similar_chunks(self, embeddings, threshold: Optional[float] = None) -> List[Tuple[int, int]]:
        """
        Find pairs of similar chunks based on embeddings.
        
        Args:
            embeddings: Numpy array of embeddings
            threshold: Similarity threshold (uses instance default if None)
            
        Returns:
            List of tuples (index1, index2) for similar chunks
        """
        if threshold is None:
            threshold = self.similarity_threshold
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
        except ImportError:
            logger.error("scikit-learn not available. Install with: pip install scikit-learn")
            raise ImportError("scikit-learn package required for semantic similarity computation")
        
        if len(embeddings) == 0:
            return []
        
        # Compute pairwise cosine similarities
        similarities = cosine_similarity(embeddings)
        
        # Find similar pairs (excluding self-similarity)
        similar_pairs = []
        for i in range(len(similarities)):
            for j in range(i + 1, len(similarities)):
                if similarities[i][j] >= threshold:
                    similar_pairs.append((i, j))
        
        return similar_pairs
    
    def remove_semantic_duplicates(self, text: str) -> Tuple[str, int]:
        """
        Remove semantically similar chunks from text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (deduplicated_text, num_chunks_removed)
        """
        chunks = self.chunk_text(text)
        
        if len(chunks) <= 1:
            return text, 0
        
        # Compute embeddings
        embeddings = self.compute_embeddings(chunks)
        
        if len(embeddings) == 0:
            return text, 0
        
        # Find similar chunks
        similar_pairs = self.find_similar_chunks(embeddings)
        
        # Determine which chunks to remove (keep the first occurrence)
        chunks_to_remove = set()
        for i, j in similar_pairs:
            chunks_to_remove.add(j)  # Remove the second occurrence
        
        # Keep only non-duplicate chunks
        unique_chunks = [
            chunk for idx, chunk in enumerate(chunks)
            if idx not in chunks_to_remove
        ]
        
        deduplicated_text = ' '.join(unique_chunks)
        return deduplicated_text, len(chunks_to_remove)


class DeduplicationPipeline:
    """
    Coordinates exact and semantic deduplication processes.
    
    This class orchestrates the complete deduplication workflow,
    combining exact and semantic duplicate detection.
    """
    
    def __init__(self, similarity_threshold: float = 0.85, chunk_size: int = 512,
                 hash_algorithm: str = "sha256"):
        """
        Initialize the deduplication pipeline.
        
        Args:
            similarity_threshold: Threshold for semantic similarity
            chunk_size: Size of chunks for semantic analysis
            hash_algorithm: Hash algorithm for exact duplicate detection
        """
        self.exact_detector = ExactDuplicateDetector(hash_algorithm)
        self.semantic_detector = SemanticDuplicateDetector(similarity_threshold, chunk_size)
        self.similarity_threshold = similarity_threshold
    
    def deduplicate_text(self, text: str) -> Tuple[str, DeduplicationStats]:
        """
        Remove both exact and semantic duplicates from text.
        
        Args:
            text: Input text to deduplicate
            
        Returns:
            Tuple of (deduplicated_text, stats)
        """
        start_time = time.time()
        stats = DeduplicationStats()
        
        # Count original lines
        original_lines = len([line for line in text.split('\n') if line.strip()])
        stats.original_lines = original_lines
        stats.similarity_threshold = self.similarity_threshold
        
        # Step 1: Remove exact duplicates
        deduplicated_text, exact_duplicates = self.exact_detector.remove_duplicate_lines(text)
        stats.duplicate_lines_removed = exact_duplicates
        
        # Step 2: Remove semantic duplicates
        final_text, semantic_duplicates = self.semantic_detector.remove_semantic_duplicates(deduplicated_text)
        stats.near_duplicate_chunks_removed = semantic_duplicates
        
        # Count final lines
        final_lines = len([line for line in final_text.split('\n') if line.strip()])
        stats.final_lines = final_lines
        
        stats.processing_time_seconds = time.time() - start_time
        
        logger.info(f"Deduplication complete. Original: {original_lines}, "
                   f"Exact duplicates removed: {exact_duplicates}, "
                   f"Semantic duplicates removed: {semantic_duplicates}, "
                   f"Final: {final_lines}")
        
        return final_text, stats
    
    def deduplicate_directory(self, input_dir: str, output_dir: Optional[str] = None) -> DeduplicationStats:
        """
        Deduplicate all text files in a directory.
        
        Args:
            input_dir: Directory containing text files to deduplicate
            output_dir: Output directory (overwrites input if None)
            
        Returns:
            Combined deduplication statistics
        """
        start_time = time.time()
        input_path = Path(input_dir)
        
        # Validate input directory
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        if not input_path.is_dir():
            raise ValueError(f"Input path is not a directory: {input_dir}")
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path
        
        combined_stats = DeduplicationStats()
        combined_stats.similarity_threshold = self.similarity_threshold
        
        # Find all text files
        text_files = list(input_path.glob("*.txt"))
        
        if not text_files:
            logger.warning(f"No .txt files found in directory: {input_dir}")
            return combined_stats
        
        logger.info(f"Found {len(text_files)} text files to deduplicate")
        
        for file_path in text_files:
            try:
                # Read file content with encoding detection
                content = self._read_file_with_encoding_detection(file_path)
                
                if not content.strip():
                    logger.warning(f"Skipping empty file: {file_path.name}")
                    continue
                
                # Deduplicate content
                deduplicated_content, file_stats = self.deduplicate_text(content)
                
                # Write deduplicated content
                output_file = output_path / file_path.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(deduplicated_content)
                
                # Accumulate statistics
                combined_stats.original_lines += file_stats.original_lines
                combined_stats.duplicate_lines_removed += file_stats.duplicate_lines_removed
                combined_stats.near_duplicate_chunks_removed += file_stats.near_duplicate_chunks_removed
                combined_stats.final_lines += file_stats.final_lines
                combined_stats.processing_time_seconds += file_stats.processing_time_seconds
                combined_stats.files_processed += 1
                
                logger.debug(f"Deduplicated {file_path.name}: {file_stats.original_lines} -> {file_stats.final_lines} lines")
                
            except Exception as e:
                logger.error(f"Failed to deduplicate {file_path}: {e}")
                continue
        
        # Reset detector state for next use
        self.exact_detector.reset()
        
        # Update total processing time
        combined_stats.processing_time_seconds = time.time() - start_time
        
        logger.info(f"Directory deduplication complete. Processed {combined_stats.files_processed} files in {combined_stats.processing_time_seconds:.2f}s")
        
        return combined_stats
    
    def _read_file_with_encoding_detection(self, file_path: Path) -> str:
        """
        Read file with encoding detection and error handling.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
        """
        # Try common encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
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
            raise ValueError(f"Could not read file {file_path}: {e}")
    
    def deduplicate_files(self, file_paths: List[str], output_dir: str) -> DeduplicationStats:
        """
        Deduplicate specific files.
        
        Args:
            file_paths: List of file paths to deduplicate
            output_dir: Output directory for deduplicated files
            
        Returns:
            Combined deduplication statistics
        """
        start_time = time.time()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        combined_stats = DeduplicationStats()
        combined_stats.similarity_threshold = self.similarity_threshold
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                continue
            
            try:
                # Read file content
                content = self._read_file_with_encoding_detection(file_path)
                
                if not content.strip():
                    logger.warning(f"Skipping empty file: {file_path.name}")
                    continue
                
                # Deduplicate content
                deduplicated_content, file_stats = self.deduplicate_text(content)
                
                # Write deduplicated content
                output_file = output_path / file_path.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(deduplicated_content)
                
                # Accumulate statistics
                combined_stats.original_lines += file_stats.original_lines
                combined_stats.duplicate_lines_removed += file_stats.duplicate_lines_removed
                combined_stats.near_duplicate_chunks_removed += file_stats.near_duplicate_chunks_removed
                combined_stats.final_lines += file_stats.final_lines
                combined_stats.processing_time_seconds += file_stats.processing_time_seconds
                combined_stats.files_processed += 1
                
                logger.debug(f"Deduplicated {file_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to deduplicate {file_path}: {e}")
                continue
        
        # Reset detector state for next use
        self.exact_detector.reset()
        
        # Update total processing time
        combined_stats.processing_time_seconds = time.time() - start_time
        
        return combined_stats
    
    def get_deduplication_summary(self, stats: DeduplicationStats) -> Dict[str, Any]:
        """
        Generate a summary of deduplication results.
        
        Args:
            stats: DeduplicationStats from deduplication operation
            
        Returns:
            Dictionary with summary information
        """
        total_removed = stats.duplicate_lines_removed + stats.near_duplicate_chunks_removed
        reduction_percent = (total_removed / stats.original_lines * 100) if stats.original_lines > 0 else 0
        
        return {
            "original_lines": stats.original_lines,
            "final_lines": stats.final_lines,
            "exact_duplicates_removed": stats.duplicate_lines_removed,
            "semantic_duplicates_removed": stats.near_duplicate_chunks_removed,
            "total_removed": total_removed,
            "reduction_percent": round(reduction_percent, 2),
            "similarity_threshold": stats.similarity_threshold,
            "processing_time_seconds": round(stats.processing_time_seconds, 2),
            "files_processed": stats.files_processed,
            "lines_per_second": round(stats.original_lines / stats.processing_time_seconds, 2) if stats.processing_time_seconds > 0 else 0,
            "efficiency_score": round((total_removed / stats.original_lines) * 100, 2) if stats.original_lines > 0 else 0
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current pipeline configuration.
        
        Returns:
            Dictionary with validation results and recommendations
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "recommendations": [],
            "configuration": {
                "similarity_threshold": self.similarity_threshold,
                "chunk_size": self.semantic_detector.chunk_size,
                "hash_algorithm": self.exact_detector.hash_algorithm
            }
        }
        
        # Check similarity threshold
        if self.similarity_threshold < 0.5:
            validation_results["warnings"].append("Very low similarity threshold may cause over-aggressive deduplication")
        elif self.similarity_threshold > 0.95:
            validation_results["warnings"].append("Very high similarity threshold may miss near-duplicates")
        
        # Check chunk size
        if self.semantic_detector.chunk_size < 100:
            validation_results["warnings"].append("Small chunk size may reduce semantic detection accuracy")
        elif self.semantic_detector.chunk_size > 1000:
            validation_results["warnings"].append("Large chunk size may increase processing time")
        
        # Check dependencies
        try:
            import sentence_transformers
            validation_results["semantic_detection_available"] = True
        except ImportError:
            validation_results["semantic_detection_available"] = False
            validation_results["warnings"].append("sentence-transformers not available - semantic deduplication disabled")
        
        try:
            import sklearn
            validation_results["similarity_computation_available"] = True
        except ImportError:
            validation_results["similarity_computation_available"] = False
            validation_results["warnings"].append("scikit-learn not available - may affect semantic similarity computation")
        
        # Provide recommendations
        if len(validation_results["warnings"]) == 0:
            validation_results["recommendations"].append("Configuration looks good for general use")
        else:
            validation_results["recommendations"].append("Consider adjusting configuration based on warnings")
        
        return validation_results
    
    def estimate_processing_time(self, text_size_mb: float, num_files: int = 1) -> Dict[str, float]:
        """
        Estimate processing time for given data size.
        
        Args:
            text_size_mb: Size of text data in megabytes
            num_files: Number of files to process
            
        Returns:
            Dictionary with time estimates
        """
        # Base processing rates (lines per second) - these are rough estimates
        exact_dedup_rate = 10000  # lines per second for exact deduplication
        semantic_dedup_rate = 1000  # lines per second for semantic deduplication
        
        # Estimate lines (assuming ~50 characters per line on average)
        estimated_lines = int((text_size_mb * 1024 * 1024) / 50)
        
        # Calculate time estimates
        exact_time = estimated_lines / exact_dedup_rate
        semantic_time = estimated_lines / semantic_dedup_rate
        
        # Add overhead for file I/O and processing
        io_overhead = num_files * 0.1  # 0.1 seconds per file
        
        return {
            "estimated_lines": estimated_lines,
            "exact_deduplication_seconds": round(exact_time, 2),
            "semantic_deduplication_seconds": round(semantic_time, 2),
            "total_estimated_seconds": round(exact_time + semantic_time + io_overhead, 2),
            "io_overhead_seconds": round(io_overhead, 2)
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and configuration.
        
        Returns:
            Dictionary with pipeline status information
        """
        return {
            "similarity_threshold": self.similarity_threshold,
            "chunk_size": self.semantic_detector.chunk_size,
            "hash_algorithm": self.exact_detector.hash_algorithm,
            "exact_detector_state": {
                "seen_hashes_count": len(self.exact_detector.seen_hashes)
            },
            "semantic_detector_available": hasattr(self.semantic_detector, '_model') and self.semantic_detector._model is not None,
            "configuration_valid": self.validate_configuration()["is_valid"]
        }
    
    def reset_pipeline(self):
        """Reset the pipeline state for processing new data."""
        self.exact_detector.reset()
        # Note: Semantic detector doesn't maintain state between calls