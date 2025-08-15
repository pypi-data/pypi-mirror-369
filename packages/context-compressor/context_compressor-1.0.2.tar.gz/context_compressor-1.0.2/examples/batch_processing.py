#!/usr/bin/env python3
"""
Batch Processing Examples for AI Context Compressor.

This script demonstrates how to efficiently process multiple texts using
batch operations with parallel execution and performance optimization.
"""

import time
from typing import List
import sys
import os

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor


def main():
    """Run batch processing examples."""
    
    print("🔄 AI Context Compressor - Batch Processing Examples")
    print("=" * 55)
    
    # Sample texts for batch processing
    sample_texts = [
        """
        Artificial Intelligence has revolutionized many industries in recent years. 
        Machine learning algorithms can now process vast amounts of data to identify 
        patterns and make predictions. Deep learning, a subset of machine learning, 
        uses neural networks with multiple layers to solve complex problems. This 
        technology has applications in image recognition, natural language processing, 
        and autonomous vehicles. Companies across various sectors are investing heavily 
        in AI research and development to stay competitive in the digital economy.
        """,
        """
        Climate change represents one of the most significant challenges facing humanity 
        today. Rising global temperatures are causing ice caps to melt, sea levels to 
        rise, and weather patterns to become more extreme. Scientists around the world 
        are studying the effects of greenhouse gas emissions on our planet's atmosphere. 
        Renewable energy sources like solar and wind power offer promising solutions 
        to reduce our carbon footprint. Governments and organizations must work together 
        to implement sustainable practices and policies to combat climate change.
        """,
        """
        The healthcare industry is undergoing a digital transformation with the adoption 
        of electronic health records, telemedicine, and AI-powered diagnostic tools. 
        Patients can now consult with doctors remotely, access their medical records 
        online, and receive personalized treatment recommendations. Wearable devices 
        monitor vital signs and track fitness metrics, providing valuable health insights. 
        Medical researchers are using big data analytics to develop new treatments and 
        drugs. These technological advances are making healthcare more accessible and 
        efficient for people worldwide.
        """,
        """
        Space exploration continues to capture the imagination of scientists and the 
        public alike. Recent missions to Mars have provided valuable insights into 
        the Red Planet's geology and potential for supporting life. Private companies 
        are now joining government agencies in developing spacecraft and launch 
        technologies. The International Space Station serves as a laboratory for 
        conducting experiments in microgravity. Future missions plan to establish 
        permanent bases on the Moon and Mars, paving the way for human colonization 
        of other planets.
        """,
        """
        Cryptocurrency and blockchain technology have disrupted traditional financial 
        systems and created new opportunities for digital transactions. Bitcoin, the 
        first cryptocurrency, introduced the concept of decentralized digital currency. 
        Blockchain networks provide secure, transparent, and immutable transaction 
        records without the need for central authorities. Smart contracts automate 
        business processes and reduce the need for intermediaries. While regulatory 
        challenges remain, many institutions are exploring the potential of digital 
        assets and distributed ledger technologies.
        """,
        """
        Education is being transformed by digital learning platforms and online resources. 
        Students can access courses from prestigious universities around the world through 
        massive open online courses (MOOCs). Virtual and augmented reality technologies 
        are creating immersive learning experiences that make complex concepts easier to 
        understand. Artificial intelligence is personalizing education by adapting to 
        individual learning styles and providing customized feedback. These innovations 
        are making quality education more accessible and flexible for learners of all ages.
        """
    ]
    
    # Initialize the compressor
    print("\n1. Initializing Context Compressor...")
    compressor = ContextCompressor()
    
    # Basic batch processing
    print("\n2. Basic Batch Processing")
    print("-" * 30)
    
    start_time = time.time()
    batch_result = compressor.compress_batch(
        texts=sample_texts,
        target_ratio=0.5,
        parallel=True
    )
    processing_time = time.time() - start_time
    
    print(f"✅ Processed {len(batch_result.results)} texts successfully")
    print(f"⏱️  Total processing time: {processing_time:.3f} seconds")
    print(f"📊 Success rate: {batch_result.success_rate:.1%}")
    print(f"📈 Average compression ratio: {batch_result.average_compression_ratio:.1%}")
    print(f"💾 Total tokens saved: {batch_result.total_tokens_saved}")
    
    if batch_result.failed_items:
        print(f"❌ Failed items: {len(batch_result.failed_items)}")
        for failed in batch_result.failed_items:
            print(f"   - Text {failed['index']}: {failed['error']}")
    
    # Compare serial vs parallel processing
    print("\n3. Serial vs Parallel Processing Comparison")
    print("-" * 45)
    
    # Test with smaller subset for timing comparison
    test_texts = sample_texts[:3]
    
    # Serial processing
    start_time = time.time()
    serial_result = compressor.compress_batch(
        texts=test_texts,
        target_ratio=0.6,
        parallel=False
    )
    serial_time = time.time() - start_time
    
    # Parallel processing  
    start_time = time.time()
    parallel_result = compressor.compress_batch(
        texts=test_texts,
        target_ratio=0.6,
        parallel=True
    )
    parallel_time = time.time() - start_time
    
    print(f"📝 Processing {len(test_texts)} texts:")
    print(f"   Serial:   {serial_time:.3f}s")
    print(f"   Parallel: {parallel_time:.3f}s")
    print(f"   Speedup:  {serial_time/parallel_time:.1f}x" if parallel_time > 0 else "   Speedup: N/A")
    
    # Different compression ratios for batch
    print("\n4. Batch Processing with Different Ratios")
    print("-" * 40)
    
    ratios = [0.3, 0.5, 0.7]
    
    for ratio in ratios:
        start_time = time.time()
        result = compressor.compress_batch(
            texts=sample_texts[:4],  # Use first 4 texts
            target_ratio=ratio,
            parallel=True
        )
        processing_time = time.time() - start_time
        
        print(f"Target {ratio:.1%}: {result.average_compression_ratio:.1%} actual, "
              f"{result.total_tokens_saved} tokens saved, {processing_time:.3f}s")
    
    # Query-aware batch processing
    print("\n5. Query-Aware Batch Processing")
    print("-" * 35)
    
    queries = [
        "artificial intelligence and machine learning",
        "climate change and environmental issues", 
        "healthcare technology innovations",
        "space exploration missions"
    ]
    
    for query in queries:
        result = compressor.compress_batch(
            texts=sample_texts[:4],
            target_ratio=0.4,
            query=query,
            parallel=True
        )
        
        print(f"\nQuery: '{query}'")
        print(f"Results: {len(result.results)} texts processed")
        print(f"Average ratio: {result.average_compression_ratio:.1%}")
        print(f"Sample compressed text: '{result.results[0].compressed_text[:100]}...'")
    
    # Batch processing with quality evaluation
    print("\n6. Batch Processing with Quality Evaluation")
    print("-" * 42)
    
    quality_result = compressor.compress_batch(
        texts=sample_texts[:3],
        target_ratio=0.5,
        evaluate_quality=True,
        parallel=True
    )
    
    print(f"Quality-evaluated batch results:")
    for i, result in enumerate(quality_result.results):
        if result.quality_metrics:
            print(f"  Text {i+1}:")
            print(f"    Overall quality: {result.quality_metrics.overall_score:.3f}")
            print(f"    ROUGE-L: {result.quality_metrics.rouge_l:.3f}")
            print(f"    Semantic similarity: {result.quality_metrics.semantic_similarity:.3f}")
            print(f"    Entity preservation: {result.quality_metrics.entity_preservation_rate:.3f}")
    
    if quality_result.average_quality_score:
        print(f"\n📊 Average quality score: {quality_result.average_quality_score:.3f}")
    
    # Error handling example
    print("\n7. Batch Processing with Error Handling")
    print("-" * 40)
    
    # Include some problematic texts
    mixed_texts = [
        sample_texts[0],  # Good text
        "",              # Empty text
        "Short",         # Too short text
        sample_texts[1], # Good text
        "A" * 10000      # Very long text
    ]
    
    error_result = compressor.compress_batch(
        texts=mixed_texts,
        target_ratio=0.5,
        parallel=True
    )
    
    print(f"Mixed batch results:")
    print(f"  ✅ Successful: {len(error_result.results)}")
    print(f"  ❌ Failed: {len(error_result.failed_items)}")
    print(f"  📈 Success rate: {error_result.success_rate:.1%}")
    
    if error_result.failed_items:
        print(f"\nFailed items:")
        for failed in error_result.failed_items:
            print(f"  - Text {failed['index']}: {failed['error']}")
    
    # Performance optimization tips
    print("\n8. Performance Optimization Tips")
    print("-" * 35)
    
    print("💡 Tips for optimal batch processing:")
    print("   1. Use parallel=True for multiple texts (default)")
    print("   2. Process similar-length texts together")
    print("   3. Adjust max_workers based on your system")
    print("   4. Use caching for repeated compressions")
    print("   5. Consider disabling quality evaluation for speed")
    
    # Large batch simulation
    print("\n9. Large Batch Processing Simulation")
    print("-" * 38)
    
    # Create a larger batch by repeating texts
    large_batch = sample_texts * 3  # 18 texts total
    
    start_time = time.time()
    large_result = compressor.compress_batch(
        texts=large_batch,
        target_ratio=0.5,
        parallel=True,
        max_workers=4  # Limit workers
    )
    large_processing_time = time.time() - start_time
    
    print(f"Large batch processing ({len(large_batch)} texts):")
    print(f"  ⏱️  Processing time: {large_processing_time:.3f}s")
    print(f"  📊 Success rate: {large_result.success_rate:.1%}")
    print(f"  📈 Avg compression: {large_result.average_compression_ratio:.1%}")
    print(f"  💾 Total tokens saved: {large_result.total_tokens_saved}")
    print(f"  ⚡ Throughput: {len(large_batch)/large_processing_time:.1f} texts/second")
    
    # Cache performance with batch
    print("\n10. Cache Performance in Batch Processing")
    print("-" * 42)
    
    # First batch (cache misses)
    start_time = time.time()
    first_batch = compressor.compress_batch(
        texts=sample_texts[:3],
        target_ratio=0.5,
        use_cache=True
    )
    first_time = time.time() - start_time
    
    # Second batch (cache hits - same texts)
    start_time = time.time()  
    second_batch = compressor.compress_batch(
        texts=sample_texts[:3],
        target_ratio=0.5,
        use_cache=True
    )
    second_time = time.time() - start_time
    
    stats = compressor.get_stats()
    
    print(f"Cache performance:")
    print(f"  First batch (cache misses):  {first_time:.3f}s")
    print(f"  Second batch (cache hits):   {second_time:.3f}s")
    print(f"  Speedup from caching:        {first_time/second_time:.1f}x" if second_time > 0 else "  Speedup: N/A")
    print(f"  Cache hit rate:              {stats['cache_hit_rate']:.1f}%")
    
    print("\n✅ All batch processing examples completed successfully!")
    
    print("\n💡 Key Takeaways:")
    print("   • Batch processing is highly efficient for multiple texts")
    print("   • Parallel processing provides significant speedups")
    print("   • Query-aware compression works great in batch mode")
    print("   • Error handling ensures robust processing")
    print("   • Caching dramatically improves performance for repeated content")
    print("   • Quality evaluation can be enabled/disabled as needed")


if __name__ == "__main__":
    main()