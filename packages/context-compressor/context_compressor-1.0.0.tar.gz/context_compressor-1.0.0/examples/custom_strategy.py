#!/usr/bin/env python3
"""
Custom Strategy Development Examples for AI Context Compressor.

This script demonstrates how to create custom compression strategies
by extending the base CompressionStrategy class and implementing
various compression algorithms.
"""

import re
import random
from typing import List, Optional, Dict, Any
import sys
import os

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor
from context_compressor.strategies.base import CompressionStrategy
from context_compressor.core.models import StrategyMetadata


class RandomSelectionStrategy(CompressionStrategy):
    """
    A simple custom strategy that randomly selects sentences.
    
    This is primarily for demonstration purposes and shows the
    minimal implementation required for a custom strategy.
    """
    
    def __init__(self, seed: Optional[int] = None, **kwargs):
        """Initialize the random selection strategy."""
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        super().__init__(**kwargs)
    
    def _create_metadata(self) -> StrategyMetadata:
        """Create strategy metadata."""
        return StrategyMetadata(
            name="random_selection",
            description="Randomly selects sentences for compression",
            version="1.0.0",
            author="Custom Strategy Developer",
            supported_languages=["en"],
            min_text_length=50,
            max_text_length=10000,
            optimal_compression_ratios=[0.3, 0.5, 0.7],
            requires_query=False,
            supports_batch=True,
            supports_streaming=False,
            computational_complexity="low",
            memory_requirements="low",
            dependencies=[],
            tags=["random", "simple", "demo"]
        )
    
    def _compress_text(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """Compress text by randomly selecting sentences."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        # Calculate number of sentences to keep
        target_count = max(1, int(len(sentences) * target_ratio))
        
        # Randomly select sentences
        selected_sentences = random.sample(sentences, target_count)
        
        # Return in original order (optional)
        ordered_sentences = []
        for sentence in sentences:
            if sentence in selected_sentences:
                ordered_sentences.append(sentence)
                selected_sentences.remove(sentence)
        
        return '. '.join(ordered_sentences) + '.'


class KeywordBasedStrategy(CompressionStrategy):
    """
    A strategy that prioritizes sentences containing important keywords.
    
    This strategy demonstrates more sophisticated text analysis
    and query-aware compression.
    """
    
    def __init__(
        self, 
        important_keywords: Optional[List[str]] = None,
        keyword_weight: float = 0.6,
        length_weight: float = 0.3,
        position_weight: float = 0.1,
        **kwargs
    ):
        """Initialize the keyword-based strategy."""
        self.important_keywords = important_keywords or []
        self.keyword_weight = keyword_weight
        self.length_weight = length_weight
        self.position_weight = position_weight
        super().__init__(**kwargs)
    
    def _create_metadata(self) -> StrategyMetadata:
        """Create strategy metadata."""
        return StrategyMetadata(
            name="keyword_based",
            description="Prioritizes sentences containing important keywords",
            version="1.0.0",
            author="Custom Strategy Developer", 
            supported_languages=["en"],
            min_text_length=100,
            max_text_length=20000,
            optimal_compression_ratios=[0.2, 0.4, 0.6],
            requires_query=False,
            supports_batch=True,
            supports_streaming=False,
            computational_complexity="medium",
            memory_requirements="low",
            dependencies=[],
            tags=["keyword", "scoring", "query-aware"]
        )
    
    def _compress_text(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """Compress text by prioritizing keyword-rich sentences."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        # Prepare keywords (combine default and query keywords)
        keywords = set(self.important_keywords)
        if query:
            # Extract keywords from query
            query_keywords = re.findall(r'\b\w+\b', query.lower())
            keywords.update(query_keywords)
        
        # Score sentences
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, keywords, i, len(sentences))
            sentence_scores.append((sentence, score, i))
        
        # Sort by score (descending)
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences
        target_count = max(1, int(len(sentences) * target_ratio))
        selected_sentences = sentence_scores[:target_count]
        
        # Sort by original position
        selected_sentences.sort(key=lambda x: x[2])
        
        # Extract sentences
        result_sentences = [s[0] for s in selected_sentences]
        
        return '. '.join(result_sentences) + '.'
    
    def _score_sentence(
        self, 
        sentence: str, 
        keywords: set, 
        position: int, 
        total_sentences: int
    ) -> float:
        """Score a sentence based on keywords, length, and position."""
        sentence_lower = sentence.lower()
        
        # Keyword score
        keyword_matches = sum(1 for keyword in keywords if keyword in sentence_lower)
        keyword_score = keyword_matches / max(1, len(keywords))
        
        # Length score (prefer medium-length sentences)
        word_count = len(sentence.split())
        optimal_length = 20  # Optimal sentence length
        length_score = 1.0 - abs(word_count - optimal_length) / optimal_length
        length_score = max(0.1, length_score)
        
        # Position score (prefer beginning and end)
        if position < total_sentences * 0.2:  # First 20%
            position_score = 1.0
        elif position > total_sentences * 0.8:  # Last 20%
            position_score = 0.8
        else:
            position_score = 0.5
        
        # Combine scores
        total_score = (
            self.keyword_weight * keyword_score +
            self.length_weight * length_score +
            self.position_weight * position_score
        )
        
        return total_score


