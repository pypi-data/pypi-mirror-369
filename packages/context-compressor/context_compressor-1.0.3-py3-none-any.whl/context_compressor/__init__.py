"""
Context Compressor - AI-powered text compression for RAG systems and API calls.

This package provides intelligent text compression capabilities designed to reduce
token usage and costs while preserving semantic meaning for AI applications.
"""

__version__ = "0.1.0"
__author__ = "Context Compressor Team"
__email__ = "support@contextcompressor.dev"

from .core.compressor import ContextCompressor
from .core.models import CompressionResult, QualityMetrics, StrategyMetadata
from .core.strategy_manager import StrategyManager
from .strategies.base import CompressionStrategy

__all__ = [
    "ContextCompressor",
    "CompressionResult", 
    "QualityMetrics",
    "StrategyMetadata",
    "StrategyManager",
    "CompressionStrategy",
]