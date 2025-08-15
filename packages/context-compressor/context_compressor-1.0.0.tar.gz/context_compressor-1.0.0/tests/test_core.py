"""Tests for core functionality."""

import unittest
import tempfile
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor, CompressionResult
from context_compressor.core.models import QualityMetrics, StrategyMetadata
from context_compressor.core.quality_evaluator import QualityEvaluator
from context_compressor.strategies.extractive import ExtractiveStrategy


class TestContextCompressor(unittest.TestCase):
    """Test ContextCompressor main class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = ContextCompressor()
        self.sample_text = (
            "Machine learning is a subset of artificial intelligence that enables "
            "computers to learn and make decisions from data without being "
            "explicitly programmed. It involves the development of algorithms "
            "that can identify patterns in large datasets and use these patterns "
            "to make predictions or classifications on new, unseen data."
        )
    
    def test_initialization(self):
        """Test compressor initialization."""
        self.assertIsInstance(self.compressor, ContextCompressor)
        self.assertTrue(len(self.compressor.list_strategies()) > 0)
        self.assertIn('extractive', self.compressor.list_strategies())
    
    def test_basic_compression(self):
        """Test basic compression functionality."""
        result = self.compressor.compress(
            text=self.sample_text,
            target_ratio=0.5
        )
        
        self.assertIsInstance(result, CompressionResult)
        self.assertEqual(result.original_text, self.sample_text)
        self.assertNotEqual(result.compressed_text, self.sample_text)
        self.assertLess(len(result.compressed_text), len(self.sample_text))
        self.assertGreater(result.original_tokens, result.compressed_tokens)
        self.assertEqual(result.tokens_saved, result.original_tokens - result.compressed_tokens)
        self.assertLess(result.actual_ratio, 1.0)
    
    def test_compression_with_query(self):
        """Test query-aware compression."""
        result = self.compressor.compress(
            text=self.sample_text,
            target_ratio=0.5,
            query="machine learning patterns"
        )
        
        self.assertIsInstance(result, CompressionResult)
        self.assertEqual(result.query, "machine learning patterns")
        self.assertIn("learning", result.compressed_text.lower())
    
    def test_compression_ratios(self):
        """Test different compression ratios."""
        # Use a longer text for better ratio differentiation
        long_text = (
            "Machine learning is a subset of artificial intelligence that enables "
            "computers to learn and make decisions from data without being "
            "explicitly programmed. It involves the development of algorithms "
            "that can identify patterns in large datasets and use these patterns "
            "to make predictions or classifications on new, unseen data. "
            "Popular machine learning techniques include supervised learning, "
            "unsupervised learning, and reinforcement learning. Each approach "
            "has different use cases and applications in various industries. "
            "The field continues to evolve rapidly with new techniques and "
            "improvements being developed regularly."
        )
        
        ratios = [0.3, 0.5, 0.7]
        results = []
        
        for ratio in ratios:
            result = self.compressor.compress(long_text, target_ratio=ratio)
            results.append(result)
        
        # Higher ratios should result in more tokens (or at least not fewer)
        self.assertLessEqual(results[0].compressed_tokens, results[1].compressed_tokens)
        self.assertLessEqual(results[1].compressed_tokens, results[2].compressed_tokens)
    
    def test_batch_compression(self):
        """Test batch compression."""
        texts = [
            "First text about artificial intelligence and its applications in modern technology. This field has grown rapidly over the past decade with significant advancements in deep learning and neural networks. Many companies are now leveraging AI to improve their products and services.",
            "Second text about machine learning algorithms and their implementation in various domains. These algorithms can process vast amounts of data to identify patterns and make accurate predictions. Popular techniques include supervised learning, unsupervised learning, and reinforcement learning methods.",
            "Third text about data science applications across different industries. Data scientists use statistical methods and programming skills to extract insights from complex datasets. The field combines mathematics, statistics, and computer science to solve real-world problems."
        ]
        
        batch_result = self.compressor.compress_batch(
            texts=texts,
            target_ratio=0.6
        )
        
        self.assertEqual(len(batch_result.results), 3)
        self.assertEqual(batch_result.success_rate, 1.0)
        self.assertGreater(batch_result.total_tokens_saved, 0)
        
        for result in batch_result.results:
            self.assertIsInstance(result, CompressionResult)
    
    def test_quality_evaluation(self):
        """Test compression with quality evaluation."""
        result = self.compressor.compress(
            text=self.sample_text,
            target_ratio=0.5,
            evaluate_quality=True
        )
        
        self.assertIsNotNone(result.quality_metrics)
        self.assertIsInstance(result.quality_metrics, QualityMetrics)
        self.assertGreaterEqual(result.quality_metrics.overall_score, 0.0)
        self.assertLessEqual(result.quality_metrics.overall_score, 1.0)
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Empty text
        with self.assertRaises(ValueError):
            self.compressor.compress("", target_ratio=0.5)
        
        # Invalid ratio
        with self.assertRaises(ValueError):
            self.compressor.compress(self.sample_text, target_ratio=1.5)
        
        # Very short text
        with self.assertRaises(ValueError):
            self.compressor.compress("Hi.", target_ratio=0.5)
    
    def test_caching(self):
        """Test compression caching."""
        # First compression
        result1 = self.compressor.compress(self.sample_text, target_ratio=0.5)
        
        # Second compression (should use cache)
        result2 = self.compressor.compress(self.sample_text, target_ratio=0.5)
        
        self.assertEqual(result1.compressed_text, result2.compressed_text)
        
        # Clear cache
        self.compressor.clear_cache()
        
        # Third compression (cache cleared)
        result3 = self.compressor.compress(self.sample_text, target_ratio=0.5)
        self.assertEqual(result1.compressed_text, result3.compressed_text)
    
    def test_statistics(self):
        """Test compression statistics."""
        # Perform some compressions
        for i in range(3):
            self.compressor.compress(
                f"Text {i}: {self.sample_text}",
                target_ratio=0.5
            )
        
        stats = self.compressor.get_stats()
        self.assertGreaterEqual(stats['total_compressions'], 3)
        self.assertGreater(stats['total_tokens_processed'], 0)


class TestQualityEvaluator(unittest.TestCase):
    """Test QualityEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = QualityEvaluator()
        self.original = (
            "Machine learning algorithms can process vast amounts of data to "
            "identify patterns and make accurate predictions about future outcomes."
        )
        self.compressed = (
            "Machine learning algorithms process data to identify patterns "
            "and make predictions."
        )
    
    def test_evaluation(self):
        """Test quality evaluation."""
        metrics = self.evaluator.evaluate(self.original, self.compressed)
        
        self.assertIsInstance(metrics, QualityMetrics)
        self.assertGreaterEqual(metrics.overall_score, 0.0)
        self.assertLessEqual(metrics.overall_score, 1.0)
        self.assertGreaterEqual(metrics.semantic_similarity, 0.0)
        self.assertLessEqual(metrics.semantic_similarity, 1.0)
    
    def test_custom_weights(self):
        """Test custom evaluation weights."""
        custom_evaluator = QualityEvaluator(
            semantic_weight=0.5,
            rouge_weight=0.3,
            entity_weight=0.1,
            readability_weight=0.1
        )
        
        metrics = custom_evaluator.evaluate(self.original, self.compressed)
        self.assertIsInstance(metrics, QualityMetrics)


class TestExtractiveStrategy(unittest.TestCase):
    """Test ExtractiveStrategy class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ExtractiveStrategy()
        self.text = (
            "First sentence about machine learning. Second sentence about "
            "artificial intelligence. Third sentence about data science. "
            "Fourth sentence about neural networks."
        )
    
    def test_metadata(self):
        """Test strategy metadata."""
        metadata = self.strategy.metadata
        self.assertIsInstance(metadata, StrategyMetadata)
        self.assertEqual(metadata.name, "extractive")
        self.assertIsInstance(metadata.version, str)
    
    def test_compression(self):
        """Test text compression."""
        result = self.strategy.compress(self.text, target_ratio=0.5)
        
        self.assertIsInstance(result, CompressionResult)
        self.assertLess(result.compressed_tokens, result.original_tokens)
        self.assertIn("sentence", result.compressed_text.lower())
    
    def test_query_aware_compression(self):
        """Test query-aware compression."""
        result = self.strategy.compress(
            self.text, 
            target_ratio=0.5,
            query="machine learning"
        )
        
        self.assertIsInstance(result, CompressionResult)
        # Should prefer sentences with query terms
        self.assertIn("machine", result.compressed_text.lower())


if __name__ == '__main__':
    unittest.main()