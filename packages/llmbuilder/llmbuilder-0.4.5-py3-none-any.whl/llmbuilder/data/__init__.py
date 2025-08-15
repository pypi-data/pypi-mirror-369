"""
Data processing module for LLMBuilder.

This module provides comprehensive data loading, cleaning, and dataset
management utilities for LLM training pipelines, including advanced
multi-format ingestion and deduplication capabilities.
"""

from .cleaner import CleaningStats, TextCleaner
from .dataset import (
    MultiFileDataset,
    TextDataset,
    create_dataloader,
    get_dataset_info,
    load_dataset,
    save_dataset,
    split_dataset,
)
from .dedup import (
    DeduplicationPipeline,
    DeduplicationStats,
    ExactDuplicateDetector,
    SemanticDuplicateDetector,
    TextNormalizer,
)

# Advanced data processing components
from .ingest import (
    DocumentProcessor,
    EPUBProcessor,
    HTMLProcessor,
    IngestionPipeline,
    MarkdownProcessor,
    ProcessingError,
    ProcessingStats,
)
from .loader import DataLoader, DocumentMetadata
from .pdf_processor import PDFProcessor

__all__ = [
    # Data loading
    "DataLoader",
    "DocumentMetadata",
    # Text cleaning
    "TextCleaner",
    "CleaningStats",
    # Dataset management
    "TextDataset",
    "MultiFileDataset",
    "create_dataloader",
    "split_dataset",
    "save_dataset",
    "load_dataset",
    "get_dataset_info",
    # Advanced ingestion
    "IngestionPipeline",
    "DocumentProcessor",
    "HTMLProcessor",
    "MarkdownProcessor",
    "EPUBProcessor",
    "PDFProcessor",
    "ProcessingStats",
    "ProcessingError",
    # Deduplication
    "DeduplicationPipeline",
    "TextNormalizer",
    "ExactDuplicateDetector",
    "SemanticDuplicateDetector",
    "DeduplicationStats",
]
