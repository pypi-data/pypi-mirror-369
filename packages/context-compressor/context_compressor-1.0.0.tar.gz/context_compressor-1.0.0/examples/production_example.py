#!/usr/bin/env python3
"""
Production-Ready Context Compressor Example.

This example demonstrates how to use Context Compressor in a production environment
with proper error handling, monitoring, and optimization techniques.
"""

import sys
import os
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CompressionRequest:
    """Production compression request model."""
    id: str
    text: str
    target_ratio: float
    query: Optional[str] = None
    strategy: str = "auto"
    priority: int = 1  # 1=high, 2=medium, 3=low

@dataclass
class CompressionResponse:
    """Production compression response model."""
    request_id: str
    success: bool
    compressed_text: Optional[str] = None
    original_length: int = 0
    compressed_length: int = 0
    compression_ratio: float = 0.0
    quality_score: float = 0.0
    processing_time: float = 0.0
    error_message: Optional[str] = None

class ProductionCompressor:
    """Production-ready Context Compressor with monitoring and optimization."""
    
    def __init__(self, 
                 max_workers: int = 4,
                 enable_monitoring: bool = True,
                 cache_size: int = 1000,
                 timeout_seconds: int = 30):
        """Initialize production compressor."""
        self.compressor = ContextCompressor(
            enable_caching=True,
            cache_ttl=3600,  # 1 hour
            enable_quality_evaluation=True,
            max_workers=max_workers
        )
        
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.enable_monitoring = enable_monitoring
        
        # Monitoring metrics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'total_tokens_saved': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        logger.info(f"ProductionCompressor initialized with {max_workers} workers")
    
    def compress_single(self, request: CompressionRequest) -> CompressionResponse:
        """Compress a single text with full error handling and monitoring."""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Validate request
            if not request.text.strip():
                raise ValueError("Empty text provided")
            
            if not 0.1 <= request.target_ratio <= 0.9:
                raise ValueError(f"Invalid target_ratio: {request.target_ratio}")
            
            # Perform compression
            result = self.compressor.compress(
                text=request.text,
                target_ratio=request.target_ratio,
                query=request.query,
                strategy=request.strategy
            )
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self.stats['successful_requests'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['total_tokens_saved'] += result.tokens_saved
            
            # Check cache performance
            if self.compressor.cache_manager:
                self.stats['cache_hits'] = self.compressor.cache_manager.hits
                self.stats['cache_misses'] = self.compressor.cache_manager.misses
            
            response = CompressionResponse(
                request_id=request.id,
                success=True,
                compressed_text=result.compressed_text,
                original_length=len(request.text),
                compressed_length=len(result.compressed_text),
                compression_ratio=result.actual_ratio,
                quality_score=result.quality_metrics.overall_score if result.quality_metrics else 0.0,
                processing_time=processing_time
            )
            
            if self.enable_monitoring:
                logger.info(f"Request {request.id}: {result.actual_ratio:.1%} compression in {processing_time:.3f}s")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.stats['failed_requests'] += 1
            
            logger.error(f"Request {request.id} failed: {str(e)}")
            
            return CompressionResponse(
                request_id=request.id,
                success=False,
                original_length=len(request.text) if request.text else 0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def compress_batch(self, requests: List[CompressionRequest]) -> List[CompressionResponse]:
        """Compress multiple texts with optimized parallel processing."""
        if not requests:
            return []
        
        logger.info(f"Processing batch of {len(requests)} requests")
        
        # Sort by priority (optional optimization)
        sorted_requests = sorted(requests, key=lambda x: x.priority)
        
        responses = []
        
        # Process in parallel with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_request = {
                executor.submit(self.compress_single, req): req 
                for req in sorted_requests
            }
            
            for future in future_to_request:
                try:
                    response = future.result(timeout=self.timeout_seconds)
                    responses.append(response)
                except Exception as e:
                    request = future_to_request[future]
                    logger.error(f"Batch request {request.id} failed: {str(e)}")
                    
                    responses.append(CompressionResponse(
                        request_id=request.id,
                        success=False,
                        error_message=f"Timeout or error: {str(e)}"
                    ))
        
        # Sort responses by original request order
        request_id_to_index = {req.id: i for i, req in enumerate(requests)}
        responses.sort(key=lambda r: request_id_to_index.get(r.request_id, 999))
        
        successful = sum(1 for r in responses if r.success)
        logger.info(f"Batch completed: {successful}/{len(responses)} successful")
        
        return responses
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        total_requests = self.stats['total_requests']
        
        if total_requests == 0:
            return self.stats
        
        avg_processing_time = self.stats['total_processing_time'] / total_requests
        success_rate = self.stats['successful_requests'] / total_requests
        
        cache_stats = {}
        if self.compressor.cache_manager:
            total_cache_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            cache_hit_rate = self.stats['cache_hits'] / total_cache_requests if total_cache_requests > 0 else 0
            cache_stats = {
                'cache_hit_rate': cache_hit_rate,
                'cache_size': self.compressor.cache_manager.size,
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses']
            }
        
        return {
            **self.stats,
            'average_processing_time': avg_processing_time,
            'success_rate': success_rate,
            'requests_per_second': total_requests / self.stats['total_processing_time'] if self.stats['total_processing_time'] > 0 else 0,
            **cache_stats
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        try:
            # Test basic compression
            test_text = "This is a health check test for the compression system."
            test_request = CompressionRequest(
                id="health_check",
                text=test_text,
                target_ratio=0.8
            )
            
            response = self.compress_single(test_request)
            health_status['checks']['compression'] = {
                'status': 'ok' if response.success else 'error',
                'details': response.error_message if not response.success else 'Compression working'
            }
            
            # Check cache if enabled
            if self.compressor.cache_manager:
                health_status['checks']['cache'] = {
                    'status': 'ok',
                    'size': self.compressor.cache_manager.size,
                    'hit_rate': self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
                }
            
            # Check available strategies
            strategies = self.compressor.get_available_strategies()
            health_status['checks']['strategies'] = {
                'status': 'ok' if strategies else 'error',
                'count': len(strategies),
                'available': strategies
            }
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status

def demonstrate_basic_usage():
    """Demonstrate basic production usage."""
    print("🚀 Basic Production Usage")
    print("-" * 25)
    
    compressor = ProductionCompressor(max_workers=2)
    
    # Single request
    request = CompressionRequest(
        id="demo_001",
        text="""
        Artificial Intelligence (AI) is revolutionizing industries through machine learning,
        natural language processing, and computer vision. These technologies enable automated
        decision-making, predictive analytics, and intelligent automation across healthcare,
        finance, transportation, and entertainment sectors. Companies are investing heavily
        in AI research and development to gain competitive advantages and improve efficiency.
        The future of AI promises even more sophisticated applications including autonomous
        vehicles, personalized medicine, and advanced robotics systems.
        """,
        target_ratio=0.5,
        query="machine learning applications",
        priority=1
    )
    
    response = compressor.compress_single(request)
    
    if response.success:
        print(f"✓ Request {response.request_id} completed successfully")
        print(f"  Original: {response.original_length} characters")
        print(f"  Compressed: {response.compressed_length} characters")
        print(f"  Compression: {response.compression_ratio:.1%}")
        print(f"  Quality: {response.quality_score:.3f}")
        print(f"  Time: {response.processing_time:.3f}s")
        print(f"  Result: {response.compressed_text[:100]}...")
    else:
        print(f"✗ Request {response.request_id} failed: {response.error_message}")

def demonstrate_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\n🔄 Batch Processing")
    print("-" * 20)
    
    compressor = ProductionCompressor(max_workers=4)
    
    # Create multiple requests
    sample_texts = [
        "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning approaches.",
        "Natural language processing involves understanding and generating human language using computational methods and AI techniques.",
        "Computer vision enables machines to interpret and understand visual information from the world, including images and videos.",
        "Deep learning uses neural networks with multiple layers to learn complex patterns and representations from large datasets.",
        "Robotics combines AI, engineering, and computer science to create intelligent machines that can perform tasks autonomously."
    ]
    
    requests = [
        CompressionRequest(
            id=f"batch_{i:03d}",
            text=text,
            target_ratio=0.6,
            priority=1 if i < 2 else 2  # First two are high priority
        )
        for i, text in enumerate(sample_texts)
    ]
    
    # Process batch
    start_time = time.time()
    responses = compressor.compress_batch(requests)
    batch_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in responses if r.success]
    failed = [r for r in responses if not r.success]
    
    print(f"Batch Results:")
    print(f"  Total requests: {len(requests)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Batch time: {batch_time:.3f}s")
    print(f"  Throughput: {len(requests)/batch_time:.1f} requests/second")
    
    if successful:
        avg_compression = sum(r.compression_ratio for r in successful) / len(successful)
        avg_quality = sum(r.quality_score for r in successful) / len(successful)
        print(f"  Average compression: {avg_compression:.1%}")
        print(f"  Average quality: {avg_quality:.3f}")

def demonstrate_monitoring():
    """Demonstrate monitoring and statistics."""
    print("\n📊 Monitoring & Statistics")
    print("-" * 28)
    
    compressor = ProductionCompressor(enable_monitoring=True)
    
    # Generate some activity
    test_requests = [
        CompressionRequest(f"monitor_{i}", f"Test text {i} " * 20, 0.5)
        for i in range(10)
    ]
    
    compressor.compress_batch(test_requests)
    
    # Get performance statistics
    stats = compressor.get_performance_stats()
    
    print("Performance Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

def demonstrate_health_check():
    """Demonstrate health check functionality."""
    print("\n🏥 Health Check")
    print("-" * 15)
    
    compressor = ProductionCompressor()
    health = compressor.health_check()
    
    print(f"Overall Status: {health['status'].upper()}")
    print("Detailed Checks:")
    
    for check_name, check_result in health.get('checks', {}).items():
        status = check_result.get('status', 'unknown')
        print(f"  {check_name}: {status.upper()}")
        
        if 'details' in check_result:
            print(f"    Details: {check_result['details']}")
        
        if check_name == 'cache' and 'size' in check_result:
            print(f"    Cache size: {check_result['size']}")
            print(f"    Hit rate: {check_result['hit_rate']:.1%}")
        
        if check_name == 'strategies' and 'available' in check_result:
            print(f"    Available strategies: {check_result['available']}")

def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n⚠️  Error Handling")
    print("-" * 18)
    
    compressor = ProductionCompressor()
    
    # Test various error conditions
    error_requests = [
        CompressionRequest("empty_text", "", 0.5),  # Empty text
        CompressionRequest("invalid_ratio", "Valid text", 1.5),  # Invalid ratio
        CompressionRequest("very_short", "Hi", 0.3),  # Very short text
    ]
    
    for request in error_requests:
        response = compressor.compress_single(request)
        
        if response.success:
            print(f"✓ {request.id}: Unexpected success")
        else:
            print(f"✗ {request.id}: {response.error_message}")

def main():
    """Run all production demonstrations."""
    print("📦 AI Context Compressor - Production Example")
    print("=" * 50)
    
    try:
        demonstrate_basic_usage()
        demonstrate_batch_processing()
        demonstrate_monitoring()
        demonstrate_health_check()
        demonstrate_error_handling()
        
        print("\n✅ Production example completed!")
        print("\n💡 Key Production Features:")
        print("   • Comprehensive error handling")
        print("   • Performance monitoring and statistics")
        print("   • Health check endpoints")
        print("   • Parallel batch processing")
        print("   • Request/response models")
        print("   • Timeout protection")
        print("   • Priority-based processing")
        
    except Exception as e:
        logger.error(f"Production example failed: {str(e)}")
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()