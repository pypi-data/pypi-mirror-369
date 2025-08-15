"""
Integration modules for Context Compressor.

This package provides integrations with popular AI frameworks and services.
"""

# Try to import integrations (may fail if dependencies not installed)
try:
    from .langchain import (
        ContextCompressorTransformer,
        compress_documents,
        compress_document_content,
        LANGCHAIN_AVAILABLE
    )
    __all__ = ['ContextCompressorTransformer', 'compress_documents', 'compress_document_content']
except ImportError:
    LANGCHAIN_AVAILABLE = False
    __all__ = []

try:
    from .openai import (
        OpenAITokenizer,
        compress_for_openai,
        estimate_openai_cost_savings,
        compress_for_chat_completion,
        batch_compress_for_openai,
        TIKTOKEN_AVAILABLE,
        OPENAI_AVAILABLE
    )
    __all__.extend([
        'OpenAITokenizer',
        'compress_for_openai', 
        'estimate_openai_cost_savings',
        'compress_for_chat_completion',
        'batch_compress_for_openai'
    ])
except ImportError:
    TIKTOKEN_AVAILABLE = False
    OPENAI_AVAILABLE = False