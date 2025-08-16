"""
OpenAI integration for Context Compressor.

This module provides utilities for compressing text before sending
to OpenAI API to reduce token usage and costs.
"""

from typing import Optional, Dict, Any, List, Union
import logging

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.compressor import ContextCompressor
from ..utils.tokenizers import TokenizerBase

logger = logging.getLogger(__name__)


class OpenAITokenizer(TokenizerBase):
    """
    OpenAI tokenizer using tiktoken for accurate token counting.
    
    This tokenizer provides accurate token counts for OpenAI models,
    which is important for cost estimation and API limits.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI tokenizer.
        
        Args:
            model: OpenAI model name for tokenizer selection
        """
        if not TIKTOKEN_AVAILABLE:
            raise ImportError(
                "tiktoken is not installed. Install with: pip install tiktoken"
            )
        
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Unknown model {model}, using cl100k_base encoding")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text using OpenAI tokenizer.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of token strings
        """
        token_ids = self.encoding.encode(text)
        return [self.encoding.decode([token_id]) for token_id in token_ids]
    
    def count(self, text: str) -> int:
        """
        Count tokens using OpenAI tokenizer.
        
        Args:
            text: Input text
            
        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))


def compress_for_openai(
    text: str,
    target_ratio: float = 0.5,
    model: str = "gpt-3.5-turbo",
    strategy: str = "extractive",
    query: Optional[str] = None,
    compressor: Optional[ContextCompressor] = None,
    estimate_cost_savings: bool = True
) -> Dict[str, Any]:
    """
    Compress text optimized for OpenAI API usage.
    
    This function compresses text and provides detailed information
    about token savings and estimated cost reductions.
    
    Args:
        text: Text to compress
        target_ratio: Target compression ratio
        model: OpenAI model name for token counting
        strategy: Compression strategy to use
        query: Optional query for context-aware compression
        compressor: Optional ContextCompressor instance
        estimate_cost_savings: Whether to estimate cost savings
        
    Returns:
        Dict[str, Any]: Compression results with OpenAI-specific metrics
    """
    if compressor is None:
        compressor = ContextCompressor()
    
    # Use OpenAI tokenizer for accurate counting
    if TIKTOKEN_AVAILABLE:
        openai_tokenizer = OpenAITokenizer(model)
        
        # Override token counting method
        original_count_tokens = compressor.strategy_manager.get_strategy("extractive")._count_tokens
        compressor.strategy_manager.get_strategy("extractive")._count_tokens = openai_tokenizer.count
    
    # Perform compression
    result = compressor.compress(
        text=text,
        target_ratio=target_ratio,
        strategy=strategy,
        query=query
    )
    
    # Calculate OpenAI-specific metrics
    if TIKTOKEN_AVAILABLE:
        original_tokens_openai = openai_tokenizer.count(text)
        compressed_tokens_openai = openai_tokenizer.count(result.compressed_text)
        tokens_saved_openai = original_tokens_openai - compressed_tokens_openai
    else:
        # Fallback to approximate counting
        original_tokens_openai = result.original_tokens
        compressed_tokens_openai = result.compressed_tokens
        tokens_saved_openai = result.tokens_saved
    
    response = {
        'compressed_text': result.compressed_text,
        'original_tokens': original_tokens_openai,
        'compressed_tokens': compressed_tokens_openai,
        'tokens_saved': tokens_saved_openai,
        'actual_compression_ratio': compressed_tokens_openai / original_tokens_openai if original_tokens_openai > 0 else 0,
        'strategy_used': result.strategy_used,
        'processing_time': result.processing_time,
        'model': model
    }
    
    # Add cost estimation if requested
    if estimate_cost_savings:
        cost_info = estimate_openai_cost_savings(
            original_tokens=original_tokens_openai,
            compressed_tokens=compressed_tokens_openai,
            model=model
        )
        response.update(cost_info)
    
    # Add quality metrics if available
    if result.quality_metrics:
        response['quality_metrics'] = result.quality_metrics.to_dict()
    
    return response


def estimate_openai_cost_savings(
    original_tokens: int,
    compressed_tokens: int,
    model: str = "gpt-3.5-turbo"
) -> Dict[str, Any]:
    """
    Estimate cost savings from token reduction for OpenAI API.
    
    Args:
        original_tokens: Original token count
        compressed_tokens: Compressed token count
        model: OpenAI model name
        
    Returns:
        Dict[str, Any]: Cost estimation details
    """
    # OpenAI pricing (as of 2024 - these may change)
    pricing = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # per 1k tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006}
    }
    
    # Default to GPT-3.5-turbo pricing if model not found
    model_pricing = pricing.get(model, pricing["gpt-3.5-turbo"])
    
    # Calculate costs (assuming input tokens)
    original_cost = (original_tokens / 1000) * model_pricing["input"]
    compressed_cost = (compressed_tokens / 1000) * model_pricing["input"]
    cost_savings = original_cost - compressed_cost
    savings_percentage = (cost_savings / original_cost * 100) if original_cost > 0 else 0
    
    return {
        'cost_estimation': {
            'model': model,
            'original_cost_usd': round(original_cost, 6),
            'compressed_cost_usd': round(compressed_cost, 6),
            'cost_savings_usd': round(cost_savings, 6),
            'savings_percentage': round(savings_percentage, 2),
            'tokens_saved': original_tokens - compressed_tokens,
            'pricing_per_1k_tokens': model_pricing["input"]
        }
    }


