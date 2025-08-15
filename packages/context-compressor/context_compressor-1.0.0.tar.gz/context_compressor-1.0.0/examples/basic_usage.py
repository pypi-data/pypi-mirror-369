#!/usr/bin/env python3
"""
Basic usage examples for Context Compressor.

This script demonstrates the core functionality of the context compression package.
"""

import sys
import os

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor

def main():
    """Run basic usage examples."""
    
    print("🚀 Context Compressor - Basic Usage Examples")
    print("=" * 50)
    
    # Sample text for compression
    sample_text = """
    Artificial Intelligence (AI) represents one of the most significant technological 
    advances of the 21st century. It encompasses a broad range of techniques and 
    methodologies designed to enable machines to perform tasks that traditionally 
    required human intelligence. These tasks include learning from data, reasoning 
    about complex problems, making decisions under uncertainty, understanding natural 
    language, recognizing patterns in visual data, and adapting to new situations.
    
    The field of AI has its roots in the 1950s, when pioneers like Alan Turing and 
    John McCarthy began exploring the possibility of creating intelligent machines. 
    Over the decades, AI has evolved through several phases, including the early 
    symbolic AI era, the knowledge-based systems of the 1980s, and the current 
    machine learning revolution powered by deep neural networks and big data.
    
    Machine learning, a subset of AI, has become particularly prominent in recent years. 
    It enables computers to learn patterns from data without being explicitly programmed 
    for every scenario. Deep learning, a subset of machine learning inspired by the 
    structure of the human brain, has achieved remarkable success in areas such as 
    computer vision, natural language processing, and speech recognition.
    
    Today, AI applications are ubiquitous in our daily lives. From recommendation 
    systems on streaming platforms and e-commerce sites to virtual assistants in 
    our smartphones, AI technologies have become integral to modern digital experiences. 
    In healthcare, AI assists in medical diagnosis and drug discovery. In finance, 
    it powers algorithmic trading and fraud detection. In transportation, it enables 
    autonomous vehicles and optimizes traffic flow.
    """
    
    # Initialize the compressor
    print("\n1. Initializing Context Compressor...")
    compressor = ContextCompressor()
    
    # Basic compression example
    print("\n2. Basic Text Compression")
    print("-" * 30)
    
    result = compressor.compress(
        text=sample_text.strip(),
        target_ratio=0.5
    )
    
    print(f"Original text length: {len(sample_text.split())} words")
    print(f"Compressed text length: {len(result.compressed_text.split())} words")
    print(f"Actual compression ratio: {result.actual_ratio:.1%}")
    print(f"Tokens saved: {result.tokens_saved}")
    print(f"Processing time: {result.processing_time:.3f} seconds")
    
    print(f"\nOriginal text (first 200 chars):")
    print(f"'{sample_text.strip()[:200]}...'")
    print(f"\nCompressed text:")
    print(f"'{result.compressed_text}'")
    
    # Different compression ratios
    print("\n3. Different Compression Ratios")
    print("-" * 35)
    
    ratios = [0.3, 0.5, 0.7]
    
    for ratio in ratios:
        result = compressor.compress(sample_text.strip(), target_ratio=ratio)
        print(f"Target: {ratio:.1%} | Actual: {result.actual_ratio:.1%} | "
              f"Words: {result.original_tokens} → {result.compressed_tokens} | "
              f"Saved: {result.tokens_saved}")
    
    # Query-aware compression
    print("\n4. Query-Aware Compression")
    print("-" * 30)
    
    queries = [
        "machine learning applications",
        "AI history and development",
        "healthcare and medical AI"
    ]
    
    for query in queries:
        result = compressor.compress(
            text=sample_text.strip(),
            target_ratio=0.4,
            query=query
        )
        
        print(f"\nQuery: '{query}'")
        print(f"Compressed text: '{result.compressed_text[:150]}...'")
        print(f"Compression ratio: {result.actual_ratio:.1%}")
    
    # Quality evaluation
    print("\n5. Quality Evaluation")
    print("-" * 25)
    
    result = compressor.compress(
        text=sample_text.strip(),
        target_ratio=0.5,
        evaluate_quality=True
    )
    
    if result.quality_metrics:
        metrics = result.quality_metrics
        print(f"Overall Quality Score: {metrics.overall_score:.3f}")
        print(f"Semantic Similarity: {metrics.semantic_similarity:.3f}")
        print(f"ROUGE-1: {metrics.rouge_1:.3f}")
        print(f"ROUGE-2: {metrics.rouge_2:.3f}")
        print(f"ROUGE-L: {metrics.rouge_l:.3f}")
        print(f"Entity Preservation: {metrics.entity_preservation_rate:.3f}")
        print(f"Readability Score: {metrics.readability_score:.1f}")
    
    # Strategy information
    print("\n6. Available Strategies")
    print("-" * 25)
    
    strategies = compressor.list_strategies()
    print(f"Available strategies: {strategies}")
    
    for strategy_name in strategies:
        info = compressor.get_strategy_info(strategy_name)
        if info:
            print(f"\n{strategy_name.title()} Strategy:")
            print(f"  Description: {info['description']}")
            print(f"  Version: {info['version']}")
            print(f"  Optimal ratios: {info['optimal_compression_ratios']}")
            print(f"  Supports batch: {info['supports_batch']}")
    
    # Cache statistics
    print("\n7. Cache Statistics")
    print("-" * 20)
    
    # Run a few compressions to populate cache
    for i in range(3):
        compressor.compress(sample_text.strip(), target_ratio=0.5)
    
    stats = compressor.get_stats()
    print(f"Total compressions: {stats['total_compressions']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Cache misses: {stats['cache_misses']}")
    print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    
    # Batch processing example
    print("\n8. Batch Processing")
    print("-" * 20)
    
    # Create multiple texts for batch processing
    texts = [
        sample_text.strip()[:len(sample_text)//3],
        sample_text.strip()[len(sample_text)//3:2*len(sample_text)//3],
        sample_text.strip()[2*len(sample_text)//3:]
    ]
    
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=0.5,
        parallel=True
    )
    
    print(f"Processed {len(batch_result.results)} texts")
    print(f"Success rate: {batch_result.success_rate:.1%}")
    print(f"Average compression ratio: {batch_result.average_compression_ratio:.1%}")
    print(f"Total tokens saved: {batch_result.total_tokens_saved}")
    print(f"Total processing time: {batch_result.total_processing_time:.3f} seconds")
    
    print("\n✅ All examples completed successfully!")
    print("\nTip: Try modifying the compression ratios and queries to see how")
    print("     they affect the results. You can also experiment with different")
    print("     strategies when they become available.")

if __name__ == "__main__":
    main()