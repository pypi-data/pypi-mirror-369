"""
Main ContextCompressor class for intelligent text compression.
"""

from typing import Dict, List, Optional, Union, Any
import logging
import time
from pathlib import Path

from .models import CompressionResult, BatchCompressionResult, CompressionStats
from .strategy_manager import StrategyManager
from .quality_evaluator import QualityEvaluator
from ..strategies.base import CompressionStrategy
from ..utils.cache import CacheManager

logger = logging.getLogger(__name__)


class ContextCompressor:
    """
    Main class for intelligent text compression.
    
    This class provides a unified interface for compressing text using various
    strategies while maintaining semantic meaning. It supports automatic strategy
    selection, quality evaluation, caching, and batch processing.
    
    Examples:
        Basic compression:
        >>> compressor = ContextCompressor()
        >>> result = compressor.compress("Long text here...", target_ratio=0.5)
        >>> print(result.compressed_text)
        
        Query-aware compression:
        >>> result = compressor.compress(
        ...     text="Document about AI and ML...",
        ...     target_ratio=0.3,
        ...     query="machine learning applications"
        ... )
        
        Batch compression:
        >>> texts = ["Text 1...", "Text 2...", "Text 3..."]
        >>> batch_result = compressor.compress_batch(texts, target_ratio=0.4)
    """
    
    def __init__(
        self,
        strategies: Optional[List[CompressionStrategy]] = None,
        enable_caching: bool = True,
        cache_ttl: int = 3600,
        enable_quality_evaluation: bool = True,
        default_strategy: str = "auto",
        max_workers: Optional[int] = None
    ):
        """
        Initialize the ContextCompressor.
        
        Args:
            strategies: List of compression strategies to register
            enable_caching: Whether to enable result caching
            cache_ttl: Cache time-to-live in seconds
            enable_quality_evaluation: Whether to evaluate compression quality
            default_strategy: Default strategy name or "auto" for automatic selection
            max_workers: Maximum number of parallel workers for batch processing
        """
        self.strategy_manager = StrategyManager()
        self.enable_quality_evaluation = enable_quality_evaluation
        self.default_strategy = default_strategy
        self.max_workers = max_workers
        self.stats = CompressionStats()
        
        # Initialize quality evaluator if enabled
        self.quality_evaluator = QualityEvaluator() if enable_quality_evaluation else None
        
        # Initialize cache if enabled
        self.cache_manager = CacheManager(ttl=cache_ttl) if enable_caching else None
        
        # Register default strategies if none provided
        if strategies is None:
            self._register_default_strategies()
        else:
            for strategy in strategies:
                self.strategy_manager.register_strategy(strategy)
        
        logger.info(f"ContextCompressor initialized with {len(self.strategy_manager.strategies)} strategies")
    
    def _register_default_strategies(self):
        """Register default compression strategies."""
        try:
            # Import and register extractive strategy
            from ..strategies.extractive import ExtractiveStrategy
            self.strategy_manager.register_strategy(ExtractiveStrategy())
            
            # Import other strategies when available
            # from ..strategies.abstractive import AbstractiveStrategy
            # self.strategy_manager.register_strategy(AbstractiveStrategy())
            
            # from ..strategies.semantic import SemanticStrategy
            # self.strategy_manager.register_strategy(SemanticStrategy())
            
            # from ..strategies.hybrid import HybridStrategy
            # self.strategy_manager.register_strategy(HybridStrategy())
            
        except ImportError as e:
            logger.warning(f"Could not import default strategies: {e}")
    
    def compress(
        self,
        text: str,
        target_ratio: float,
        strategy: str = "auto",
        query: Optional[str] = None,
        evaluate_quality: Optional[bool] = None,
        use_cache: Optional[bool] = None,
        **kwargs
    ) -> CompressionResult:
        """
        Compress text using the specified or automatically selected strategy.
        
        Args:
            text: The input text to compress
            target_ratio: Target compression ratio (0.0 to 1.0)
            strategy: Strategy name or "auto" for automatic selection
            query: Optional query for context-aware compression
            evaluate_quality: Whether to evaluate compression quality (overrides default)
            use_cache: Whether to use caching (overrides default)
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            CompressionResult: Detailed compression results
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If no suitable strategy is available
        """
        # Validate inputs
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        if not (0.0 < target_ratio < 1.0):
            raise ValueError(f"Target ratio must be between 0.0 and 1.0, got {target_ratio}")
        
        # Use default settings if not specified
        if evaluate_quality is None:
            evaluate_quality = self.enable_quality_evaluation
        
        if use_cache is None:
            use_cache = self.cache_manager is not None
        
        # Check cache first
        if use_cache and self.cache_manager:
            cache_key = self.cache_manager.generate_key(text, target_ratio, strategy, query, **kwargs)
            cached_result = self.cache_manager.get(cache_key)
            
            if cached_result is not None:
                self.stats.cache_hits += 1
                logger.debug(f"Cache hit for key: {cache_key[:20]}...")
                return cached_result
            else:
                self.stats.cache_misses += 1
        
        # Select strategy
        strategy_name = strategy if strategy != "auto" else self.default_strategy
        if strategy_name == "auto":
            selected_strategy = self.strategy_manager.select_strategy(text, target_ratio, query)
        else:
            selected_strategy = self.strategy_manager.get_strategy(strategy_name)
        
        if selected_strategy is None:
            raise RuntimeError(f"No suitable strategy found for: {strategy_name}")
        
        # Perform compression
        logger.info(f"Compressing with {selected_strategy.metadata.name} strategy")
        result = selected_strategy.compress(text, target_ratio, query, **kwargs)
        
        # Evaluate quality if enabled
        if evaluate_quality and self.quality_evaluator:
            quality_metrics = self.quality_evaluator.evaluate(
                original=text,
                compressed=result.compressed_text,
                query=query
            )
            result.quality_metrics = quality_metrics
        
        # Update statistics
        self.stats.update_from_result(result)
        
        # Cache result
        if use_cache and self.cache_manager:
            cache_key = self.cache_manager.generate_key(text, target_ratio, strategy, query, **kwargs)
            self.cache_manager.put(cache_key, result)
        
        logger.info(
            f"Compression completed: {result.original_tokens} -> {result.compressed_tokens} tokens "
            f"({result.actual_ratio:.2%}) with {selected_strategy.metadata.name}"
        )
        
        return result
    
    def compress_batch(
        self,
        texts: List[str],
        target_ratio: float,
        strategy: str = "auto",
        query: Optional[str] = None,
        parallel: bool = True,
        evaluate_quality: Optional[bool] = None,
        use_cache: Optional[bool] = None,
        **kwargs
    ) -> BatchCompressionResult:
        """
        Compress multiple texts in batch.
        
        Args:
            texts: List of input texts to compress
            target_ratio: Target compression ratio (0.0 to 1.0)
            strategy: Strategy name or "auto" for automatic selection
            query: Optional query for context-aware compression
            parallel: Whether to process texts in parallel
            evaluate_quality: Whether to evaluate compression quality (overrides default)
            use_cache: Whether to use caching (overrides default)
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            BatchCompressionResult: Batch compression results
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If no suitable strategy is available
        """
        if not texts:
            raise ValueError("Input texts list cannot be empty")
        
        # Use default settings if not specified
        if evaluate_quality is None:
            evaluate_quality = self.enable_quality_evaluation
        
        if use_cache is None:
            use_cache = self.cache_manager is not None
        
        start_time = time.time()
        results = []
        failed_items = []
        
        # Process each text
        for i, text in enumerate(texts):
            try:
                result = self.compress(
                    text=text,
                    target_ratio=target_ratio,
                    strategy=strategy,
                    query=query,
                    evaluate_quality=evaluate_quality,
                    use_cache=use_cache,
                    **kwargs
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to compress text {i}: {e}")
                failed_items.append({
                    'index': i,
                    'text': text[:100] + "..." if len(text) > 100 else text,
                    'error': str(e)
                })
        
        total_processing_time = time.time() - start_time
        
        # Determine which strategy was primarily used
        strategy_used = "mixed" if len(set(r.strategy_used for r in results)) > 1 else (
            results[0].strategy_used if results else "none"
        )
        
        batch_result = BatchCompressionResult(
            results=results,
            total_processing_time=total_processing_time,
            strategy_used=strategy_used,
            target_ratio=target_ratio,
            parallel_processing=parallel and len(texts) > 1,
            failed_items=failed_items
        )
        
        logger.info(
            f"Batch compression completed: {len(results)}/{len(texts)} texts processed "
            f"in {total_processing_time:.2f}s"
        )
        
        return batch_result
    
    def evaluate_quality(
        self,
        original: str,
        compressed: str,
        query: Optional[str] = None
    ) -> Optional[Any]:
        """
        Evaluate the quality of compression.
        
        Args:
            original: Original text
            compressed: Compressed text
            query: Optional query for context-aware evaluation
            
        Returns:
            QualityMetrics: Quality evaluation metrics or None if evaluator not available
        """
        if not self.quality_evaluator:
            logger.warning("Quality evaluator not available")
            return None
        
        return self.quality_evaluator.evaluate(original, compressed, query)
    
    def register_strategy(self, strategy: CompressionStrategy) -> None:
        """
        Register a new compression strategy.
        
        Args:
            strategy: The compression strategy to register
        """
        self.strategy_manager.register_strategy(strategy)
        logger.info(f"Registered strategy: {strategy.metadata.name}")
    
    def unregister_strategy(self, strategy_name: str) -> None:
        """
        Unregister a compression strategy.
        
        Args:
            strategy_name: Name of the strategy to unregister
        """
        self.strategy_manager.unregister_strategy(strategy_name)
        logger.info(f"Unregistered strategy: {strategy_name}")
    
    def list_strategies(self) -> List[str]:
        """
        List all registered strategy names.
        
        Returns:
            List[str]: List of strategy names
        """
        return list(self.strategy_manager.strategies.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dict[str, Any]: Strategy metadata or None if not found
        """
        strategy = self.strategy_manager.get_strategy(strategy_name)
        return strategy.metadata.to_dict() if strategy else None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get compression statistics.
        
        Returns:
            Dict[str, Any]: Compression statistics
        """
        stats_dict = self.stats.to_dict()
        
        # Add additional stats
        if self.cache_manager:
            stats_dict.update(self.cache_manager.get_stats())
        
        return stats_dict
    
    def clear_cache(self) -> None:
        """Clear the compression cache."""
        if self.cache_manager:
            self.cache_manager.clear()
            logger.info("Cache cleared")
        else:
            logger.warning("No cache manager available")
    
    def reset_stats(self) -> None:
        """Reset compression statistics."""
        self.stats = CompressionStats()
        logger.info("Statistics reset")
    
    def save_config(self, filepath: Union[str, Path]) -> None:
        """
        Save compressor configuration to file.
        
        Args:
            filepath: Path to save configuration
        """
        import json
        
        config = {
            'strategies': [s.metadata.to_dict() for s in self.strategy_manager.strategies.values()],
            'enable_quality_evaluation': self.enable_quality_evaluation,
            'default_strategy': self.default_strategy,
            'max_workers': self.max_workers,
            'cache_enabled': self.cache_manager is not None,
            'cache_ttl': self.cache_manager.ttl if self.cache_manager else None
        }
        
        filepath = Path(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
        
        logger.info(f"Configuration saved to {filepath}")
    
    def load_config(self, filepath: Union[str, Path]) -> None:
        """
        Load compressor configuration from file.
        
        Args:
            filepath: Path to load configuration from
        """
        import json
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Apply configuration
        self.enable_quality_evaluation = config.get('enable_quality_evaluation', True)
        self.default_strategy = config.get('default_strategy', "auto")
        self.max_workers = config.get('max_workers')
        
        # Reinitialize quality evaluator if needed
        if self.enable_quality_evaluation and not self.quality_evaluator:
            self.quality_evaluator = QualityEvaluator()
        
        logger.info(f"Configuration loaded from {filepath}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        # Cleanup all strategies
        for strategy in self.strategy_manager.strategies.values():
            if strategy.is_initialized:
                strategy.cleanup()
        
        # Clear cache
        if self.cache_manager:
            self.cache_manager.clear()
        
        logger.info("ContextCompressor cleanup completed")
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"ContextCompressor("
            f"strategies={len(self.strategy_manager.strategies)}, "
            f"cache={'enabled' if self.cache_manager else 'disabled'}, "
            f"quality_eval={'enabled' if self.quality_evaluator else 'disabled'})"
        )
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"{self.__class__.__name__}("
            f"strategies={list(self.strategy_manager.strategies.keys())}, "
            f"default_strategy='{self.default_strategy}', "
            f"enable_quality_evaluation={self.enable_quality_evaluation}, "
            f"cache_enabled={self.cache_manager is not None})"
        )