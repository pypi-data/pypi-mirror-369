#!/usr/bin/env python3
"""
Advanced Usage Examples for AI Context Compressor.

This script demonstrates advanced features including custom tokenizers,
compression pipelines, caching strategies, and production-ready patterns.
"""

import sys
import os
import time
import threading
import hashlib
import json
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor, CompressionResult
from context_compressor.core.models import QualityMetrics, StrategyMetadata
from context_compressor.strategies.base import CompressionStrategy
from context_compressor.utils.tokenizers import TokenizerBase


class AdvancedTokenizer(TokenizerBase):
    """
    Advanced tokenizer with custom logic and domain-specific handling.
    
    This example shows how to create sophisticated tokenizers for
    specific use cases or domains.
    """
    
    def __init__(self, preserve_entities: bool = True, domain: str = "general"):
        """
        Initialize advanced tokenizer.
        
        Args:
            preserve_entities: Whether to preserve named entities
            domain: Domain-specific tokenization rules
        """
        self.preserve_entities = preserve_entities
        self.domain = domain
        
        # Domain-specific patterns
        self.domain_patterns = {
            "technical": [
                r'\b[A-Z]{2,}\b',  # Acronyms
                r'\b\w+\.\w+\b',   # Module names
                r'\b\d+\.\d+\b'    # Version numbers
            ],
            "financial": [
                r'\$[\d,]+\.?\d*',  # Currency
                r'\b\d+%\b',        # Percentages
                r'\b[A-Z]{3,4}\b'   # Stock symbols
            ],
            "scientific": [
                r'\b[A-Z][a-z]*\d+\b',  # Chemical formulas
                r'\b\d+\.?\d*[μmkKMG]?[gLsVAWΩ]\b',  # Units
                r'\bp\s*[<>=]\s*\d+\.?\d*\b'  # P-values
            ]
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Advanced tokenization with domain-specific rules.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of tokens
        """
        import re
        
        # Basic word tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Preserve domain-specific patterns
        if self.domain in self.domain_patterns:
            for pattern in self.domain_patterns[self.domain]:
                matches = re.findall(pattern, text)
                for match in matches:
                    # Find and replace original tokens with preserved versions
                    match_tokens = re.findall(r'\b\w+\b', match.lower())
                    if match_tokens and match_tokens[0] in tokens:
                        idx = tokens.index(match_tokens[0])
                        tokens[idx] = f"PRESERVE_{match}"
        
        return tokens
    
    def count(self, text: str) -> int:
        """
        Count tokens using advanced logic.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of tokens
        """
        return len(self.tokenize(text))


class AdaptiveCompressionStrategy(CompressionStrategy):
    """
    Adaptive compression strategy that adjusts based on content characteristics.
    
    This strategy analyzes text properties and selects the best approach
    for each specific text.
    """
    
    def __init__(self):
        """Initialize adaptive strategy."""
        super().__init__()
        self._strategies = {
            "short": self._compress_short_text,
            "technical": self._compress_technical_text,
            "narrative": self._compress_narrative_text,
            "structured": self._compress_structured_text
        }
    
    def _create_metadata(self) -> StrategyMetadata:
        """Get strategy metadata."""
        return StrategyMetadata(
            name="adaptive",
            description="Adaptive compression that selects optimal approach based on content",
            version="1.0.0",
            author="AI Context Compressor",
            supported_languages=["en"],
            optimal_compression_ratios=[0.3, 0.4, 0.5, 0.6, 0.7],
            computational_complexity="O(n log n)",
            memory_requirements="Medium",
            tags=["adaptive", "multi-strategy", "content-aware"],
            min_text_length=5,  # Lower minimum for adaptive strategy
            max_text_length=None
        )
    
    def _compress_text(self, text: str, target_ratio: float, query: Optional[str] = None, **kwargs) -> str:
        """
        Compress text using adaptive approach.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            query: Optional query for context awareness
            **kwargs: Additional arguments
            
        Returns:
            str: Compressed text
        """
        # Analyze text characteristics
        content_type = self._analyze_content(text)
        
        # Select appropriate compression method
        compression_method = self._strategies.get(content_type, self._compress_narrative_text)
        
        # Apply compression
        return compression_method(text, target_ratio, query)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_content(self, text: str) -> str:
        """
        Analyze content to determine optimal compression approach.
        
        Args:
            text: Input text
            
        Returns:
            str: Content type classification
        """
        import re
        
        sentences = self._split_sentences(text)
        
        # Short text
        if len(sentences) <= 3:
            return "short"
        
        # Technical indicators
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\bfunction\b|\bclass\b|\bmethod\b',  # Programming terms
            r'\balgorithm\b|\bimplementation\b|\boptimization\b'  # Technical terms
        ]
        
        technical_score = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in technical_patterns)
        
        if technical_score > len(sentences) * 0.3:
            return "technical"
        
        # Structured content (lists, enumerations)
        if re.search(r'(\n\s*[-*•]\s+|\n\s*\d+\.\s+)', text):
            return "structured"
        
        # Default to narrative
        return "narrative"
    
    def _compress_short_text(self, text: str, target_ratio: float, query: Optional[str] = None) -> str:
        """Compress short text (minimal compression)."""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 1:
            return text
        
        # Keep most important sentence
        return sentences[0] if sentences else text
    
    def _compress_technical_text(self, text: str, target_ratio: float, query: Optional[str] = None) -> str:
        """Compress technical text (preserve terminology)."""
        sentences = self._split_sentences(text)
        target_count = max(1, int(len(sentences) * target_ratio))
        
        # Score sentences based on technical terms
        scores = []
        for sentence in sentences:
            score = 0
            # Boost sentences with technical terms
            if any(term in sentence.lower() for term in ['algorithm', 'function', 'method', 'implementation']):
                score += 3
            # Boost sentences with acronyms
            import re
            if re.search(r'\b[A-Z]{2,}\b', sentence):
                score += 2
            # Length penalty
            score -= len(sentence.split()) * 0.01
            scores.append(score)
        
        # Select top-scored sentences
        selected_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:target_count]
        selected_indices.sort()
        
        return '. '.join(sentences[i] for i in selected_indices)
    
    def _compress_narrative_text(self, text: str, target_ratio: float, query: Optional[str] = None) -> str:
        """Compress narrative text (preserve flow)."""
        sentences = self._split_sentences(text)
        target_count = max(1, int(len(sentences) * target_ratio))
        
        # Simple sentence selection maintaining order
        step = len(sentences) / target_count
        selected_indices = [int(i * step) for i in range(target_count)]
        
        return '. '.join(sentences[i] for i in selected_indices if i < len(sentences))
    
    def _compress_structured_text(self, text: str, target_ratio: float, query: Optional[str] = None) -> str:
        """Compress structured text (preserve structure)."""
        lines = text.split('\n')
        target_lines = max(1, int(len(lines) * target_ratio))
        
        # Prioritize lines with structure markers
        scored_lines = []
        for i, line in enumerate(lines):
            score = 0
            if line.strip().startswith(('-', '*', '•')):  # Bullet points
                score += 2
            elif line.strip() and line.strip()[0].isdigit():  # Numbered items
                score += 2
            elif line.strip() and len(line.strip()) > 10:  # Content lines
                score += 1
            scored_lines.append((score, i, line))
        
        # Select top lines maintaining order
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        selected_indices = sorted([x[1] for x in scored_lines[:target_lines]])
        
        return '\n'.join(lines[i] for i in selected_indices)


@dataclass
class CompressionPipeline:
    """
    Advanced compression pipeline with multiple stages and validation.
    
    This class demonstrates how to build sophisticated compression
    workflows with preprocessing, validation, and post-processing.
    """
    
    name: str
    stages: List[Callable[[str], str]]
    validators: List[Callable[[str, str], bool]]
    post_processors: List[Callable[[str], str]]
    
    def process(self, text: str, target_ratio: float = 0.5) -> Dict[str, Any]:
        """
        Process text through the pipeline.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            
        Returns:
            Dict[str, Any]: Processing results
        """
        results = {
            'original_text': text,
            'stage_results': [],
            'validation_results': [],
            'final_text': text,
            'processing_time': 0,
            'success': True,
            'errors': []
        }
        
        start_time = time.time()
        current_text = text
        
        try:
            # Process through stages
            for i, stage in enumerate(self.stages):
                stage_start = time.time()
                stage_result = stage(current_text)
                stage_time = time.time() - stage_start
                
                results['stage_results'].append({
                    'stage_index': i,
                    'input_length': len(current_text),
                    'output_length': len(stage_result),
                    'processing_time': stage_time,
                    'output_text': stage_result[:100] + '...' if len(stage_result) > 100 else stage_result
                })
                
                current_text = stage_result
            
            # Validate results
            for validator in self.validators:
                try:
                    is_valid = validator(text, current_text)
                    results['validation_results'].append({
                        'validator': validator.__name__,
                        'passed': is_valid
                    })
                    
                    if not is_valid:
                        results['success'] = False
                        results['errors'].append(f"Validation failed: {validator.__name__}")
                        
                except Exception as e:
                    results['errors'].append(f"Validator error: {e}")
            
            # Post-processing
            for post_processor in self.post_processors:
                try:
                    current_text = post_processor(current_text)
                except Exception as e:
                    results['errors'].append(f"Post-processor error: {e}")
            
            results['final_text'] = current_text
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(f"Pipeline error: {e}")
        
        results['processing_time'] = time.time() - start_time
        return results


class CompressionCache:
    """
    Advanced caching system with multiple eviction strategies and persistence.
    
    This cache provides sophisticated caching capabilities for
    production environments.
    """
    
    def __init__(
        self, 
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        eviction_strategy: str = "lru",
        persistence_file: Optional[str] = None
    ):
        """
        Initialize compression cache.
        
        Args:
            max_size: Maximum cache size
            ttl_seconds: Time-to-live for cache entries
            eviction_strategy: Eviction strategy (lru, lfu, fifo)
            persistence_file: Optional file for cache persistence
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.eviction_strategy = eviction_strategy
        self.persistence_file = persistence_file
        
        self._cache = {}
        self._access_times = {}
        self._access_counts = {}
        self._insertion_order = []
        self._lock = threading.RLock()
        
        # Load persisted cache if available
        self._load_cache()
    
    def get(self, key: str) -> Optional[CompressionResult]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[CompressionResult]: Cached result or None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if time.time() - entry['timestamp'] > self.ttl_seconds:
                self._remove_key(key)
                return None
            
            # Update access tracking
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            return entry['result']
    
    def put(self, key: str, result: CompressionResult) -> None:
        """
        Put item in cache.
        
        Args:
            key: Cache key
            result: Compression result to cache
        """
        with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_one()
            
            # Store entry
            self._cache[key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # Update tracking
            self._access_times[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            if key not in self._insertion_order:
                self._insertion_order.append(key)
            
            # Persist if configured
            self._save_cache()
    
    def _evict_one(self) -> None:
        """Evict one item based on strategy."""
        if not self._cache:
            return
        
        if self.eviction_strategy == "lru":
            # Least recently used
            key_to_evict = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        elif self.eviction_strategy == "lfu":
            # Least frequently used
            key_to_evict = min(self._access_counts.keys(), key=lambda k: self._access_counts[k])
        elif self.eviction_strategy == "fifo":
            # First in, first out
            key_to_evict = self._insertion_order[0]
        else:
            # Default to LRU
            key_to_evict = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        
        self._remove_key(key_to_evict)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache and tracking."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
        if key in self._access_counts:
            del self._access_counts[key]
        if key in self._insertion_order:
            self._insertion_order.remove(key)
    
    def _save_cache(self) -> None:
        """Save cache to persistence file."""
        if not self.persistence_file:
            return
        
        try:
            cache_data = {
                'cache': {k: {'timestamp': v['timestamp']} for k, v in self._cache.items()},
                'access_counts': self._access_counts,
                'insertion_order': self._insertion_order
            }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def _load_cache(self) -> None:
        """Load cache from persistence file."""
        if not self.persistence_file or not os.path.exists(self.persistence_file):
            return
        
        try:
            with open(self.persistence_file, 'r') as f:
                cache_data = json.load(f)
            
            # Note: We only restore metadata, not the actual results
            # since CompressionResult objects can't be easily serialized
            self._access_counts = cache_data.get('access_counts', {})
            self._insertion_order = cache_data.get('insertion_order', [])
            
        except Exception as e:
            print(f"Failed to load cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'eviction_strategy': self.eviction_strategy,
                'total_accesses': sum(self._access_counts.values()),
                'unique_keys': len(self._access_counts)
            }


class ProductionCompressor:
    """
    Production-ready compressor with advanced features.
    
    This class demonstrates how to build a robust compression system
    suitable for production environments.
    """
    
    def __init__(
        self,
        enable_caching: bool = True,
        cache_config: Optional[Dict[str, Any]] = None,
        enable_metrics: bool = True,
        enable_fallbacks: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize production compressor.
        
        Args:
            enable_caching: Whether to enable caching
            cache_config: Cache configuration
            enable_metrics: Whether to collect metrics
            enable_fallbacks: Whether to enable fallback strategies
            max_workers: Maximum worker threads
        """
        self.compressor = ContextCompressor()
        self.enable_caching = enable_caching
        self.enable_metrics = enable_metrics
        self.enable_fallbacks = enable_fallbacks
        self.max_workers = max_workers
        
        # Initialize cache
        if enable_caching:
            cache_config = cache_config or {}
            self.cache = CompressionCache(**cache_config)
        else:
            self.cache = None
        
        # Initialize metrics
        if enable_metrics:
            self.metrics = {
                'total_requests': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'errors': 0,
                'processing_times': [],
                'compression_ratios': []
            }
        else:
            self.metrics = None
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def compress_with_fallback(
        self,
        text: str,
        target_ratio: float = 0.5,
        strategy: str = "extractive",
        query: Optional[str] = None,
        timeout: float = 30.0
    ) -> CompressionResult:
        """
        Compress text with fallback strategies and caching.
        
        Args:
            text: Text to compress
            target_ratio: Target compression ratio
            strategy: Primary compression strategy
            query: Optional query for context awareness
            timeout: Processing timeout in seconds
            
        Returns:
            CompressionResult: Compression result
        """
        start_time = time.time()
        
        # Update metrics
        if self.enable_metrics:
            self.metrics['total_requests'] += 1
        
        # Generate cache key
        cache_key = None
        if self.enable_caching:
            cache_key = self._generate_cache_key(text, target_ratio, strategy, query)
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                if self.enable_metrics:
                    self.metrics['cache_hits'] += 1
                return cached_result
            elif self.enable_metrics:
                self.metrics['cache_misses'] += 1
        
        # Attempt compression with timeout
        try:
            future = self.executor.submit(
                self._compress_with_strategies,
                text, target_ratio, strategy, query
            )
            
            result = future.result(timeout=timeout)
            
            # Cache result
            if self.enable_caching and cache_key:
                self.cache.put(cache_key, result)
            
            # Update metrics
            if self.enable_metrics:
                processing_time = time.time() - start_time
                self.metrics['processing_times'].append(processing_time)
                self.metrics['compression_ratios'].append(result.actual_ratio)
            
            return result
            
        except Exception as e:
            if self.enable_metrics:
                self.metrics['errors'] += 1
            
            if self.enable_fallbacks:
                # Fallback to simple compression
                return self._fallback_compress(text, target_ratio)
            else:
                raise e
    
    def _compress_with_strategies(
        self,
        text: str,
        target_ratio: float,
        strategy: str,
        query: Optional[str]
    ) -> CompressionResult:
        """Try compression with multiple strategies."""
        strategies_to_try = [strategy]
        
        if self.enable_fallbacks:
            strategies_to_try.extend(["extractive", "auto"])
        
        last_error = None
        
        for strategy_name in strategies_to_try:
            try:
                return self.compressor.compress(
                    text=text,
                    target_ratio=target_ratio,
                    strategy=strategy_name,
                    query=query
                )
            except Exception as e:
                last_error = e
                continue
        
        # If all strategies failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise ValueError("No compression strategies available")
    
    def _fallback_compress(self, text: str, target_ratio: float) -> CompressionResult:
        """Simple fallback compression."""
        sentences = text.split('. ')
        target_count = max(1, int(len(sentences) * target_ratio))
        compressed_sentences = sentences[:target_count]
        compressed_text = '. '.join(compressed_sentences)
        
        # Create a basic result
        from context_compressor.core.models import CompressionResult
        return CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            original_tokens=len(text.split()),
            compressed_tokens=len(compressed_text.split()),
            target_ratio=target_ratio,
            actual_ratio=len(compressed_text.split()) / len(text.split()) if text else 0,
            strategy_used="fallback",
            processing_time=0.001,
            quality_metrics=None
        )
    
    def _generate_cache_key(
        self,
        text: str,
        target_ratio: float,
        strategy: str,
        query: Optional[str]
    ) -> str:
        """Generate cache key for compression parameters."""
        content = f"{text}{target_ratio}{strategy}{query or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.enable_metrics:
            return {}
        
        metrics = self.metrics.copy()
        
        # Calculate derived metrics
        if metrics['processing_times']:
            metrics['avg_processing_time'] = sum(metrics['processing_times']) / len(metrics['processing_times'])
            metrics['max_processing_time'] = max(metrics['processing_times'])
        
        if metrics['compression_ratios']:
            metrics['avg_compression_ratio'] = sum(metrics['compression_ratios']) / len(metrics['compression_ratios'])
        
        # Cache metrics
        if self.cache:
            metrics.update(self.cache.get_stats())
        
        return metrics
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


def demonstrate_advanced_tokenizer():
    """Demonstrate advanced tokenizer usage."""
    
    print("🔤 Advanced Tokenizer Examples")
    print("-" * 30)
    
    # Sample texts for different domains
    texts = {
        "technical": """
        The ML model uses TensorFlow 2.8 for training. The training.py script implements
        the train_model() function with hyperparameters optimization. GPU acceleration
        requires CUDA 11.2 or higher.
        """,
        
        "financial": """
        The company reported $15.2M revenue in Q3, up 23% YoY. AAPL stock reached
        $150.25, while the S&P 500 index gained 1.8%. The profit margin was 12.5%.
        """,
        
        "scientific": """
        The reaction produces H2SO4 at 298K with ΔG = -45.2 kJ/mol. Statistical
        analysis shows p < 0.05 for the treatment group (n=150). The UV absorption
        peak appears at 280nm.
        """
    }
    
    # Test different domains
    for domain, text in texts.items():
        print(f"\n{domain.upper()} Domain:")
        print(f"Text: {text.strip()[:100]}...")
        
        # Standard tokenizer
        compressor = ContextCompressor()
        standard_result = compressor.compress(text, target_ratio=0.6)
        
        print(f"Standard tokenizer: {standard_result.original_tokens} → {standard_result.compressed_tokens} tokens")
        
        # Advanced tokenizer
        advanced_tokenizer = AdvancedTokenizer(domain=domain)
        token_count = advanced_tokenizer.count(text)
        tokens = advanced_tokenizer.tokenize(text)
        
        print(f"Advanced tokenizer: {token_count} tokens")
        print(f"Preserved patterns: {[t for t in tokens if t.startswith('PRESERVE_')]}")


def demonstrate_adaptive_strategy():
    """Demonstrate adaptive compression strategy."""
    
    print("\n🧠 Adaptive Strategy Examples")
    print("-" * 29)
    
    # Register adaptive strategy
    compressor = ContextCompressor()
    adaptive_strategy = AdaptiveCompressionStrategy()
    compressor.strategy_manager.register_strategy(adaptive_strategy)
    
    # Test texts of different types
    test_texts = {
        "short": "AI is transforming technology in many ways. Artificial intelligence and machine learning algorithms are being deployed across various industries including healthcare, finance, and transportation.",
        
        "technical": """
        The algorithm implements a depth-first search with memoization. The time complexity
        is O(n log n) where n is the input size. The function uses recursion with
        optimization techniques for better performance.
        """,
        
        "narrative": """
        Once upon a time, there was a small village nestled in the mountains. The villagers
        lived peacefully, tending to their crops and livestock. Every morning, the sun would
        rise over the peaks, casting a golden glow across the valley.
        """,
        
        "structured": """
        Features of the new system:
        - Real-time data processing
        - Scalable architecture
        - User-friendly interface
        - Advanced security measures
        
        Benefits include:
        1. Improved efficiency
        2. Cost reduction
        3. Better user experience
        """
    }
    
    for content_type, text in test_texts.items():
        print(f"\n{content_type.upper()} Content:")
        
        result = compressor.compress(
            text=text,
            target_ratio=0.5,
            strategy="adaptive"
        )
        
        print(f"Original: {result.original_tokens} tokens")
        print(f"Compressed: {result.compressed_tokens} tokens ({result.actual_ratio:.1%})")
        print(f"Result: '{result.compressed_text[:80]}...'")


def demonstrate_compression_pipeline():
    """Demonstrate compression pipeline usage."""
    
    print("\n🔄 Compression Pipeline Examples")
    print("-" * 33)
    
    # Define pipeline stages
    def preprocessing_stage(text: str) -> str:
        """Clean and normalize text."""
        import re
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove parenthetical comments
        text = re.sub(r'\([^)]*\)', '', text)
        return text.strip()
    
    def compression_stage(text: str) -> str:
        """Apply compression."""
        compressor = ContextCompressor()
        result = compressor.compress(text, target_ratio=0.6)
        return result.compressed_text
    
    def quality_check(original: str, compressed: str) -> bool:
        """Validate compression quality."""
        # Simple length check
        return len(compressed) >= len(original) * 0.3
    
    def readability_check(original: str, compressed: str) -> bool:
        """Check readability."""
        # Ensure sentences end properly
        return compressed.endswith('.') or compressed.endswith('!') or compressed.endswith('?')
    
    def postprocessing_stage(text: str) -> str:
        """Final cleanup."""
        # Ensure proper capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        return text
    
    # Create pipeline
    pipeline = CompressionPipeline(
        name="quality_compression",
        stages=[preprocessing_stage, compression_stage],
        validators=[quality_check, readability_check],
        post_processors=[postprocessing_stage]
    )
    
    # Test pipeline
    sample_text = """
    Artificial intelligence (AI) has revolutionized many industries. Companies are using
    machine learning (ML) algorithms to process vast amounts of data. These technologies
    enable better decision-making and improved efficiency across various sectors.
    """
    
    result = pipeline.process(sample_text)
    
    print(f"Pipeline: {pipeline.name}")
    print(f"Success: {result['success']}")
    print(f"Processing time: {result['processing_time']:.3f}s")
    print(f"Stages completed: {len(result['stage_results'])}")
    
    for stage_result in result['stage_results']:
        print(f"  Stage {stage_result['stage_index']}: "
              f"{stage_result['input_length']} → {stage_result['output_length']} chars "
              f"({stage_result['processing_time']:.3f}s)")
    
    print(f"Validation results: {[v['passed'] for v in result['validation_results']]}")
    print(f"Final text: '{result['final_text'][:100]}...'")
    
    if result['errors']:
        print(f"Errors: {result['errors']}")


def demonstrate_production_compressor():
    """Demonstrate production-ready compressor."""
    
    print("\n🏭 Production Compressor Examples")
    print("-" * 34)
    
    # Configure production compressor
    cache_config = {
        'max_size': 100,
        'ttl_seconds': 300,  # 5 minutes
        'eviction_strategy': 'lru'
    }
    
    prod_compressor = ProductionCompressor(
        enable_caching=True,
        cache_config=cache_config,
        enable_metrics=True,
        enable_fallbacks=True,
        max_workers=2
    )
    
    # Test texts
    test_texts = [
        "AI and machine learning are transforming business operations.",
        "Cloud computing provides scalable infrastructure for modern applications.",
        "Data science helps organizations make informed decisions from data insights."
    ]
    
    print("Processing texts with production compressor...")
    
    # Process texts (some will be cached)
    for i, text in enumerate(test_texts):
        print(f"\nText {i+1}:")
        
        # First compression
        result1 = prod_compressor.compress_with_fallback(
            text=text,
            target_ratio=0.6,
            timeout=5.0
        )
        
        print(f"  First compression: {result1.original_tokens} → {result1.compressed_tokens} tokens")
        
        # Second compression (should hit cache)
        result2 = prod_compressor.compress_with_fallback(
            text=text,
            target_ratio=0.6,
            timeout=5.0
        )
        
        print(f"  Second compression: {result2.original_tokens} → {result2.compressed_tokens} tokens (cached)")
    
    # Show metrics
    metrics = prod_compressor.get_metrics()
    print(f"\n📊 Performance Metrics:")
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Cache hits: {metrics['cache_hits']}")
    print(f"  Cache misses: {metrics['cache_misses']}")
    print(f"  Cache hit rate: {metrics['cache_hits'] / metrics['total_requests'] * 100:.1f}%")
    print(f"  Average processing time: {metrics.get('avg_processing_time', 0):.3f}s")
    print(f"  Average compression ratio: {metrics.get('avg_compression_ratio', 0):.1%}")
    print(f"  Errors: {metrics['errors']}")


def demonstrate_concurrent_processing():
    """Demonstrate concurrent compression processing."""
    
    print("\n⚡ Concurrent Processing Examples")
    print("-" * 33)
    
    # Generate test data
    texts = [
        f"This is test document number {i+1}. It contains information about "
        f"various topics including technology, science, and business applications. "
        f"The content is designed to test compression algorithms and performance "
        f"under different scenarios and workloads."
        for i in range(10)
    ]
    
    compressor = ContextCompressor()
    
    # Sequential processing
    print("Sequential processing:")
    start_time = time.time()
    sequential_results = []
    
    for text in texts:
        result = compressor.compress(text, target_ratio=0.5)
        sequential_results.append(result)
    
    sequential_time = time.time() - start_time
    print(f"  Time: {sequential_time:.3f}s")
    print(f"  Results: {len(sequential_results)} compressed texts")
    
    # Concurrent processing
    print("\nConcurrent processing:")
    start_time = time.time()
    
    def compress_text(text):
        return compressor.compress(text, target_ratio=0.5)
    
    concurrent_results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(compress_text, text) for text in texts]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                concurrent_results.append(result)
            except Exception as e:
                print(f"  Error: {e}")
    
    concurrent_time = time.time() - start_time
    print(f"  Time: {concurrent_time:.3f}s")
    print(f"  Results: {len(concurrent_results)} compressed texts")
    print(f"  Speedup: {sequential_time / concurrent_time:.2f}x")


def main():
    """Run all advanced usage examples."""
    
    print("🚀 AI Context Compressor - Advanced Usage Examples")
    print("=" * 55)
    
    # Demonstrate advanced features
    demonstrate_advanced_tokenizer()
    demonstrate_adaptive_strategy()
    demonstrate_compression_pipeline()
    demonstrate_production_compressor()
    demonstrate_concurrent_processing()
    
    print("\n✅ Advanced usage examples completed!")
    
    print("\n💡 Key Takeaways:")
    print("   • Custom tokenizers enable domain-specific optimizations")
    print("   • Adaptive strategies can improve compression quality")
    print("   • Pipelines provide structured processing workflows")
    print("   • Production features include caching, metrics, and fallbacks")
    print("   • Concurrent processing can significantly improve throughput")
    
    print("\n🔧 Production Tips:")
    print("   • Monitor cache hit rates and adjust TTL accordingly")
    print("   • Use appropriate eviction strategies for your use case")
    print("   • Implement proper error handling and fallback mechanisms")
    print("   • Consider domain-specific tokenizers for specialized content")
    print("   • Use concurrent processing for high-throughput scenarios")
    print("   • Collect and analyze performance metrics regularly")
    
    print("\n📚 Further Reading:")
    print("   • Study the source code for implementation details")
    print("   • Experiment with different caching strategies")
    print("   • Benchmark performance with your specific workloads")
    print("   • Consider custom strategies for your domain")


if __name__ == "__main__":
    main()