def compress_for_chat_completion(
    messages: List[Dict[str, str]],
    target_ratio: float = 0.5,
    model: str = "gpt-3.5-turbo",
    strategy: str = "extractive",
    compress_system: bool = False,
    compress_user: bool = True,
    compress_assistant: bool = False,
    compressor: Optional[ContextCompressor] = None
) -> List[Dict[str, str]]:
    """
    Compress messages for OpenAI chat completion API.
    
    Args:
        messages: List of chat messages
        target_ratio: Target compression ratio
        model: OpenAI model name
        strategy: Compression strategy to use
        compress_system: Whether to compress system messages
        compress_user: Whether to compress user messages
        compress_assistant: Whether to compress assistant messages
        compressor: Optional ContextCompressor instance
        
    Returns:
        List[Dict[str, str]]: Compressed messages
    """
    if compressor is None:
        compressor = ContextCompressor()
    
    compressed_messages = []
    
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        should_compress = (
            (role == "system" and compress_system) or
            (role == "user" and compress_user) or
            (role == "assistant" and compress_assistant)
        )
        
        if should_compress and content:
            try:
                result = compressor.compress(
                    text=content,
                    target_ratio=target_ratio,
                    strategy=strategy
                )
                compressed_content = result.compressed_text
            except Exception as e:
                logger.error(f"Failed to compress {role} message: {e}")
                compressed_content = content
        else:
            compressed_content = content
        
        compressed_messages.append({
            "role": role,
            "content": compressed_content
        })
    
    return compressed_messages


def batch_compress_for_openai(
    texts: List[str],
    target_ratio: float = 0.5,
    model: str = "gpt-3.5-turbo",
    strategy: str = "extractive",
    parallel: bool = True,
    compressor: Optional[ContextCompressor] = None,
    estimate_total_savings: bool = True
) -> Dict[str, Any]:
    """
    Batch compress multiple texts for OpenAI API usage.
    
    Args:
        texts: List of texts to compress
        target_ratio: Target compression ratio
        model: OpenAI model name
        strategy: Compression strategy to use
        parallel: Whether to use parallel processing
        compressor: Optional ContextCompressor instance
        estimate_total_savings: Whether to estimate total cost savings
        
    Returns:
        Dict[str, Any]: Batch compression results with cost analysis
    """
    if compressor is None:
        compressor = ContextCompressor()
    
    # Perform batch compression
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=target_ratio,
        strategy=strategy,
        parallel=parallel
    )
    
    # Calculate OpenAI-specific metrics
    if TIKTOKEN_AVAILABLE:
        tokenizer = OpenAITokenizer(model)
        total_original_tokens = sum(tokenizer.count(text) for text in texts)
        total_compressed_tokens = sum(
            tokenizer.count(result.compressed_text) 
            for result in batch_result.results
        )
    else:
        total_original_tokens = sum(result.original_tokens for result in batch_result.results)
        total_compressed_tokens = sum(result.compressed_tokens for result in batch_result.results)
    
    total_tokens_saved = total_original_tokens - total_compressed_tokens
    
    response = {
        'results': [
            {
                'compressed_text': result.compressed_text,
                'original_tokens': result.original_tokens,
                'compressed_tokens': result.compressed_tokens,
                'tokens_saved': result.tokens_saved,
                'compression_ratio': result.actual_ratio
            }
            for result in batch_result.results
        ],
        'summary': {
            'texts_processed': len(batch_result.results),
            'total_original_tokens': total_original_tokens,
            'total_compressed_tokens': total_compressed_tokens,
            'total_tokens_saved': total_tokens_saved,
            'average_compression_ratio': batch_result.average_compression_ratio,
            'processing_time': batch_result.total_processing_time,
            'model': model
        }
    }
    
    # Add cost estimation
    if estimate_total_savings:
        cost_info = estimate_openai_cost_savings(
            original_tokens=total_original_tokens,
            compressed_tokens=total_compressed_tokens,
            model=model
        )
        response['summary'].update(cost_info)
    
    return response


# Export main functions
__all__ = [
    'OpenAITokenizer',
    'compress_for_openai',
    'estimate_openai_cost_savings',
    'compress_for_chat_completion',
    'batch_compress_for_openai',
    'TIKTOKEN_AVAILABLE',
    'OPENAI_AVAILABLE'
]