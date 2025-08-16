"""
Strategy manager for handling compression strategies.
"""

from typing import Dict, List, Optional, Any, Callable
import logging
import re

from .models import StrategyMetadata
from ..strategies.base import CompressionStrategy

logger = logging.getLogger(__name__)


class StrategyManager:
    """
    Manager class for compression strategies.
    
    Handles strategy registration, selection, and lifecycle management.
    Supports automatic strategy selection based on text characteristics
    and user requirements.
    """
    
    def __init__(self):
        """Initialize the strategy manager."""
        self.strategies: Dict[str, CompressionStrategy] = {}
        self.selection_rules: List[Callable] = []
        self._setup_default_selection_rules()
    
    def register_strategy(self, strategy: CompressionStrategy) -> None:
        """
        Register a compression strategy.
        
        Args:
            strategy: The compression strategy to register
            
        Raises:
            ValueError: If strategy name already exists
        """
        strategy_name = strategy.metadata.name
        
        if strategy_name in self.strategies:
            logger.warning(f"Overwriting existing strategy: {strategy_name}")
        
        self.strategies[strategy_name] = strategy
        logger.info(f"Registered strategy: {strategy_name} v{strategy.metadata.version}")
    
    def unregister_strategy(self, strategy_name: str) -> None:
        """
        Unregister a compression strategy.
        
        Args:
            strategy_name: Name of the strategy to unregister
            
        Raises:
            KeyError: If strategy doesn't exist
        """
        if strategy_name not in self.strategies:
            raise KeyError(f"Strategy not found: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        if strategy.is_initialized:
            strategy.cleanup()
        
        del self.strategies[strategy_name]
        logger.info(f"Unregistered strategy: {strategy_name}")
    
    def get_strategy(self, strategy_name: str) -> Optional[CompressionStrategy]:
        """
        Get a strategy by name.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            CompressionStrategy: The strategy or None if not found
        """
        return self.strategies.get(strategy_name)
    
    def list_strategies(self) -> List[str]:
        """
        List all registered strategy names.
        
        Returns:
            List[str]: List of strategy names
        """
        return list(self.strategies.keys())
    
    def get_strategy_metadata(self, strategy_name: str) -> Optional[StrategyMetadata]:
        """
        Get metadata for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            StrategyMetadata: Strategy metadata or None if not found
        """
        strategy = self.get_strategy(strategy_name)
        return strategy.metadata if strategy else None
    
    def select_strategy(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[CompressionStrategy]:
        """
        Automatically select the best strategy for given text and requirements.
        
        Args:
            text: The input text to compress
            target_ratio: Target compression ratio
            query: Optional query for context-aware compression
            user_preferences: Optional user preferences for strategy selection
            
        Returns:
            CompressionStrategy: Selected strategy or None if no suitable strategy found
        """
        if not self.strategies:
            logger.warning("No strategies registered")
            return None
        
        # Analyze text characteristics
        text_analysis = self._analyze_text(text)
        
        # Score each strategy
        strategy_scores = {}
        for name, strategy in self.strategies.items():
            score = self._score_strategy(
                strategy, text_analysis, target_ratio, query, user_preferences
            )
            if score > 0:  # Only consider viable strategies
                strategy_scores[name] = score
        
        if not strategy_scores:
            logger.warning("No suitable strategy found")
            return None
        
        # Select strategy with highest score
        best_strategy_name = max(strategy_scores, key=strategy_scores.get)
        best_strategy = self.strategies[best_strategy_name]
        
        logger.info(
            f"Selected strategy: {best_strategy_name} "
            f"(score: {strategy_scores[best_strategy_name]:.2f})"
        )
        
        return best_strategy
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text characteristics for strategy selection.
        
        Args:
            text: Input text
            
        Returns:
            Dict[str, Any]: Text analysis results
        """
        # Basic text statistics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Character analysis
        char_counts = {
            'letters': sum(1 for c in text if c.isalpha()),
            'digits': sum(1 for c in text if c.isdigit()),
            'spaces': sum(1 for c in text if c.isspace()),
            'punctuation': sum(1 for c in text if not c.isalnum() and not c.isspace())
        }
        
        # Content type detection
        content_type = self._detect_content_type(text)
        
        analysis = {
            'length': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'char_distribution': char_counts,
            'content_type': content_type,
            'complexity': self._estimate_complexity(text, words, sentences),
            'language': 'en'  # Default to English, could be enhanced with language detection
        }
        
        return analysis
    
    def _detect_content_type(self, text: str) -> str:
        """
        Detect the type of content (technical, narrative, etc.).
        
        Args:
            text: Input text
            
        Returns:
            str: Detected content type
        """
        text_lower = text.lower()
        
        # Technical indicators
        technical_terms = [
            'algorithm', 'function', 'method', 'class', 'variable', 'parameter',
            'system', 'process', 'implementation', 'configuration', 'protocol'
        ]
        technical_score = sum(text_lower.count(term) for term in technical_terms)
        
        # Academic indicators
        academic_terms = [
            'research', 'study', 'analysis', 'hypothesis', 'methodology',
            'conclusion', 'abstract', 'introduction', 'discussion', 'results'
        ]
        academic_score = sum(text_lower.count(term) for term in academic_terms)
        
        # Narrative indicators
        narrative_terms = [
            'story', 'character', 'plot', 'scene', 'chapter', 'narrative',
            'once upon', 'meanwhile', 'suddenly', 'finally'
        ]
        narrative_score = sum(text_lower.count(term) for term in narrative_terms)
        
        # News indicators
        news_terms = [
            'according to', 'reported', 'sources', 'statement', 'official',
            'government', 'company', 'announced', 'yesterday', 'today'
        ]
        news_score = sum(text_lower.count(term) for term in news_terms)
        
        scores = {
            'technical': technical_score,
            'academic': academic_score,
            'narrative': narrative_score,
            'news': news_score
        }
        
        max_score_type = max(scores, key=scores.get)
        
        # If no clear type detected, classify as general
        if scores[max_score_type] == 0:
            return 'general'
        
        return max_score_type
    
    def _estimate_complexity(
        self, 
        text: str, 
        words: List[str], 
        sentences: List[str]
    ) -> str:
        """
        Estimate text complexity (low, medium, high).
        
        Args:
            text: Input text
            words: List of words
            sentences: List of sentences
            
        Returns:
            str: Complexity level
        """
        if not words or not sentences:
            return 'low'
        
        # Calculate complexity factors
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # Count complex words (3+ syllables, estimated)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = complex_words / len(words)
        
        # Complexity scoring
        complexity_score = 0
        
        if avg_word_length > 5:
            complexity_score += 1
        if avg_sentence_length > 20:
            complexity_score += 1
        if complex_word_ratio > 0.15:
            complexity_score += 1
        
        if complexity_score <= 1:
            return 'low'
        elif complexity_score == 2:
            return 'medium'
        else:
            return 'high'
    
    def _score_strategy(
        self,
        strategy: CompressionStrategy,
        text_analysis: Dict[str, Any],
        target_ratio: float,
        query: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Score a strategy based on suitability for the given text and requirements.
        
        Args:
            strategy: The strategy to score
            text_analysis: Text analysis results
            target_ratio: Target compression ratio
            query: Optional query
            user_preferences: Optional user preferences
            
        Returns:
            float: Strategy score (0.0 to 1.0)
        """
        metadata = strategy.metadata
        score = 0.0
        
        # Check basic compatibility
        if text_analysis['length'] < metadata.min_text_length:
            return 0.0  # Strategy not suitable
        
        if (metadata.max_text_length is not None and 
            text_analysis['length'] > metadata.max_text_length):
            score -= 0.2  # Penalty for exceeding recommended size
        
        # Language compatibility
        if text_analysis['language'] not in metadata.supported_languages:
            return 0.0  # Language not supported
        
        # Compression ratio compatibility
        ratio_distances = [abs(target_ratio - ratio) for ratio in metadata.optimal_compression_ratios]
        min_distance = min(ratio_distances)
        ratio_score = max(0, 1.0 - min_distance * 2)  # Penalty for non-optimal ratios
        score += ratio_score * 0.3
        
        # Query requirement compatibility
        if metadata.requires_query and query is None:
            score -= 0.3
        elif not metadata.requires_query and query is not None:
            score += 0.1  # Bonus for strategies that can use query but don't require it
        
        # Performance characteristics
        complexity_preferences = {
            'low': {'low': 0.3, 'medium': 0.2, 'high': 0.1},
            'medium': {'low': 0.2, 'medium': 0.3, 'high': 0.2},
            'high': {'low': 0.1, 'medium': 0.2, 'high': 0.3}
        }
        
        text_complexity = text_analysis['complexity']
        strategy_complexity = metadata.computational_complexity
        score += complexity_preferences[text_complexity].get(strategy_complexity, 0.1)
        
        # Content type specific bonuses
        content_type = text_analysis['content_type']
        if content_type == 'technical' and 'technical' in metadata.tags:
            score += 0.2
        elif content_type == 'narrative' and 'narrative' in metadata.tags:
            score += 0.2
        elif content_type == 'academic' and 'academic' in metadata.tags:
            score += 0.2
        
        # User preferences
        if user_preferences:
            preferred_strategy = user_preferences.get('strategy')
            if preferred_strategy and preferred_strategy == metadata.name:
                score += 0.3
            
            performance_priority = user_preferences.get('performance', 'balanced')
            if performance_priority == 'speed' and metadata.computational_complexity == 'low':
                score += 0.2
            elif performance_priority == 'quality' and metadata.computational_complexity == 'high':
                score += 0.2
        
        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _setup_default_selection_rules(self) -> None:
        """Setup default strategy selection rules."""
        # This could be extended with more sophisticated rule-based selection
        pass
    
    def get_recommendations(
        self, 
        text: str, 
        target_ratio: float,
        query: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get strategy recommendations with scores.
        
        Args:
            text: Input text
            target_ratio: Target compression ratio
            query: Optional query
            top_k: Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of strategy recommendations with scores
        """
        text_analysis = self._analyze_text(text)
        recommendations = []
        
        for name, strategy in self.strategies.items():
            score = self._score_strategy(strategy, text_analysis, target_ratio, query)
            if score > 0:
                recommendations.append({
                    'strategy_name': name,
                    'score': score,
                    'metadata': strategy.metadata.to_dict(),
                    'suitability_reasons': self._get_suitability_reasons(
                        strategy, text_analysis, target_ratio, query
                    )
                })
        
        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_k]
    
    def _get_suitability_reasons(
        self,
        strategy: CompressionStrategy,
        text_analysis: Dict[str, Any],
        target_ratio: float,
        query: Optional[str] = None
    ) -> List[str]:
        """
        Get reasons why a strategy is suitable.
        
        Args:
            strategy: The strategy
            text_analysis: Text analysis results
            target_ratio: Target compression ratio
            query: Optional query
            
        Returns:
            List[str]: List of suitability reasons
        """
        reasons = []
        metadata = strategy.metadata
        
        # Length compatibility
        if (text_analysis['length'] >= metadata.min_text_length and 
            (metadata.max_text_length is None or 
             text_analysis['length'] <= metadata.max_text_length)):
            reasons.append("Text length is compatible")
        
        # Compression ratio
        if target_ratio in metadata.optimal_compression_ratios:
            reasons.append("Target ratio is optimal for this strategy")
        
        # Query handling
        if query and not metadata.requires_query:
            reasons.append("Can utilize query for better relevance")
        
        # Performance characteristics
        if metadata.computational_complexity == 'low':
            reasons.append("Fast processing")
        elif metadata.computational_complexity == 'high':
            reasons.append("High-quality results")
        
        # Content type matching
        content_type = text_analysis['content_type']
        if content_type in metadata.tags:
            reasons.append(f"Optimized for {content_type} content")
        
        return reasons
    
    def validate_all_strategies(self) -> Dict[str, List[str]]:
        """
        Validate all registered strategies.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping strategy names to validation errors
        """
        validation_results = {}
        
        for name, strategy in self.strategies.items():
            errors = []
            
            # Check metadata completeness
            metadata = strategy.metadata
            if not metadata.name:
                errors.append("Missing strategy name")
            if not metadata.description:
                errors.append("Missing description")
            if not metadata.version:
                errors.append("Missing version")
            
            # Check configuration
            if metadata.min_text_length <= 0:
                errors.append("Invalid minimum text length")
            if (metadata.max_text_length is not None and 
                metadata.max_text_length <= metadata.min_text_length):
                errors.append("Maximum text length must be greater than minimum")
            
            # Check compression ratios
            if not metadata.optimal_compression_ratios:
                errors.append("No optimal compression ratios specified")
            else:
                for ratio in metadata.optimal_compression_ratios:
                    if not (0.0 < ratio < 1.0):
                        errors.append(f"Invalid compression ratio: {ratio}")
            
            validation_results[name] = errors
        
        return validation_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered strategies.
        
        Returns:
            Dict[str, Any]: Strategy statistics
        """
        if not self.strategies:
            return {'total_strategies': 0}
        
        # Count strategies by type
        complexity_counts = {}
        language_counts = {}
        tag_counts = {}
        
        for strategy in self.strategies.values():
            metadata = strategy.metadata
            
            # Complexity distribution
            complexity = metadata.computational_complexity
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            
            # Language support
            for lang in metadata.supported_languages:
                language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Tag distribution
            for tag in metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_strategies': len(self.strategies),
            'complexity_distribution': complexity_counts,
            'language_support': language_counts,
            'tag_distribution': tag_counts,
            'strategies': list(self.strategies.keys())
        }
    
    def cleanup_all_strategies(self) -> None:
        """Cleanup all initialized strategies."""
        for strategy in self.strategies.values():
            if strategy.is_initialized:
                strategy.cleanup()
        
        logger.info("All strategies cleaned up")
    
    def __str__(self) -> str:
        """String representation."""
        return f"StrategyManager(strategies={len(self.strategies)})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"StrategyManager(strategies={list(self.strategies.keys())})"