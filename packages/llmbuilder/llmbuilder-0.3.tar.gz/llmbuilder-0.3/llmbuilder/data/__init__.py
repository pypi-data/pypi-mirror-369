"""
Data processing module for LLMBuilder.

This module provides comprehensive data loading, cleaning, and dataset
management utilities for LLM training pipelines, including advanced
multi-format ingestion and deduplication capabilities.
"""

from .loader import DataLoader, DocumentMetadata
from .cleaner import TextCleaner, CleaningStats
from .dataset import (
    TextDataset, 
    MultiFileDataset, 
    create_dataloader, 
    split_dataset,
    save_dataset,
    load_dataset,
    get_dataset_info
)

# Advanced data processing components
from .ingest import (
    IngestionPipeline,
    DocumentProcessor,
    HTMLProcessor,
    MarkdownProcessor,
    EPUBProcessor,
    ProcessingStats,
    ProcessingError,
)
from .pdf_processor import PDFProcessor
from .dedup import (
    DeduplicationPipeline,
    TextNormalizer,
    ExactDuplicateDetector,
    SemanticDuplicateDetector,
    DeduplicationStats,
)

__all__ = [
    # Data loading
    'DataLoader',
    'DocumentMetadata',
    
    # Text cleaning
    'TextCleaner',
    'CleaningStats',
    
    # Dataset management
    'TextDataset',
    'MultiFileDataset',
    'create_dataloader',
    'split_dataset',
    'save_dataset',
    'load_dataset',
    'get_dataset_info',
    
    # Advanced ingestion
    'IngestionPipeline',
    'DocumentProcessor',
    'HTMLProcessor',
    'MarkdownProcessor',
    'EPUBProcessor',
    'PDFProcessor',
    'ProcessingStats',
    'ProcessingError',
    
    # Deduplication
    'DeduplicationPipeline',
    'TextNormalizer',
    'ExactDuplicateDetector',
    'SemanticDuplicateDetector',
    'DeduplicationStats',
]