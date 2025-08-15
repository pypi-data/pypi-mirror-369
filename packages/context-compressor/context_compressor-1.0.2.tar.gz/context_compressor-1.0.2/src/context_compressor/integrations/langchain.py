"""
LangChain integration for Context Compressor.

This module provides integration with LangChain framework for
document processing and chain composition.
"""

from typing import List, Optional, Any, Dict
import logging

try:
    from langchain.schema import Document
    from langchain.schema.document_transformer import BaseDocumentTransformer
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    Document = Any
    BaseDocumentTransformer = object

from ..core.compressor import ContextCompressor

logger = logging.getLogger(__name__)


class ContextCompressorTransformer(BaseDocumentTransformer):
    """
    LangChain document transformer that compresses document content.
    
    This transformer can be used in LangChain pipelines to compress
    documents before further processing.
    
    Example:
        >>> from context_compressor.integrations.langchain import ContextCompressorTransformer
        >>> transformer = ContextCompressorTransformer(target_ratio=0.6)
        >>> compressed_docs = transformer.transform_documents(documents)
    """
    
    def __init__(
        self,
        compressor: Optional[ContextCompressor] = None,
        target_ratio: float = 0.5,
        strategy: str = "extractive",
        query: Optional[str] = None,
        preserve_metadata: bool = True,
        **kwargs
    ):
        """
        Initialize the LangChain transformer.
        
        Args:
            compressor: ContextCompressor instance (created if None)
            target_ratio: Target compression ratio
            strategy: Compression strategy to use
            query: Optional query for context-aware compression
            preserve_metadata: Whether to preserve document metadata
            **kwargs: Additional arguments for ContextCompressor
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install with: pip install langchain"
            )
        
        self.compressor = compressor or ContextCompressor(**kwargs)
        self.target_ratio = target_ratio
        self.strategy = strategy
        self.query = query
        self.preserve_metadata = preserve_metadata
    
    def transform_documents(
        self, 
        documents: List[Document], 
        **kwargs: Any
    ) -> List[Document]:
        """
        Transform documents by compressing their content.
        
        Args:
            documents: List of LangChain Document objects
            **kwargs: Additional arguments (can override instance settings)
            
        Returns:
            List[Document]: List of compressed Document objects
        """
        compressed_docs = []
        
        # Get parameters (allow override via kwargs)
        target_ratio = kwargs.get('target_ratio', self.target_ratio)
        strategy = kwargs.get('strategy', self.strategy)
        query = kwargs.get('query', self.query)
        
        for doc in documents:
            try:
                # Compress document content
                result = self.compressor.compress(
                    text=doc.page_content,
                    target_ratio=target_ratio,
                    strategy=strategy,
                    query=query
                )
                
                # Create new document with compressed content
                compressed_doc = Document(
                    page_content=result.compressed_text,
                    metadata=doc.metadata.copy() if self.preserve_metadata else {}
                )
                
                # Add compression metadata
                if self.preserve_metadata:
                    compressed_doc.metadata.update({
                        'compression_ratio': result.actual_ratio,
                        'original_tokens': result.original_tokens,
                        'compressed_tokens': result.compressed_tokens,
                        'tokens_saved': result.tokens_saved,
                        'compression_strategy': result.strategy_used,
                        'processing_time': result.processing_time
                    })
                
                compressed_docs.append(compressed_doc)
                
            except Exception as e:
                logger.error(f"Failed to compress document: {e}")
                # Return original document if compression fails
                compressed_docs.append(doc)
        
        return compressed_docs
    
    async def atransform_documents(
        self, 
        documents: List[Document], 
        **kwargs: Any
    ) -> List[Document]:
        """
        Async version of transform_documents.
        
        Args:
            documents: List of LangChain Document objects
            **kwargs: Additional arguments
            
        Returns:
            List[Document]: List of compressed Document objects
        """
        # For now, just call the sync version
        # Could be enhanced with actual async processing
        return self.transform_documents(documents, **kwargs)


def compress_documents(
    documents: List[Document],
    target_ratio: float = 0.5,
    strategy: str = "extractive",
    query: Optional[str] = None,
    compressor: Optional[ContextCompressor] = None,
    preserve_metadata: bool = True
) -> List[Document]:
    """
    Utility function to compress LangChain documents.
    
    Args:
        documents: List of LangChain Document objects
        target_ratio: Target compression ratio
        strategy: Compression strategy to use
        query: Optional query for context-aware compression
        compressor: Optional ContextCompressor instance
        preserve_metadata: Whether to preserve document metadata
        
    Returns:
        List[Document]: List of compressed Document objects
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is not installed. Install with: pip install langchain"
        )
    
    transformer = ContextCompressorTransformer(
        compressor=compressor,
        target_ratio=target_ratio,
        strategy=strategy,
        query=query,
        preserve_metadata=preserve_metadata
    )
    
    return transformer.transform_documents(documents)


def compress_document_content(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    target_ratio: float = 0.5,
    strategy: str = "extractive",
    query: Optional[str] = None,
    compressor: Optional[ContextCompressor] = None
) -> Document:
    """
    Compress text content and return as LangChain Document.
    
    Args:
        content: Text content to compress
        metadata: Optional metadata dictionary
        target_ratio: Target compression ratio
        strategy: Compression strategy to use
        query: Optional query for context-aware compression
        compressor: Optional ContextCompressor instance
        
    Returns:
        Document: LangChain Document with compressed content
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is not installed. Install with: pip install langchain"
        )
    
    if compressor is None:
        compressor = ContextCompressor()
    
    # Compress the content
    result = compressor.compress(
        text=content,
        target_ratio=target_ratio,
        strategy=strategy,
        query=query
    )
    
    # Create document with compressed content
    doc_metadata = metadata or {}
    doc_metadata.update({
        'compression_ratio': result.actual_ratio,
        'original_tokens': result.original_tokens,
        'compressed_tokens': result.compressed_tokens,
        'tokens_saved': result.tokens_saved,
        'compression_strategy': result.strategy_used,
        'processing_time': result.processing_time
    })
    
    return Document(
        page_content=result.compressed_text,
        metadata=doc_metadata
    )


# Export main classes and functions
__all__ = [
    'ContextCompressorTransformer',
    'compress_documents',
    'compress_document_content',
    'LANGCHAIN_AVAILABLE'
]