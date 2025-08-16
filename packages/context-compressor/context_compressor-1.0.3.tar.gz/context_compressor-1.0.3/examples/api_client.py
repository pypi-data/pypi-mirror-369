#!/usr/bin/env python3
"""
API Client Examples for AI Context Compressor.

This script demonstrates how to interact with the Context Compressor REST API
using various HTTP clients and shows different API usage patterns.
"""

import sys
import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class ContextCompressorAPIClient:
    """
    Python client for Context Compressor REST API.
    
    This client provides a convenient interface for interacting with
    the Context Compressor API service.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API service
        """
        self.base_url = base_url.rstrip('/')
        
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests library is required. Install with: pip install requests"
            )
    
    def compress(
        self, 
        text: str, 
        target_ratio: float = 0.5,
        strategy: str = "auto",
        query: Optional[str] = None,
        evaluate_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Compress a single text.
        
        Args:
            text: Text to compress
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            query: Optional query for context-aware compression
            evaluate_quality: Whether to evaluate compression quality
            
        Returns:
            Dict[str, Any]: Compression result
        """
        payload = {
            "text": text,
            "target_ratio": target_ratio,
            "strategy": strategy,
            "evaluate_quality": evaluate_quality
        }
        
        if query:
            payload["query"] = query
        
        response = requests.post(
            f"{self.base_url}/compress",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    def compress_batch(
        self,
        texts: List[str],
        target_ratio: float = 0.5,
        strategy: str = "auto",
        query: Optional[str] = None,
        parallel: bool = True,
        evaluate_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Compress multiple texts in batch.
        
        Args:
            texts: List of texts to compress
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            query: Optional query for context-aware compression
            parallel: Whether to process texts in parallel
            evaluate_quality: Whether to evaluate compression quality
            
        Returns:
            Dict[str, Any]: Batch compression result
        """
        payload = {
            "texts": texts,
            "target_ratio": target_ratio,
            "strategy": strategy,
            "parallel": parallel,
            "evaluate_quality": evaluate_quality
        }
        
        if query:
            payload["query"] = query
        
        response = requests.post(
            f"{self.base_url}/compress/batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """
        List all available compression strategies.
        
        Returns:
            List[Dict[str, Any]]: List of strategy information
        """
        response = requests.get(f"{self.base_url}/strategies")
        response.raise_for_status()
        return response.json()
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get information about a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dict[str, Any]: Strategy information
        """
        response = requests.get(f"{self.base_url}/strategies/{strategy_name}")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Dict[str, Any]: Health information
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get API performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        response = requests.get(f"{self.base_url}/metrics")
        response.raise_for_status()
        return response.json()
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear the compression cache.
        
        Returns:
            Dict[str, Any]: Success message
        """
        response = requests.post(f"{self.base_url}/cache/clear")
        response.raise_for_status()
        return response.json()
    
    def reset_stats(self) -> Dict[str, Any]:
        """
        Reset compression statistics.
        
        Returns:
            Dict[str, Any]: Success message
        """
        response = requests.post(f"{self.base_url}/stats/reset")
        response.raise_for_status()
        return response.json()


class AsyncContextCompressorAPIClient:
    """
    Async Python client for Context Compressor REST API.
    
    This client provides async methods for high-performance API interactions.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize async API client.
        
        Args:
            base_url: Base URL of the API service
        """
        self.base_url = base_url.rstrip('/')
        
        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp library is required. Install with: pip install aiohttp"
            )
    
    async def compress(
        self, 
        text: str, 
        target_ratio: float = 0.5,
        strategy: str = "auto",
        query: Optional[str] = None,
        evaluate_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Async compress a single text.
        
        Args:
            text: Text to compress
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            query: Optional query for context-aware compression
            evaluate_quality: Whether to evaluate compression quality
            
        Returns:
            Dict[str, Any]: Compression result
        """
        payload = {
            "text": text,
            "target_ratio": target_ratio,
            "strategy": strategy,
            "evaluate_quality": evaluate_quality
        }
        
        if query:
            payload["query"] = query
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/compress",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def compress_batch(
        self,
        texts: List[str],
        target_ratio: float = 0.5,
        strategy: str = "auto",
        query: Optional[str] = None,
        parallel: bool = True,
        evaluate_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Async compress multiple texts in batch.
        
        Args:
            texts: List of texts to compress
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            query: Optional query for context-aware compression
            parallel: Whether to process texts in parallel
            evaluate_quality: Whether to evaluate compression quality
            
        Returns:
            Dict[str, Any]: Batch compression result
        """
        payload = {
            "texts": texts,
            "target_ratio": target_ratio,
            "strategy": strategy,
            "parallel": parallel,
            "evaluate_quality": evaluate_quality
        }
        
        if query:
            payload["query"] = query
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/compress/batch",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def concurrent_compress(
        self,
        texts: List[str],
        target_ratio: float = 0.5,
        strategy: str = "auto",
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Compress multiple texts concurrently using individual API calls.
        
        Args:
            texts: List of texts to compress
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List[Dict[str, Any]]: List of compression results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def compress_single(text: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.compress(
                    text=text,
                    target_ratio=target_ratio,
                    strategy=strategy
                )
        
        tasks = [compress_single(text) for text in texts]
        return await asyncio.gather(*tasks)


def demonstrate_basic_api_usage():
    """Demonstrate basic API usage with the sync client."""
    
    print("🔧 Basic API Usage Examples")
    print("-" * 30)
    
    if not REQUESTS_AVAILABLE:
        print("❌ requests library not available - skipping sync examples")
        return
    
    # Initialize client
    client = ContextCompressorAPIClient()
    
    try:
        # Test health check first
        health = client.health_check()
        print(f"✅ API is healthy - uptime: {health.get('uptime_seconds', 0):.1f}s")
        
        # List available strategies
        strategies = client.list_strategies()
        print(f"📋 Available strategies: {[s['name'] for s in strategies]}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - make sure the server is running:")
        print("   python -m src.context_compressor.api.main")
        print("   or: uvicorn src.context_compressor.api.main:app --reload")
        return
    except Exception as e:
        print(f"❌ API error: {e}")
        return
    
    # Sample text for compression
    sample_text = """
    Artificial intelligence has revolutionized the way we process and analyze data.
    Machine learning algorithms can identify complex patterns in massive datasets
    and make accurate predictions. Deep learning networks use multiple layers of
    neurons to solve sophisticated problems such as image recognition, natural
    language processing, and speech synthesis. The applications of AI span across
    healthcare, finance, transportation, education, and entertainment industries.
    Companies worldwide are investing heavily in AI research and development to
    gain competitive advantages and improve their products and services.
    """
    
    print(f"\n📄 Sample text ({len(sample_text.split())} words)")
    
    # 1. Basic compression
    print("\n1. Basic Compression")
    print("-" * 18)
    
    try:
        result = client.compress(
            text=sample_text,
            target_ratio=0.6,
            strategy="extractive"
        )
        
        print(f"   Original tokens: {result['original_tokens']}")
        print(f"   Compressed tokens: {result['compressed_tokens']}")
        print(f"   Tokens saved: {result['tokens_saved']}")
        print(f"   Actual ratio: {result['actual_ratio']:.1%}")
        print(f"   Processing time: {result['processing_time']:.3f}s")
        print(f"   Compressed text: '{result['compressed_text'][:100]}...'")
        
    except Exception as e:
        print(f"   ❌ Compression failed: {e}")
    
    # 2. Query-aware compression
    print("\n2. Query-Aware Compression")
    print("-" * 25)
    
    try:
        result = client.compress(
            text=sample_text,
            target_ratio=0.5,
            strategy="extractive",
            query="machine learning applications"
        )
        
        print(f"   Query: 'machine learning applications'")
        print(f"   Compressed tokens: {result['compressed_tokens']}")
        print(f"   Quality metrics: {result.get('quality_metrics', {})}")
        print(f"   Compressed text: '{result['compressed_text'][:120]}...'")
        
    except Exception as e:
        print(f"   ❌ Query-aware compression failed: {e}")
    
    # 3. Batch compression
    print("\n3. Batch Compression")
    print("-" * 18)
    
    batch_texts = [
        "Cloud computing provides scalable and flexible computing resources over the internet.",
        "Blockchain technology enables secure and decentralized transaction recording.",
        "Quantum computing leverages quantum mechanical phenomena for advanced computation."
    ]
    
    try:
        result = client.compress_batch(
            texts=batch_texts,
            target_ratio=0.6,
            parallel=True
        )
        
        print(f"   Texts processed: {len(result['results'])}")
        print(f"   Success rate: {result['success_rate']:.1%}")
        print(f"   Total tokens saved: {result['total_tokens_saved']}")
        print(f"   Processing time: {result['total_processing_time']:.3f}s")
        
        for i, item_result in enumerate(result['results']):
            print(f"     Text {i+1}: {item_result['tokens_saved']} tokens saved")
        
    except Exception as e:
        print(f"   ❌ Batch compression failed: {e}")
    
    # 4. Get metrics
    print("\n4. Performance Metrics")
    print("-" * 20)
    
    try:
        metrics = client.get_metrics()
        print(f"   Total compressions: {metrics['total_compressions']}")
        print(f"   Total tokens processed: {metrics['total_tokens_processed']}")
        print(f"   Total tokens saved: {metrics['total_tokens_saved']}")
        print(f"   Average compression ratio: {metrics['average_compression_ratio']:.1%}")
        print(f"   Cache hit rate: {metrics['cache_hit_rate']:.1%}")
        
    except Exception as e:
        print(f"   ❌ Failed to get metrics: {e}")


async def demonstrate_async_api_usage():
    """Demonstrate async API usage."""
    
    print("\n🚀 Async API Usage Examples")
    print("-" * 28)
    
    if not AIOHTTP_AVAILABLE:
        print("❌ aiohttp library not available - skipping async examples")
        return
    
    # Initialize async client
    client = AsyncContextCompressorAPIClient()
    
    # Sample texts for concurrent processing
    texts = [
        "Artificial intelligence is transforming industries through automation and data analysis.",
        "Machine learning algorithms enable computers to learn from data without explicit programming.",
        "Deep learning networks can process complex data patterns and make accurate predictions.",
        "Natural language processing allows machines to understand and generate human language.",
        "Computer vision systems can analyze and interpret visual information from images and videos."
    ]
    
    print(f"📦 Processing {len(texts)} texts concurrently...")
    
    try:
        # Test concurrent compression
        start_time = time.time()
        
        results = await client.concurrent_compress(
            texts=texts,
            target_ratio=0.6,
            max_concurrent=3
        )
        
        processing_time = time.time() - start_time
        
        print(f"✅ Concurrent processing completed in {processing_time:.3f}s")
        print(f"   Average per text: {processing_time / len(texts):.3f}s")
        
        total_tokens_saved = sum(result['tokens_saved'] for result in results)
        print(f"   Total tokens saved: {total_tokens_saved}")
        
        for i, result in enumerate(results):
            print(f"   Text {i+1}: {result['tokens_saved']} tokens saved "
                  f"({result['actual_ratio']:.1%} ratio)")
        
    except Exception as e:
        print(f"❌ Async compression failed: {e}")
    
    # Test batch vs concurrent comparison
    print(f"\n📊 Batch vs Concurrent Performance")
    print("-" * 35)
    
    try:
        # Batch processing
        start_time = time.time()
        batch_result = await client.compress_batch(
            texts=texts,
            target_ratio=0.6,
            parallel=True
        )
        batch_time = time.time() - start_time
        
        print(f"   Batch processing: {batch_time:.3f}s")
        print(f"   Tokens saved: {batch_result['total_tokens_saved']}")
        
        # Concurrent processing
        start_time = time.time()
        concurrent_results = await client.concurrent_compress(
            texts=texts,
            target_ratio=0.6,
            max_concurrent=3
        )
        concurrent_time = time.time() - start_time
        
        concurrent_tokens_saved = sum(r['tokens_saved'] for r in concurrent_results)
        
        print(f"   Concurrent processing: {concurrent_time:.3f}s")
        print(f"   Tokens saved: {concurrent_tokens_saved}")
        
        if batch_time > 0:
            speedup = batch_time / concurrent_time if concurrent_time > 0 else 1
            print(f"   Speedup: {speedup:.2f}x")
        
    except Exception as e:
        print(f"❌ Performance comparison failed: {e}")


def demonstrate_curl_examples():
    """Show equivalent curl command examples."""
    
    print("\n🌐 cURL Command Examples")
    print("-" * 24)
    
    base_url = "http://localhost:8000"
    
    print("1. Basic compression:")
    print("   curl -X POST \\")
    print(f"     {base_url}/compress \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"text\": \"Your text to compress here...\",")
    print("       \"target_ratio\": 0.6,")
    print("       \"strategy\": \"extractive\"")
    print("     }'")
    
    print("\n2. Query-aware compression:")
    print("   curl -X POST \\")
    print(f"     {base_url}/compress \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"text\": \"Your text to compress here...\",")
    print("       \"target_ratio\": 0.5,")
    print("       \"query\": \"specific topic\"")
    print("     }'")
    
    print("\n3. Batch compression:")
    print("   curl -X POST \\")
    print(f"     {base_url}/compress/batch \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"texts\": [\"Text 1\", \"Text 2\", \"Text 3\"],")
    print("       \"target_ratio\": 0.6,")
    print("       \"parallel\": true")
    print("     }'")
    
    print("\n4. List strategies:")
    print(f"   curl {base_url}/strategies")
    
    print("\n5. Health check:")
    print(f"   curl {base_url}/health")
    
    print("\n6. Get metrics:")
    print(f"   curl {base_url}/metrics")


def demonstrate_error_handling():
    """Demonstrate error handling with the API."""
    
    print("\n⚠️  Error Handling Examples")
    print("-" * 27)
    
    if not REQUESTS_AVAILABLE:
        print("❌ requests library not available - skipping error examples")
        return
    
    client = ContextCompressorAPIClient()
    
    # 1. Invalid compression ratio
    print("1. Invalid compression ratio:")
    try:
        result = client.compress(
            text="Sample text",
            target_ratio=1.5  # Invalid ratio > 1.0
        )
    except requests.exceptions.HTTPError as e:
        print(f"   ✅ Caught expected error: {e.response.status_code}")
        print(f"   Error detail: {e.response.json().get('detail', 'Unknown error')}")
    
    # 2. Empty text
    print("\n2. Empty text:")
    try:
        result = client.compress(text="")
    except requests.exceptions.HTTPError as e:
        print(f"   ✅ Caught expected error: {e.response.status_code}")
        print(f"   Error detail: {e.response.json().get('detail', 'Unknown error')}")
    
    # 3. Unknown strategy
    print("\n3. Unknown strategy:")
    try:
        result = client.compress(
            text="Sample text",
            strategy="unknown_strategy"
        )
    except requests.exceptions.HTTPError as e:
        print(f"   ✅ Caught expected error: {e.response.status_code}")
        print(f"   Error detail: {e.response.json().get('detail', 'Unknown error')}")
    
    # 4. Connection error (assuming server is down)
    print("\n4. Connection handling:")
    wrong_client = ContextCompressorAPIClient(base_url="http://localhost:9999")
    try:
        result = wrong_client.health_check()
    except requests.exceptions.ConnectionError:
        print("   ✅ Caught connection error (expected if server not on port 9999)")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")


def main():
    """Run all API client examples."""
    
    print("🌐 AI Context Compressor - API Client Examples")
    print("=" * 50)
    
    print("\n💡 Before running these examples:")
    print("   1. Start the API server:")
    print("      python -m src.context_compressor.api.main")
    print("   2. Or with uvicorn:")
    print("      uvicorn src.context_compressor.api.main:app --reload")
    print("   3. API will be available at http://localhost:8000")
    print("   4. Interactive docs at http://localhost:8000/docs")
    
    # Demonstrate different client approaches
    demonstrate_basic_api_usage()
    
    # Async examples
    if AIOHTTP_AVAILABLE:
        try:
            asyncio.run(demonstrate_async_api_usage())
        except Exception as e:
            print(f"❌ Async examples failed: {e}")
    
    # Show curl equivalents
    demonstrate_curl_examples()
    
    # Error handling
    demonstrate_error_handling()
    
    print("\n✅ API client examples completed!")
    
    print("\n📚 Additional Resources:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • ReDoc Documentation: http://localhost:8000/redoc")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Metrics: http://localhost:8000/metrics")
    
    print("\n🔧 Integration Tips:")
    print("   • Always handle connection errors gracefully")
    print("   • Use appropriate timeouts for your use case")
    print("   • Monitor API metrics for performance optimization")
    print("   • Consider using async clients for high-throughput scenarios")
    print("   • Implement retry logic for transient failures")
    print("   • Cache frequently used compression results")
    
    print("\n⚙️  Production Considerations:")
    print("   • Use environment variables for API endpoints")
    print("   • Implement proper authentication if needed")
    print("   • Add request/response logging")
    print("   • Set up monitoring and alerting")
    print("   • Use connection pooling for better performance")
    print("   • Consider rate limiting and throttling")


if __name__ == "__main__":
    main()