class SummaryStrategy(CompressionStrategy):
    """
    A strategy that creates extractive summaries by identifying
    key sentences and maintaining document structure.
    
    This demonstrates a more sophisticated approach to text compression.
    """
    
    def __init__(
        self,
        preserve_structure: bool = True,
        min_sentence_score: float = 0.3,
        **kwargs
    ):
        """Initialize the summary strategy."""
        self.preserve_structure = preserve_structure
        self.min_sentence_score = min_sentence_score
        super().__init__(**kwargs)
    
    def _create_metadata(self) -> StrategyMetadata:
        """Create strategy metadata."""
        return StrategyMetadata(
            name="summary",
            description="Creates extractive summaries while preserving document structure",
            version="1.0.0",
            author="Custom Strategy Developer",
            supported_languages=["en"],
            min_text_length=200,
            max_text_length=50000,
            optimal_compression_ratios=[0.1, 0.3, 0.5],
            requires_query=False,
            supports_batch=True,
            supports_streaming=False,
            computational_complexity="high",
            memory_requirements="medium",
            dependencies=[],
            tags=["summary", "extractive", "structure-preserving"]
        )
    
    def _compress_text(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        **kwargs
    ) -> str:
        """Compress text using extractive summarization."""
        # Split into paragraphs and sentences
        paragraphs = text.strip().split('\n\n')
        all_sentences = []
        paragraph_map = {}
        
        for para_idx, paragraph in enumerate(paragraphs):
            sentences = re.split(r'[.!?]+', paragraph.strip())
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for sentence in sentences:
                all_sentences.append(sentence)
                paragraph_map[sentence] = para_idx
        
        if not all_sentences:
            return text
        
        # Score all sentences
        sentence_scores = []
        for sentence in all_sentences:
            score = self._calculate_sentence_importance(sentence, all_sentences, query)
            if score >= self.min_sentence_score:
                sentence_scores.append((sentence, score))
        
        # Sort by score
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select sentences based on target ratio
        target_count = max(1, int(len(all_sentences) * target_ratio))
        selected_sentences = sentence_scores[:target_count]
        
        # If preserving structure, organize by paragraphs
        if self.preserve_structure:
            return self._reconstruct_with_structure(
                selected_sentences, paragraph_map, paragraphs
            )
        else:
            # Simple concatenation
            sentences = [s[0] for s in selected_sentences]
            return '. '.join(sentences) + '.'
    
    def _calculate_sentence_importance(
        self, 
        sentence: str, 
        all_sentences: List[str],
        query: Optional[str] = None
    ) -> float:
        """Calculate the importance score of a sentence."""
        words = re.findall(r'\b\w+\b', sentence.lower())
        
        if not words:
            return 0.0
        
        # Calculate word frequencies across all sentences
        all_words = []
        for s in all_sentences:
            all_words.extend(re.findall(r'\b\w+\b', s.lower()))
        
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score based on word frequencies
        sentence_score = sum(word_freq.get(word, 0) for word in words) / len(words)
        
        # Boost score for query relevance
        if query:
            query_words = re.findall(r'\b\w+\b', query.lower())
            query_matches = sum(1 for word in query_words if word in words)
            if query_words:
                query_boost = query_matches / len(query_words)
                sentence_score = 0.7 * sentence_score + 0.3 * query_boost
        
        # Normalize score
        max_possible_score = max(word_freq.values()) if word_freq else 1
        return sentence_score / max_possible_score
    
    def _reconstruct_with_structure(
        self,
        selected_sentences: List[tuple],
        paragraph_map: Dict[str, int],
        original_paragraphs: List[str]
    ) -> str:
        """Reconstruct text maintaining paragraph structure."""
        # Group sentences by paragraph
        para_sentences = {}
        for sentence, score in selected_sentences:
            para_idx = paragraph_map[sentence]
            if para_idx not in para_sentences:
                para_sentences[para_idx] = []
            para_sentences[para_idx].append(sentence)
        
        # Reconstruct paragraphs
        result_paragraphs = []
        for para_idx in sorted(para_sentences.keys()):
            sentences = para_sentences[para_idx]
            paragraph_text = '. '.join(sentences) + '.'
            result_paragraphs.append(paragraph_text)
        
        return '\n\n'.join(result_paragraphs)


