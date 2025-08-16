"""
FastAPI REST API for Context Compressor.

This module provides a RESTful API interface for the Context Compressor
package, allowing remote compression services and microservice deployment.
"""

from typing import List, Optional, Dict, Any
import time
from datetime import datetime
import logging

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field, validator
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object
    Field = lambda *args, **kwargs: None

from ..core.compressor import ContextCompressor
from ..core.models import CompressionStats

logger = logging.getLogger(__name__)

# Global compressor instance
compressor_instance = None

def get_compressor() -> ContextCompressor:
    """Get or create the global compressor instance."""
    global compressor_instance
    if compressor_instance is None:
        compressor_instance = ContextCompressor()
    return compressor_instance


if FASTAPI_AVAILABLE:
    # Request/Response Models
    class CompressionRequest(BaseModel):
        """Request model for single text compression."""
        text: str = Field(..., description="Text to compress", min_length=1)
        target_ratio: float = Field(0.5, description="Target compression ratio", ge=0.1, le=0.9)
        strategy: str = Field("auto", description="Compression strategy to use")
        query: Optional[str] = Field(None, description="Optional query for context-aware compression")
        evaluate_quality: bool = Field(True, description="Whether to evaluate compression quality")
        
        @validator('text')
        def text_not_empty(cls, v):
            if not v.strip():
                raise ValueError('Text cannot be empty or whitespace only')
            return v
    
    
    class BatchCompressionRequest(BaseModel):
        """Request model for batch text compression."""
        texts: List[str] = Field(..., description="List of texts to compress", min_items=1)
        target_ratio: float = Field(0.5, description="Target compression ratio", ge=0.1, le=0.9)
        strategy: str = Field("auto", description="Compression strategy to use")
        query: Optional[str] = Field(None, description="Optional query for context-aware compression")
        parallel: bool = Field(True, description="Whether to process texts in parallel")
        evaluate_quality: bool = Field(True, description="Whether to evaluate compression quality")
        
        @validator('texts')
        def texts_not_empty(cls, v):
            if not all(text.strip() for text in v):
                raise ValueError('All texts must be non-empty')
            return v
    
    
    class CompressionResponse(BaseModel):
        """Response model for single text compression."""
        compressed_text: str
        original_tokens: int
        compressed_tokens: int
        actual_ratio: float
        tokens_saved: int
        strategy_used: str
        processing_time: float
        quality_metrics: Optional[Dict[str, float]] = None
        timestamp: str
    
    
    class BatchCompressionResponse(BaseModel):
        """Response model for batch text compression."""
        results: List[CompressionResponse]
        total_processing_time: float
        strategy_used: str
        target_ratio: float
        success_rate: float
        average_compression_ratio: float
        total_tokens_saved: int
        failed_items: List[Dict[str, Any]]
        timestamp: str
    
    
    class StrategyInfo(BaseModel):
        """Strategy information model."""
        name: str
        description: str
        version: str
        author: str
        supported_languages: List[str]
        optimal_compression_ratios: List[float]
        computational_complexity: str
        memory_requirements: str
        tags: List[str]
    
    
    class HealthResponse(BaseModel):
        """Health check response model."""
        status: str
        timestamp: str
        uptime_seconds: float
        version: str = "0.1.0"
        available_strategies: List[str]
        total_compressions: int
    
    
    class MetricsResponse(BaseModel):
        """Metrics response model."""
        total_compressions: int
        total_tokens_processed: int
        total_tokens_saved: int
        average_compression_ratio: float
        cache_hit_rate: float
        strategy_usage: Dict[str, int]
        uptime_seconds: float
    
    
    # FastAPI App
    app = FastAPI(
        title="AI Context Compressor API",
        description="RESTful API for intelligent text compression with semantic meaning preservation",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Track API start time
    API_START_TIME = time.time()
    
    
    @app.post("/compress", response_model=CompressionResponse)
    async def compress_text(
        request: CompressionRequest,
        compressor: ContextCompressor = Depends(get_compressor)
    ):
        """
        Compress a single text using the specified strategy.
        
        - **text**: The input text to compress
        - **target_ratio**: Target compression ratio (0.1 to 0.9)
        - **strategy**: Compression strategy ("auto", "extractive", etc.)
        - **query**: Optional query for context-aware compression
        - **evaluate_quality**: Whether to evaluate compression quality
        """
        try:
            result = compressor.compress(
                text=request.text,
                target_ratio=request.target_ratio,
                strategy=request.strategy,
                query=request.query,
                evaluate_quality=request.evaluate_quality
            )
            
            quality_metrics = None
            if result.quality_metrics:
                quality_metrics = result.quality_metrics.to_dict()
            
            return CompressionResponse(
                compressed_text=result.compressed_text,
                original_tokens=result.original_tokens,
                compressed_tokens=result.compressed_tokens,
                actual_ratio=result.actual_ratio,
                tokens_saved=result.tokens_saved,
                strategy_used=result.strategy_used,
                processing_time=result.processing_time,
                quality_metrics=quality_metrics,
                timestamp=datetime.now().isoformat()
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Compression error: {e}")
            raise HTTPException(status_code=500, detail="Internal compression error")
    
    
    @app.post("/compress/batch", response_model=BatchCompressionResponse)
    async def compress_batch(
        request: BatchCompressionRequest,
        compressor: ContextCompressor = Depends(get_compressor)
    ):
        """
        Compress multiple texts in batch.
        
        - **texts**: List of input texts to compress
        - **target_ratio**: Target compression ratio (0.1 to 0.9)
        - **strategy**: Compression strategy to use
        - **query**: Optional query for context-aware compression
        - **parallel**: Whether to process texts in parallel
        - **evaluate_quality**: Whether to evaluate compression quality
        """
        try:
            batch_result = compressor.compress_batch(
                texts=request.texts,
                target_ratio=request.target_ratio,
                strategy=request.strategy,
                query=request.query,
                parallel=request.parallel,
                evaluate_quality=request.evaluate_quality
            )
            
            # Convert individual results
            results = []
            for result in batch_result.results:
                quality_metrics = None
                if result.quality_metrics:
                    quality_metrics = result.quality_metrics.to_dict()
                
                results.append(CompressionResponse(
                    compressed_text=result.compressed_text,
                    original_tokens=result.original_tokens,
                    compressed_tokens=result.compressed_tokens,
                    actual_ratio=result.actual_ratio,
                    tokens_saved=result.tokens_saved,
                    strategy_used=result.strategy_used,
                    processing_time=result.processing_time,
                    quality_metrics=quality_metrics,
                    timestamp=result.timestamp.isoformat()
                ))
            
            return BatchCompressionResponse(
                results=results,
                total_processing_time=batch_result.total_processing_time,
                strategy_used=batch_result.strategy_used,
                target_ratio=request.target_ratio,
                success_rate=batch_result.success_rate,
                average_compression_ratio=batch_result.average_compression_ratio,
                total_tokens_saved=batch_result.total_tokens_saved,
                failed_items=batch_result.failed_items,
                timestamp=datetime.now().isoformat()
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Batch compression error: {e}")
            raise HTTPException(status_code=500, detail="Internal batch compression error")
    
    
    @app.get("/strategies", response_model=List[StrategyInfo])
    async def list_strategies(compressor: ContextCompressor = Depends(get_compressor)):
        """
        List all available compression strategies with their metadata.
        """
        strategies = []
        
        for strategy_name in compressor.list_strategies():
            strategy_info = compressor.get_strategy_info(strategy_name)
            if strategy_info:
                strategies.append(StrategyInfo(**strategy_info))
        
        return strategies
    
    
    @app.get("/strategies/{strategy_name}", response_model=StrategyInfo)
    async def get_strategy_info(
        strategy_name: str,
        compressor: ContextCompressor = Depends(get_compressor)
    ):
        """
        Get detailed information about a specific compression strategy.
        """
        strategy_info = compressor.get_strategy_info(strategy_name)
        
        if not strategy_info:
            raise HTTPException(
                status_code=404, 
                detail=f"Strategy '{strategy_name}' not found"
            )
        
        return StrategyInfo(**strategy_info)
    
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check(compressor: ContextCompressor = Depends(get_compressor)):
        """
        Health check endpoint for monitoring and load balancer probes.
        """
        uptime = time.time() - API_START_TIME
        stats = compressor.get_stats()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=uptime,
            available_strategies=compressor.list_strategies(),
            total_compressions=stats.get('total_compressions', 0)
        )
    
    
    @app.get("/metrics", response_model=MetricsResponse)
    async def get_metrics(compressor: ContextCompressor = Depends(get_compressor)):
        """
        Get performance metrics and statistics.
        """
        stats = compressor.get_stats()
        uptime = time.time() - API_START_TIME
        
        return MetricsResponse(
            total_compressions=stats.get('total_compressions', 0),
            total_tokens_processed=stats.get('total_tokens_processed', 0),
            total_tokens_saved=stats.get('total_tokens_saved', 0),
            average_compression_ratio=stats.get('average_compression_ratio', 0.0),
            cache_hit_rate=stats.get('cache_hit_rate', 0.0),
            strategy_usage=stats.get('strategy_usage', {}),
            uptime_seconds=uptime
        )
    
    
    @app.post("/cache/clear")
    async def clear_cache(compressor: ContextCompressor = Depends(get_compressor)):
        """
        Clear the compression cache.
        """
        compressor.clear_cache()
        return {"message": "Cache cleared successfully"}
    
    
    @app.post("/stats/reset")
    async def reset_stats(compressor: ContextCompressor = Depends(get_compressor)):
        """
        Reset compression statistics.
        """
        compressor.reset_stats()
        return {"message": "Statistics reset successfully"}
    
    
    # Error handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return HTTPException(status_code=400, detail=str(exc))
    
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled error: {exc}")
        return HTTPException(status_code=500, detail="Internal server error")
    
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    # Fallback when FastAPI is not available
    def create_app():
        raise ImportError(
            "FastAPI is not installed. Install with: pip install 'context-compressor[api]'"
        )
    
    app = None