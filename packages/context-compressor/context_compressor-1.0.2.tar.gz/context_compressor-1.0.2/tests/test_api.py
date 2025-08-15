"""Tests for API endpoints."""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from fastapi.testclient import TestClient
    from context_compressor.api.main import app, FASTAPI_AVAILABLE
    FASTAPI_TEST_AVAILABLE = FASTAPI_AVAILABLE
except ImportError:
    FASTAPI_TEST_AVAILABLE = False
    TestClient = None
    app = None


@unittest.skipUnless(FASTAPI_TEST_AVAILABLE, "FastAPI not available")
class TestAPI(unittest.TestCase):
    """Test REST API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        if FASTAPI_TEST_AVAILABLE:
            self.client = TestClient(app)
        self.sample_text = (
            "Machine learning algorithms can analyze large datasets to "
            "identify patterns and make predictions about future outcomes."
        )
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("available_strategies", data)
    
    def test_compress_endpoint(self):
        """Test single text compression endpoint."""
        payload = {
            "text": self.sample_text,
            "target_ratio": 0.6,
            "strategy": "extractive"
        }
        
        response = self.client.post("/compress", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("compressed_text", data)
        self.assertIn("original_tokens", data)
        self.assertIn("compressed_tokens", data)
        self.assertIn("tokens_saved", data)
        
        self.assertLess(data["compressed_tokens"], data["original_tokens"])
    
    def test_compress_with_query(self):
        """Test compression with query."""
        payload = {
            "text": self.sample_text,
            "target_ratio": 0.5,
            "query": "machine learning patterns"
        }
        
        response = self.client.post("/compress", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("compressed_text", data)
        self.assertIn("machine", data["compressed_text"].lower())
    
    def test_batch_compress_endpoint(self):
        """Test batch compression endpoint."""
        texts = [
            "First text about AI technology and its revolutionary impact on modern society. Artificial intelligence systems are being deployed across various industries to automate processes and improve decision-making capabilities.",
            "Second text about machine learning algorithms and their applications in predictive analytics. These powerful tools can analyze historical data patterns to forecast future trends and outcomes with remarkable accuracy.",
            "Third text about data science methodologies used in business intelligence. Data scientists combine statistical analysis with domain expertise to extract valuable insights from complex datasets and drive strategic decisions."
        ]
        
        payload = {
            "texts": texts,
            "target_ratio": 0.6,
            "parallel": True
        }
        
        response = self.client.post("/compress/batch", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 3)
        self.assertIn("total_tokens_saved", data)
    
    def test_strategies_endpoint(self):
        """Test strategies listing endpoint."""
        response = self.client.get("/strategies")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check strategy structure
        strategy = data[0]
        self.assertIn("name", strategy)
        self.assertIn("description", strategy)
        self.assertIn("version", strategy)
    
    def test_strategy_info_endpoint(self):
        """Test individual strategy info endpoint."""
        response = self.client.get("/strategies/extractive")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["name"], "extractive")
        self.assertIn("description", data)
        self.assertIn("version", data)
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        # Perform some compressions first
        payload = {"text": self.sample_text, "target_ratio": 0.5}
        self.client.post("/compress", json=payload)
        
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("total_compressions", data)
        self.assertIn("uptime_seconds", data)
    
    def test_invalid_requests(self):
        """Test invalid request handling."""
        # Empty text
        response = self.client.post("/compress", json={
            "text": "",
            "target_ratio": 0.5
        })
        self.assertEqual(response.status_code, 400)
        
        # Invalid ratio
        response = self.client.post("/compress", json={
            "text": self.sample_text,
            "target_ratio": 1.5
        })
        self.assertEqual(response.status_code, 400)
        
        # Unknown strategy
        response = self.client.get("/strategies/nonexistent")
        self.assertEqual(response.status_code, 404)
    
    def test_cache_operations(self):
        """Test cache management endpoints."""
        # Clear cache
        response = self.client.post("/cache/clear")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("message", data)
        
        # Reset stats
        response = self.client.post("/stats/reset")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("message", data)


if __name__ == '__main__':
    unittest.main()