def main():
    """Run custom strategy development examples."""
    
    print("🔧 AI Context Compressor - Custom Strategy Development")
    print("=" * 55)
    
    # Sample text for testing strategies
    sample_text = """
    Machine learning is revolutionizing the technology industry. Artificial intelligence 
    algorithms can now process vast amounts of data to identify patterns and make predictions. 
    Deep learning networks use multiple layers to solve complex problems.
    
    Companies are investing heavily in AI research and development. The applications span 
    across various industries including healthcare, finance, and transportation. Natural 
    language processing enables computers to understand human language.
    
    The future of AI looks promising with continued advances in computational power and 
    algorithm development. However, ethical considerations and responsible AI development 
    remain important challenges that need to be addressed.
    """
    
    # Initialize base compressor
    compressor = ContextCompressor()
    
    print("\n1. Creating Custom Strategies")
    print("-" * 32)
    
    # Create instances of custom strategies
    random_strategy = RandomSelectionStrategy(seed=42)
    keyword_strategy = KeywordBasedStrategy(
        important_keywords=["machine learning", "AI", "artificial intelligence", "data"]
    )
    summary_strategy = SummaryStrategy()
    
    print("✅ Created custom strategies:")
    print(f"   • {random_strategy.metadata.name} v{random_strategy.metadata.version}")
    print(f"   • {keyword_strategy.metadata.name} v{keyword_strategy.metadata.version}")
    print(f"   • {summary_strategy.metadata.name} v{summary_strategy.metadata.version}")
    
    # Register custom strategies
    print("\n2. Registering Custom Strategies")
    print("-" * 34)
    
    compressor.register_strategy(random_strategy)
    compressor.register_strategy(keyword_strategy)
    compressor.register_strategy(summary_strategy)
    
    strategies = compressor.list_strategies()
    print(f"✅ Available strategies: {strategies}")
    
    # Test each strategy
    print("\n3. Testing Custom Strategies")
    print("-" * 30)
    
    target_ratio = 0.4
    
    for strategy_name in ["random_selection", "keyword_based", "summary"]:
        print(f"\n🧪 Testing {strategy_name} strategy:")
        
        result = compressor.compress(
            text=sample_text,
            target_ratio=target_ratio,
            strategy=strategy_name
        )
        
        print(f"   Original tokens: {result.original_tokens}")
        print(f"   Compressed tokens: {result.compressed_tokens}")
        print(f"   Actual ratio: {result.actual_ratio:.1%}")
        print(f"   Compressed text: '{result.compressed_text[:100]}...'")
    
    # Query-aware testing
    print("\n4. Query-Aware Custom Strategies")
    print("-" * 34)
    
    query = "artificial intelligence applications"
    
    print(f"Testing with query: '{query}'")
    
    for strategy_name in ["keyword_based", "summary"]:
        result = compressor.compress(
            text=sample_text,
            target_ratio=0.5,
            strategy=strategy_name,
            query=query
        )
        
        print(f"\n{strategy_name}:")
        print(f"   Result: '{result.compressed_text[:120]}...'")
        print(f"   Ratio: {result.actual_ratio:.1%}")
    
    # Strategy metadata inspection
    print("\n5. Strategy Metadata Inspection")  
    print("-" * 33)
    
    for strategy_name in ["keyword_based", "summary"]:
        info = compressor.get_strategy_info(strategy_name)
        print(f"\n📋 {strategy_name} metadata:")
        print(f"   Description: {info['description']}")
        print(f"   Complexity: {info['computational_complexity']}")
        print(f"   Memory: {info['memory_requirements']}")
        print(f"   Optimal ratios: {info['optimal_compression_ratios']}")
        print(f"   Tags: {', '.join(info['tags'])}")
    
    # Strategy comparison
    print("\n6. Strategy Performance Comparison")
    print("-" * 35)
    
    strategies_to_compare = ["extractive", "keyword_based", "summary"]
    comparison_results = {}
    
    for strategy in strategies_to_compare:
        import time
        start_time = time.time()
        
        result = compressor.compress(
            text=sample_text,
            target_ratio=0.4,
            strategy=strategy
        )
        
        processing_time = time.time() - start_time
        
        comparison_results[strategy] = {
            'ratio': result.actual_ratio,
            'tokens': result.compressed_tokens,
            'time': processing_time
        }
    
    print("Strategy Performance:")
    print("Strategy        | Ratio  | Tokens | Time(ms)")
    print("-" * 45)
    
    for strategy, results in comparison_results.items():
        print(f"{strategy:15} | {results['ratio']:5.1%} | "
              f"{results['tokens']:6d} | {results['time']*1000:7.1f}")
    
    # Advanced custom strategy features
    print("\n7. Advanced Custom Strategy Features")
    print("-" * 37)
    
    # Custom strategy with configuration
    advanced_keyword_strategy = KeywordBasedStrategy(
        important_keywords=["technology", "innovation", "development"],
        keyword_weight=0.8,  # Higher emphasis on keywords
        length_weight=0.15,
        position_weight=0.05
    )
    
    compressor.register_strategy(advanced_keyword_strategy)
    
    result = compressor.compress(
        text=sample_text,
        target_ratio=0.3,
        strategy="keyword_based"  # Will use the last registered one
    )
    
    print("Advanced keyword strategy results:")
    print(f"   Compressed: '{result.compressed_text}'")
    print(f"   Ratio: {result.actual_ratio:.1%}")
    
    # Batch processing with custom strategies
    print("\n8. Batch Processing with Custom Strategies")
    print("-" * 41)
    
    texts = [sample_text[:200], sample_text[200:400], sample_text[400:]]
    
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=0.5,
        strategy="summary"
    )
    
    print(f"Batch processing with summary strategy:")
    print(f"   Processed: {len(batch_result.results)} texts")
    print(f"   Average ratio: {batch_result.average_compression_ratio:.1%}")
    print(f"   Total time: {batch_result.total_processing_time:.3f}s")
    
    # Strategy validation and error handling
    print("\n9. Strategy Validation and Error Handling")
    print("-" * 42)
    
    validation_results = compressor.strategy_manager.validate_all_strategies()
    
    print("Strategy validation results:")
    for strategy_name, errors in validation_results.items():
        if errors:
            print(f"   ❌ {strategy_name}: {', '.join(errors)}")
        else:
            print(f"   ✅ {strategy_name}: All validations passed")
    
    # Best practices for custom strategies
    print("\n10. Best Practices for Custom Strategies")
    print("-" * 40)
    
    print("📚 Custom Strategy Development Guidelines:")
    print("   1. Always inherit from CompressionStrategy base class")
    print("   2. Implement _create_metadata() with complete information")
    print("   3. Implement _compress_text() with proper error handling") 
    print("   4. Override _count_tokens() for custom tokenization if needed")
    print("   5. Add proper input validation in your methods")
    print("   6. Include comprehensive docstrings and type hints")
    print("   7. Test with various text types and compression ratios")
    print("   8. Consider memory and computational complexity")
    print("   9. Support query-aware compression when relevant")
    print("   10. Register strategies with descriptive metadata")
    
    print("\n💡 Strategy Development Tips:")
    print("   • Start with simple approaches and iterate")
    print("   • Use existing strategies as reference implementations")
    print("   • Test edge cases (empty text, very short/long text)")
    print("   • Consider domain-specific requirements")
    print("   • Profile performance for large texts")
    print("   • Document configuration parameters clearly")
    
    print("\n✅ All custom strategy examples completed!")
    
    print("\n🚀 Next Steps:")
    print("   • Implement your own domain-specific strategy")
    print("   • Experiment with different scoring algorithms")
    print("   • Combine multiple strategies for hybrid approaches")
    print("   • Share your strategies with the community!")


if __name__ == "__main__":
    main()