#!/usr/bin/env python3
"""
Quality Evaluation Examples for AI Context Compressor.

This script demonstrates the comprehensive quality evaluation system
including ROUGE scores, semantic similarity, entity preservation,
and custom quality metrics.
"""

import sys
import os

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor
from context_compressor.core.quality_evaluator import QualityEvaluator


def main():
    """Run quality evaluation examples."""
    
    print("📊 AI Context Compressor - Quality Evaluation Examples")
    print("=" * 55)
    
    # Sample texts with different characteristics
    sample_texts = {
        "technical": """
        Machine learning algorithms are computational models that enable computers 
        to learn and make decisions from data without being explicitly programmed. 
        These algorithms use statistical techniques to identify patterns in large 
        datasets. Popular algorithms include decision trees, random forests, support 
        vector machines, and neural networks. Deep learning, a subset of machine 
        learning, uses multi-layered neural networks to process complex data such 
        as images, speech, and natural language. The training process involves 
        feeding the algorithm labeled examples so it can learn to make accurate 
        predictions on new, unseen data.
        """,
        
        "narrative": """
        Sarah walked through the bustling marketplace on a sunny Tuesday morning. 
        The vendors were calling out their prices for fresh fruits and vegetables. 
        She stopped at Mrs. Johnson's stall to buy some apples and oranges for 
        her family's lunch. The elderly woman smiled warmly and gave her an extra 
        apple for free. As Sarah continued her shopping, she met her neighbor Tom 
        who was buying flowers for his wife's birthday. They chatted briefly about 
        the weather and their children's school activities before parting ways. 
        Sarah finished her shopping and headed home with her grocery bags.
        """,
        
        "factual": """
        The COVID-19 pandemic was declared by the World Health Organization (WHO) 
        on March 11, 2020. The virus, officially named SARS-CoV-2, originated in 
        Wuhan, China in late 2019. By April 2020, over 200 countries and territories 
        had reported cases. The pandemic led to widespread lockdowns, travel 
        restrictions, and economic disruption. Vaccines were developed in record 
        time, with the first approvals coming in December 2020. As of 2023, over 
        13 billion vaccine doses have been administered worldwide. The pandemic 
        significantly impacted global health systems, education, and social interactions.
        """
    }
    
    # Initialize compressor with quality evaluation enabled
    print("\n1. Initializing Context Compressor with Quality Evaluation")
    print("-" * 58)
    
    compressor = ContextCompressor(enable_quality_evaluation=True)
    quality_evaluator = QualityEvaluator()
    
    print("✅ Quality evaluator initialized with default weights:")
    print(f"   - Semantic similarity: {quality_evaluator.semantic_weight:.1%}")
    print(f"   - ROUGE scores: {quality_evaluator.rouge_weight:.1%}")  
    print(f"   - Entity preservation: {quality_evaluator.entity_weight:.1%}")
    print(f"   - Readability: {quality_evaluator.readability_weight:.1%}")
    
    # Basic quality evaluation
    print("\n2. Basic Quality Evaluation")
    print("-" * 30)
    
    text = sample_texts["technical"]
    result = compressor.compress(text, target_ratio=0.5)
    
    if result.quality_metrics:
        metrics = result.quality_metrics
        print(f"📈 Compression Results:")
        print(f"   Original tokens: {result.original_tokens}")
        print(f"   Compressed tokens: {result.compressed_tokens}")
        print(f"   Actual ratio: {result.actual_ratio:.1%}")
        
        print(f"\n📊 Quality Metrics:")
        print(f"   Overall Score:           {metrics.overall_score:.3f} ⭐")
        print(f"   Semantic Similarity:     {metrics.semantic_similarity:.3f}")
        print(f"   ROUGE-1:                 {metrics.rouge_1:.3f}")
        print(f"   ROUGE-2:                 {metrics.rouge_2:.3f}")
        print(f"   ROUGE-L:                 {metrics.rouge_l:.3f}")
        print(f"   Entity Preservation:     {metrics.entity_preservation_rate:.3f}")
        print(f"   Readability Score:       {metrics.readability_score:.1f}")
        print(f"   Compression Ratio:       {metrics.compression_ratio:.3f}")
    
    # Compare different compression ratios
    print("\n3. Quality vs Compression Ratio Analysis")
    print("-" * 42)
    
    text = sample_texts["factual"]
    ratios = [0.2, 0.3, 0.5, 0.7, 0.8]
    
    print("Ratio | Quality | ROUGE-L | Semantic | Entity | Readability")
    print("-" * 62)
    
    for ratio in ratios:
        result = compressor.compress(text, target_ratio=ratio)
        if result.quality_metrics:
            m = result.quality_metrics
            print(f"{result.actual_ratio:5.1%} | {m.overall_score:7.3f} | "
                  f"{m.rouge_l:7.3f} | {m.semantic_similarity:8.3f} | "
                  f"{m.entity_preservation_rate:6.3f} | {m.readability_score:11.1f}")
    
    # Text type comparison
    print("\n4. Quality Evaluation by Text Type")
    print("-" * 36)
    
    for text_type, text in sample_texts.items():
        result = compressor.compress(text, target_ratio=0.5)
        
        print(f"\n📝 {text_type.title()} Text:")
        print(f"   Length: {len(text.split())} words")
        
        if result.quality_metrics:
            m = result.quality_metrics
            print(f"   Quality Score: {m.overall_score:.3f}")
            print(f"   Best Metrics:")
            
            # Find the best metrics
            metrics_dict = {
                'ROUGE-1': m.rouge_1,
                'ROUGE-2': m.rouge_2,
                'ROUGE-L': m.rouge_l,
                'Semantic': m.semantic_similarity,
                'Entity': m.entity_preservation_rate,
                'Readability': m.readability_score / 100  # Normalize to 0-1
            }
            
            sorted_metrics = sorted(metrics_dict.items(), key=lambda x: x[1], reverse=True)
            for metric, score in sorted_metrics[:3]:
                print(f"     • {metric}: {score:.3f}")
    
    # Query-aware quality evaluation
    print("\n5. Query-Aware Quality Evaluation")
    print("-" * 35)
    
    text = sample_texts["technical"]
    queries = [
        "machine learning algorithms",
        "neural networks and deep learning", 
        "data processing techniques",
        "unrelated query about cooking"
    ]
    
    for query in queries:
        result = compressor.compress(text, target_ratio=0.4, query=query)
        
        print(f"\nQuery: '{query}'")
        print(f"Compressed: '{result.compressed_text[:80]}...'")
        
        if result.quality_metrics:
            print(f"Quality: {result.quality_metrics.overall_score:.3f} "
                  f"(ROUGE-L: {result.quality_metrics.rouge_l:.3f})")
    
    # Detailed quality analysis
    print("\n6. Detailed Quality Analysis")
    print("-" * 30)
    
    text = sample_texts["narrative"]
    result = compressor.compress(text, target_ratio=0.4)
    
    # Get detailed analysis
    detailed_analysis = quality_evaluator.get_detailed_analysis(
        original=text,
        compressed=result.compressed_text
    )
    
    print("📊 Detailed Quality Analysis:")
    print(f"   Overall Interpretation: {detailed_analysis['quality_interpretation']}")
    
    print(f"\n📈 Component Scores:")
    components = detailed_analysis['component_scores']
    for component, score in components.items():
        print(f"   {component.replace('_', ' ').title()}: {score:.3f}")
    
    print(f"\n🏷️  Entity Analysis:")
    entity_analysis = detailed_analysis['entity_analysis']
    print(f"   Original entities: {len(entity_analysis['original_entities'])}")
    print(f"   Preserved entities: {len(entity_analysis['preserved_entities'])}")
    print(f"   Lost entities: {len(entity_analysis['lost_entities'])}")
    
    if entity_analysis['preserved_entities']:
        print(f"   Preserved: {', '.join(entity_analysis['preserved_entities'][:5])}")
    if entity_analysis['lost_entities']:
        print(f"   Lost: {', '.join(entity_analysis['lost_entities'][:5])}")
    
    print(f"\n📊 Text Statistics:")
    stats = detailed_analysis['text_statistics']
    orig_stats = stats['original']
    comp_stats = stats['compressed']
    reduction = stats['reduction']
    
    print(f"   Original:   {orig_stats['words']} words, {orig_stats['sentences']} sentences")
    print(f"   Compressed: {comp_stats['words']} words, {comp_stats['sentences']} sentences")
    print(f"   Reduction:  {reduction['words']} words, {reduction['sentences']} sentences")
    
    # Custom quality evaluator
    print("\n7. Custom Quality Evaluator")
    print("-" * 29)
    
    # Create evaluator with custom weights
    custom_evaluator = QualityEvaluator(
        semantic_weight=0.4,      # Prioritize semantic similarity
        rouge_weight=0.25,        # Moderate ROUGE importance
        entity_weight=0.25,       # Moderate entity preservation
        readability_weight=0.1    # Lower readability importance
    )
    
    text = sample_texts["technical"]
    result = compressor.compress(text, target_ratio=0.5)
    
    # Evaluate with both default and custom evaluators
    default_quality = quality_evaluator.evaluate(text, result.compressed_text)
    custom_quality = custom_evaluator.evaluate(text, result.compressed_text)
    
    print("Quality Evaluator Comparison:")
    print(f"   Default weights: {default_quality.overall_score:.3f}")
    print(f"   Custom weights:  {custom_quality.overall_score:.3f}")
    print(f"   Difference:      {abs(custom_quality.overall_score - default_quality.overall_score):.3f}")
    
    # Quality trends across multiple compressions
    print("\n8. Quality Trends Analysis")
    print("-" * 28)
    
    text = sample_texts["factual"]
    quality_scores = []
    compression_ratios = []
    
    test_ratios = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print("Analyzing quality trends across compression ratios...")
    
    for ratio in test_ratios:
        result = compressor.compress(text, target_ratio=ratio)
        if result.quality_metrics:
            quality_scores.append(result.quality_metrics.overall_score)
            compression_ratios.append(result.actual_ratio)
    
    print("\nQuality Trend Analysis:")
    print("Ratio | Quality | Trend")
    print("-" * 25)
    
    for i, (ratio, quality) in enumerate(zip(compression_ratios, quality_scores)):
        if i > 0:
            trend = "📈" if quality > quality_scores[i-1] else "📉" if quality < quality_scores[i-1] else "➡️"
        else:
            trend = "➡️"
        print(f"{ratio:5.1%} | {quality:7.3f} | {trend}")
    
    # Find optimal compression point
    if quality_scores:
        # Find ratio with best quality-compression balance
        efficiency_scores = [q * (1 - r) for q, r in zip(quality_scores, compression_ratios)]
        best_idx = efficiency_scores.index(max(efficiency_scores))
        
        print(f"\n🎯 Optimal Compression Point:")
        print(f"   Ratio: {compression_ratios[best_idx]:.1%}")
        print(f"   Quality: {quality_scores[best_idx]:.3f}")
        print(f"   Efficiency Score: {efficiency_scores[best_idx]:.3f}")
    
    # Batch quality evaluation
    print("\n9. Batch Quality Evaluation")
    print("-" * 29)
    
    texts = list(sample_texts.values())
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=0.5,
        evaluate_quality=True
    )
    
    print("Batch Quality Results:")
    print(f"   Texts processed: {len(batch_result.results)}")
    
    if batch_result.average_quality_score:
        print(f"   Average quality: {batch_result.average_quality_score:.3f}")
    
    print("\nIndividual Results:")
    for i, result in enumerate(batch_result.results):
        text_type = list(sample_texts.keys())[i]
        if result.quality_metrics:
            print(f"   {text_type.title()}: {result.quality_metrics.overall_score:.3f} "
                  f"({result.actual_ratio:.1%} compression)")
    
    # Quality interpretation guide
    print("\n10. Quality Score Interpretation Guide")
    print("-" * 38)
    
    print("Quality Score Ranges:")
    print("   0.90 - 1.00: Excellent ⭐⭐⭐⭐⭐")
    print("   0.80 - 0.89: Very Good ⭐⭐⭐⭐")
    print("   0.70 - 0.79: Good ⭐⭐⭐")
    print("   0.60 - 0.69: Fair ⭐⭐")
    print("   0.50 - 0.59: Poor ⭐")
    print("   0.00 - 0.49: Very Poor")
    
    print("\nMetric Interpretations:")
    print("   • ROUGE scores: Measure overlap with original text")
    print("   • Semantic similarity: Measures meaning preservation")
    print("   • Entity preservation: Tracks important entities (names, dates, numbers)")
    print("   • Readability: Flesch Reading Ease (higher = more readable)")
    print("   • Overall score: Weighted combination of all metrics")
    
    print("\n✅ All quality evaluation examples completed!")
    
    print("\n💡 Key Insights:")
    print("   • Quality decreases with higher compression ratios")
    print("   • Different text types have different quality patterns")
    print("   • Query-aware compression can improve relevance")
    print("   • Custom evaluator weights allow domain-specific tuning")
    print("   • Entity preservation is crucial for factual content")
    print("   • Semantic similarity is important for technical content")


if __name__ == "__main__":
    main()