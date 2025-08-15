"""
Core data models for the context compressor package.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json


@dataclass
class QualityMetrics:
    """Metrics for evaluating compression quality."""
    
    semantic_similarity: float  # 0.0 to 1.0
    rouge_1: float  # ROUGE-1 F1 score
    rouge_2: float  # ROUGE-2 F1 score
    rouge_l: float  # ROUGE-L F1 score
    entity_preservation_rate: float  # 0.0 to 1.0
    readability_score: float  # Flesch reading ease score
    compression_ratio: float  # actual compression achieved
    overall_score: float  # weighted combination of all metrics
    
    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            'semantic_similarity': self.semantic_similarity,
            'rouge_1': self.rouge_1,
            'rouge_2': self.rouge_2,
            'rouge_l': self.rouge_l,
            'entity_preservation_rate': self.entity_preservation_rate,
            'readability_score': self.readability_score,
            'compression_ratio': self.compression_ratio,
            'overall_score': self.overall_score
        }


@dataclass
class StrategyMetadata:
    """Metadata about a compression strategy."""
    
    name: str
    description: str
    version: str
    author: str
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    min_text_length: int = 100
    max_text_length: Optional[int] = None
    optimal_compression_ratios: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])
    requires_query: bool = False
    supports_batch: bool = True
    supports_streaming: bool = False
    computational_complexity: str = "medium"  # low, medium, high
    memory_requirements: str = "medium"  # low, medium, high
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'supported_languages': self.supported_languages,
            'min_text_length': self.min_text_length,
            'max_text_length': self.max_text_length,
            'optimal_compression_ratios': self.optimal_compression_ratios,
            'requires_query': self.requires_query,
            'supports_batch': self.supports_batch,
            'supports_streaming': self.supports_streaming,
            'computational_complexity': self.computational_complexity,
            'memory_requirements': self.memory_requirements,
            'dependencies': self.dependencies,
            'tags': self.tags
        }


@dataclass
class CompressionResult:
    """Result of text compression operation."""
    
    original_text: str
    compressed_text: str
    strategy_used: str
    target_ratio: float
    actual_ratio: float
    original_tokens: int
    compressed_tokens: int
    processing_time: float  # in seconds
    quality_metrics: Optional[QualityMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    query: Optional[str] = None
    strategy_metadata: Optional[StrategyMetadata] = None
    
    @property
    def tokens_saved(self) -> int:
        """Number of tokens saved by compression."""
        return self.original_tokens - self.compressed_tokens
    
    @property
    def token_savings_percentage(self) -> float:
        """Percentage of tokens saved."""
        if self.original_tokens == 0:
            return 0.0
        return (self.tokens_saved / self.original_tokens) * 100
    
    @property
    def compression_efficiency(self) -> float:
        """Efficiency score combining compression and quality."""
        if self.quality_metrics is None:
            return self.actual_ratio
        return self.actual_ratio * self.quality_metrics.overall_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'original_text': self.original_text,
            'compressed_text': self.compressed_text,
            'strategy_used': self.strategy_used,
            'target_ratio': self.target_ratio,
            'actual_ratio': self.actual_ratio,
            'original_tokens': self.original_tokens,
            'compressed_tokens': self.compressed_tokens,
            'tokens_saved': self.tokens_saved,
            'token_savings_percentage': self.token_savings_percentage,
            'processing_time': self.processing_time,
            'quality_metrics': self.quality_metrics.to_dict() if self.quality_metrics else None,
            'compression_efficiency': self.compression_efficiency,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'query': self.query,
            'strategy_metadata': self.strategy_metadata.to_dict() if self.strategy_metadata else None
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def save_to_file(self, filepath: str) -> None:
        """Save result to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=2))


@dataclass
class BatchCompressionResult:
    """Result of batch compression operation."""
    
    results: List[CompressionResult]
    total_processing_time: float
    strategy_used: str
    target_ratio: float
    parallel_processing: bool = True
    failed_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """Success rate of batch processing."""
        total_items = len(self.results) + len(self.failed_items)
        if total_items == 0:
            return 1.0
        return len(self.results) / total_items
    
    @property
    def average_compression_ratio(self) -> float:
        """Average compression ratio across all successful results."""
        if not self.results:
            return 0.0
        return sum(r.actual_ratio for r in self.results) / len(self.results)
    
    @property
    def total_tokens_saved(self) -> int:
        """Total tokens saved across all results."""
        return sum(r.tokens_saved for r in self.results)
    
    @property
    def average_quality_score(self) -> Optional[float]:
        """Average quality score across results with quality metrics."""
        quality_results = [r for r in self.results if r.quality_metrics is not None]
        if not quality_results:
            return None
        return sum(r.quality_metrics.overall_score for r in quality_results) / len(quality_results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result to dictionary."""
        return {
            'results': [r.to_dict() for r in self.results],
            'total_processing_time': self.total_processing_time,
            'strategy_used': self.strategy_used,
            'target_ratio': self.target_ratio,
            'parallel_processing': self.parallel_processing,
            'failed_items': self.failed_items,
            'success_rate': self.success_rate,
            'average_compression_ratio': self.average_compression_ratio,
            'total_tokens_saved': self.total_tokens_saved,
            'average_quality_score': self.average_quality_score,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class CacheEntry:
    """Cache entry for storing compressed results."""
    
    key: str
    result: Union[CompressionResult, BatchCompressionResult]
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def access(self) -> None:
        """Mark cache entry as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class CompressionStats:
    """Statistics for compression operations."""
    
    total_compressions: int = 0
    total_tokens_processed: int = 0
    total_tokens_saved: int = 0
    total_processing_time: float = 0.0
    strategy_usage: Dict[str, int] = field(default_factory=dict)
    average_compression_ratio: float = 0.0
    average_quality_score: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate percentage."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return (self.cache_hits / total_requests) * 100
    
    @property
    def tokens_saved_percentage(self) -> float:
        """Overall tokens saved percentage."""
        if self.total_tokens_processed == 0:
            return 0.0
        return (self.total_tokens_saved / self.total_tokens_processed) * 100
    
    def update_from_result(self, result: CompressionResult) -> None:
        """Update stats from compression result."""
        self.total_compressions += 1
        self.total_tokens_processed += result.original_tokens
        self.total_tokens_saved += result.tokens_saved
        self.total_processing_time += result.processing_time
        
        # Update strategy usage
        self.strategy_usage[result.strategy_used] = (
            self.strategy_usage.get(result.strategy_used, 0) + 1
        )
        
        # Update running averages
        self.average_compression_ratio = (
            (self.average_compression_ratio * (self.total_compressions - 1) + result.actual_ratio) 
            / self.total_compressions
        )
        
        if result.quality_metrics:
            current_avg_quality = self.average_quality_score * (self.total_compressions - 1)
            self.average_quality_score = (
                (current_avg_quality + result.quality_metrics.overall_score) 
                / self.total_compressions
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'total_compressions': self.total_compressions,
            'total_tokens_processed': self.total_tokens_processed,
            'total_tokens_saved': self.total_tokens_saved,
            'tokens_saved_percentage': self.tokens_saved_percentage,
            'total_processing_time': self.total_processing_time,
            'strategy_usage': self.strategy_usage,
            'average_compression_ratio': self.average_compression_ratio,
            'average_quality_score': self.average_quality_score,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': self.cache_hit_rate
        }