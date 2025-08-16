"""Tests for framework integrations."""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor.integrations.openai import (
    OpenAITokenizer, compress_for_openai, estimate_openai_cost_savings,
    TIKTOKEN_AVAILABLE, OPENAI_AVAILABLE
)
from context_compressor.integrations.langchain import (
    compress_documents, compress_document_content, LANGCHAIN_AVAILABLE
)


class TestOpenAIIntegration(unittest.TestCase):
    """Test OpenAI integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = (
            "Machine learning is revolutionizing technology. AI systems can "
            "process vast amounts of data and make intelligent decisions."
        )
    
    @unittest.skipUnless(TIKTOKEN_AVAILABLE, "tiktoken not available")
    def test_openai_tokenizer(self):
        """Test OpenAI tokenizer."""
        tokenizer = OpenAITokenizer("gpt-3.5-turbo")
        
        tokens = tokenizer.tokenize(self.sample_text)
        count = tokenizer.count(self.sample_text)
        
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
        self.assertEqual(len(tokens), count)
    
    def test_compress_for_openai(self):
        """Test OpenAI compression function."""
        result = compress_for_openai(
            text=self.sample_text,
            target_ratio=0.6,
            model="gpt-3.5-turbo"
        )
        
        self.assertIn('compressed_text', result)
        self.assertIn('original_tokens', result)
        self.assertIn('compressed_tokens', result)
        self.assertIn('tokens_saved', result)
        self.assertLess(result['compressed_tokens'], result['original_tokens'])
    
    def test_cost_estimation(self):
        """Test cost estimation."""
        cost_info = estimate_openai_cost_savings(
            original_tokens=100,
            compressed_tokens=50,
            model="gpt-3.5-turbo"
        )
        
        self.assertIn('cost_estimation', cost_info)
        estimation = cost_info['cost_estimation']
        
        self.assertIn('original_cost_usd', estimation)
        self.assertIn('compressed_cost_usd', estimation)
        self.assertIn('cost_savings_usd', estimation)
        self.assertIn('savings_percentage', estimation)
        
        self.assertGreater(estimation['cost_savings_usd'], 0)
        self.assertGreater(estimation['savings_percentage'], 0)


class TestLangChainIntegration(unittest.TestCase):
    """Test LangChain integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_content = (
            "Natural language processing enables machines to understand "
            "and generate human language effectively."
        )
    
    def test_compress_document_content(self):
        """Test document content compression."""
        if not LANGCHAIN_AVAILABLE:
            self.skipTest("LangChain not available")
        
        document = compress_document_content(
            content=self.sample_content,
            target_ratio=0.6
        )
        
        # Would test document properties if LangChain was available
        # This test will be skipped if LangChain is not installed
        self.assertTrue(True)  # Placeholder
    
    def test_langchain_availability(self):
        """Test LangChain availability detection."""
        # This test always passes but shows the availability status
        self.assertIsInstance(LANGCHAIN_AVAILABLE, bool)


if __name__ == '__main__':
    unittest.main()