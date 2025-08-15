"""Tests for utility modules."""

import unittest
import sys
import os
import time

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor.utils.tokenizers import (
    WhitespaceTokenizer, RegexTokenizer, SentenceTokenizer, 
    ApproximateTokenizer, TokenizerManager
)
from context_compressor.utils.cache import CacheManager


class TestTokenizers(unittest.TestCase):
    """Test tokenizer utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = (
            "Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data."
        )
    
    def test_whitespace_tokenizer(self):
        """Test whitespace tokenizer."""
        tokenizer = WhitespaceTokenizer()
        tokens = tokenizer.tokenize(self.sample_text)
        count = tokenizer.count(self.sample_text)
        
        self.assertIsInstance(tokens, list)
        self.assertEqual(len(tokens), count)
        self.assertGreater(count, 0)
    
    def test_regex_tokenizer(self):
        """Test regex tokenizer."""
        tokenizer = RegexTokenizer()
        tokens = tokenizer.tokenize(self.sample_text)
        count = tokenizer.count(self.sample_text)
        
        self.assertIsInstance(tokens, list)
        self.assertEqual(len(tokens), count)
        self.assertGreater(count, 0)
    
    def test_regex_tokenizer_with_stopwords(self):
        """Test regex tokenizer with stopword removal."""
        tokenizer = RegexTokenizer(remove_stopwords=True)
        tokens_with_stopwords = tokenizer.tokenize(self.sample_text)
        
        tokenizer_no_stopwords = RegexTokenizer(remove_stopwords=False)
        tokens_no_stopwords = tokenizer_no_stopwords.tokenize(self.sample_text)
        
        # Should have fewer tokens with stopword removal
        self.assertLessEqual(len(tokens_with_stopwords), len(tokens_no_stopwords))
    
    def test_sentence_tokenizer(self):
        """Test sentence tokenizer."""
        tokenizer = SentenceTokenizer()
        sentences = tokenizer.tokenize(self.sample_text)
        count = tokenizer.count(self.sample_text)
        
        self.assertIsInstance(sentences, list)
        self.assertEqual(len(sentences), count)
        self.assertEqual(count, 2)  # Two sentences in sample text
    
    def test_approximate_tokenizer(self):
        """Test approximate tokenizer."""
        tokenizer = ApproximateTokenizer()
        count = tokenizer.count(self.sample_text)
        tokens = tokenizer.tokenize(self.sample_text)
        
        self.assertGreater(count, 0)
        self.assertIsInstance(tokens, list)
    
    def test_tokenizer_manager(self):
        """Test tokenizer manager."""
        manager = TokenizerManager()
        
        # Test available tokenizers
        tokenizers = manager.list_tokenizers()
        self.assertIn('whitespace', tokenizers)
        self.assertIn('regex', tokenizers)
        
        # Test tokenization
        tokens = manager.tokenize(self.sample_text, 'whitespace')
        self.assertIsInstance(tokens, list)
        
        # Test token counting
        count = manager.count_tokens(self.sample_text, 'regex')
        self.assertGreater(count, 0)
        
        # Test sentence operations
        sentences = manager.split_sentences(self.sample_text)
        self.assertEqual(len(sentences), 2)
        
        # Test text analysis
        analysis = manager.analyze_text(self.sample_text)
        self.assertIn('word_count', analysis)
        self.assertIn('sentence_count', analysis)
        self.assertIn('character_count', analysis)


class TestCacheManager(unittest.TestCase):
    """Test cache manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = CacheManager(ttl=1)  # 1 second TTL for testing
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        # Test put and get
        self.cache.put("key1", "value1")
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
        
        # Test non-existent key
        value = self.cache.get("nonexistent")
        self.assertIsNone(value)
    
    def test_cache_ttl(self):
        """Test cache TTL expiration."""
        self.cache.put("key1", "value1")
        
        # Should exist immediately
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
        
        # Wait for TTL expiration
        time.sleep(1.1)
        
        # Should be expired
        value = self.cache.get("key1")
        self.assertIsNone(value)
    
    def test_cache_clear(self):
        """Test cache clearing."""
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        # Verify items exist
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        
        # Clear cache
        self.cache.clear()
        
        # Verify items are gone
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_cache_size_limit(self):
        """Test cache size limitations."""
        small_cache = CacheManager(max_size=2, ttl=10)
        
        # Add items up to limit
        small_cache.put("key1", "value1")
        small_cache.put("key2", "value2")
        
        # Both should exist
        self.assertEqual(small_cache.get("key1"), "value1")
        self.assertEqual(small_cache.get("key2"), "value2")
        
        # Add third item (should evict oldest)
        small_cache.put("key3", "value3")
        
        # key1 should be evicted, others should remain
        self.assertIsNone(small_cache.get("key1"))
        self.assertEqual(small_cache.get("key2"), "value2")
        self.assertEqual(small_cache.get("key3"), "value3")
    
    def test_cache_stats(self):
        """Test cache statistics."""
        # Perform some operations
        self.cache.put("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertIn('size', stats)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('hit_rate_percent', stats)
        
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)


if __name__ == '__main__':
    unittest.main()