# Context Compressor

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI Version](https://img.shields.io/pypi/v/context-compressor.svg)](https://pypi.org/project/context-compressor/)
[![Downloads](https://img.shields.io/pypi/dm/context-compressor.svg)](https://pypi.org/project/context-compressor/)

**The most powerful AI-powered text compression library for RAG systems and API calls. Reduce token usage by up to 80% while preserving semantic meaning with state-of-the-art compression strategies.**

*Developed by Mohammed Huzaifa*

## 🚀 Features

### Core Compression Engine
- **4 Advanced Compression Strategies**: Extractive, Abstractive, Semantic, and Hybrid approaches using state-of-the-art AI models
- **Transformer-Powered**: Built on BERT, BART, T5, and other cutting-edge models for maximum compression quality
- **Query-Aware Intelligence**: Context-aware compression that prioritizes relevant content based on user queries
- **Multi-Model Support**: Works with OpenAI GPT, Anthropic Claude, Google PaLM, and custom models

### Quality & Performance
- **Comprehensive Quality Metrics**: ROUGE scores, semantic similarity, entity preservation, readability analysis
- **Up to 80% Token Reduction**: Achieve massive cost savings while maintaining content quality
- **Parallel Batch Processing**: High-performance processing of thousands of documents
- **Intelligent Caching**: Advanced TTL-based caching with cleanup for optimal performance

### Enterprise-Ready Integrations
- **LangChain Integration**: Seamless document transformer for RAG pipelines
- **OpenAI API Optimization**: Direct integration with GPT models and token counting
- **Anthropic Claude Support**: Native integration with Claude API
- **REST API Service**: Production-ready FastAPI microservice with OpenAPI documentation
- **Framework Agnostic**: Works with any Python ML/AI framework

### Advanced Features
- **Custom Strategy Development**: Plugin system for implementing custom compression algorithms
- **Real-time Monitoring**: Built-in metrics and performance tracking
- **Visualization Tools**: Matplotlib, Seaborn, and Plotly integration for compression analytics
- **NLP Enhancement**: SpaCy, NLTK integration for advanced text processing
- **Production Deployment**: Docker, Kubernetes, and cloud deployment ready

## 📦 Installation

### Full Installation (Recommended)

```bash
pip install context-compressor
```

*This now includes ALL features by default: ML models, API service, integrations, and NLP processing.*

### Advanced Installation Options

```bash
# For specific features only (legacy support)
pip install "context-compressor[ml]"          # ML models only
pip install "context-compressor[api]"         # API service only
pip install "context-compressor[integrations]" # Framework integrations
pip install "context-compressor[nlp]"         # NLP enhancements

# Development installation
pip install "context-compressor[dev]"         # Testing and development tools
pip install "context-compressor[docs]"        # Documentation generation
```

### Development Installation

```bash
git clone https://github.com/Huzaifa785/context-compressor.git
cd context-compressor
pip install -e ".[dev]"
```

## 🏁 Quick Start

### Basic Usage

```python
from context_compressor import ContextCompressor

# Initialize the compressor
compressor = ContextCompressor()

# Compress text
text = """
Artificial Intelligence (AI) is a broad field of computer science focused on 
creating systems that can perform tasks that typically require human intelligence. 
These tasks include learning, reasoning, problem-solving, perception, and language 
understanding. AI has applications in various domains including healthcare, finance, 
transportation, and entertainment. Machine learning, a subset of AI, enables 
computers to learn and improve from experience without being explicitly programmed.
"""

result = compressor.compress(text, target_ratio=0.5)

print("Original text:")
print(text)
print(f"\nCompressed text ({result.actual_ratio:.1%} of original):")
print(result.compressed_text)
print(f"\nTokens saved: {result.tokens_saved}")
print(f"Quality score: {result.quality_metrics.overall_score:.2f}")
```

### Query-Aware Compression

```python
# Compress with focus on specific topic
query = "machine learning applications"

result = compressor.compress(
    text=text,
    target_ratio=0.3,
    query=query
)

print(f"Query-focused compression: {result.compressed_text}")
```

### Batch Processing

```python
texts = [
    "First document about AI and machine learning...",
    "Second document about natural language processing...",
    "Third document about computer vision..."
]

batch_result = compressor.compress_batch(
    texts=texts,
    target_ratio=0.4,
    parallel=True
)

print(f"Processed {len(batch_result.results)} texts")
print(f"Average compression ratio: {batch_result.average_compression_ratio:.1%}")
print(f"Total tokens saved: {batch_result.total_tokens_saved}")
```

## 🔧 Configuration

### Strategy Selection

```python
from context_compressor import ContextCompressor
from context_compressor.strategies import ExtractiveStrategy

# Use specific strategy
extractive_strategy = ExtractiveStrategy(
    scoring_method="tfidf",
    min_sentence_length=20,
    position_bias=0.2
)

compressor = ContextCompressor(strategies=[extractive_strategy])

# Or let the system auto-select
compressor = ContextCompressor(default_strategy="auto")
```

### Quality Evaluation Settings

```python
compressor = ContextCompressor(
    enable_quality_evaluation=True,
    enable_caching=True,
    cache_ttl=3600  # 1 hour
)

result = compressor.compress(text, target_ratio=0.5)

# Access detailed quality metrics
print(f"ROUGE-1: {result.quality_metrics.rouge_1:.3f}")
print(f"ROUGE-2: {result.quality_metrics.rouge_2:.3f}")
print(f"ROUGE-L: {result.quality_metrics.rouge_l:.3f}")
print(f"Semantic similarity: {result.quality_metrics.semantic_similarity:.3f}")
print(f"Entity preservation: {result.quality_metrics.entity_preservation_rate:.3f}")
```

## 🎯 Compression Strategies

### 1. Extractive Strategy (Default)

Selects important sentences based on TF-IDF, position, and query relevance:

```python
from context_compressor.strategies import ExtractiveStrategy

strategy = ExtractiveStrategy(
    scoring_method="combined",  # "tfidf", "frequency", "position", "combined"
    min_sentence_length=10,
    position_bias=0.2,
    query_weight=0.3
)
```

### 2. Abstractive Strategy (Requires ML dependencies)

Uses transformer models for summarization:

```python
from context_compressor.strategies import AbstractiveStrategy

strategy = AbstractiveStrategy(
    model_name="facebook/bart-large-cnn",
    max_length=150,
    min_length=50
)
```

### 3. Semantic Strategy (Requires ML dependencies)

Groups similar content using embeddings:

```python
from context_compressor.strategies import SemanticStrategy

strategy = SemanticStrategy(
    embedding_model="all-MiniLM-L6-v2",
    clustering_method="kmeans",
    n_clusters="auto"
)
```

### 4. Hybrid Strategy

Combines multiple strategies for optimal results:

```python
from context_compressor.strategies import HybridStrategy

strategy = HybridStrategy(
    primary_strategy="extractive",
    secondary_strategy="semantic",
    combination_method="weighted"
)
```

## 🔌 Integrations

### LangChain Integration

```python
from context_compressor.integrations.langchain import ContextCompressorTransformer

# Use as a document transformer
transformer = ContextCompressorTransformer(
    compressor=compressor,
    target_ratio=0.6
)

# Apply to document chain
compressed_docs = transformer.transform_documents(documents)
```

### OpenAI Integration

```python
from context_compressor.integrations.openai import compress_for_openai

# Compress text before sending to OpenAI API
compressed_prompt = compress_for_openai(
    text=long_context,
    target_ratio=0.4,
    model="gpt-4"  # Automatically uses appropriate tokenizer
)
```

## 🌐 REST API

Start the API server:

```bash
uvicorn context_compressor.api.main:app --reload
```

### API Endpoints

#### Compress Text

```bash
curl -X POST "http://localhost:8000/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "target_ratio": 0.5,
    "strategy": "extractive",
    "query": "optional query"
  }'
```

#### Batch Compression

```bash
curl -X POST "http://localhost:8000/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Text 1...", "Text 2...", "Text 3..."],
    "target_ratio": 0.4,
    "parallel": true
  }'
```

#### List Available Strategies

```bash
curl "http://localhost:8000/strategies"
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📊 Quality Metrics

The system provides comprehensive quality evaluation:

- **Semantic Similarity**: Measures content preservation using word embeddings
- **ROUGE Scores**: Standard summarization metrics (ROUGE-1, ROUGE-2, ROUGE-L)
- **Entity Preservation**: Tracks retention of named entities, numbers, dates
- **Readability**: Flesch Reading Ease score for text readability
- **Overall Score**: Weighted combination of all metrics

## 🎛️ Advanced Configuration

### Custom Strategy Development

```python
from context_compressor.strategies.base import CompressionStrategy
from context_compressor.core.models import StrategyMetadata

class CustomStrategy(CompressionStrategy):
    def _create_metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            name="custom",
            description="Custom compression strategy",
            version="1.0.0",
            author="Your Name"
        )
    
    def _compress_text(self, text: str, target_ratio: float, **kwargs) -> str:
        # Implement your compression logic
        return compressed_text

# Register and use
compressor.register_strategy(CustomStrategy())
```

### Cache Configuration

```python
from context_compressor.utils.cache import CacheManager

# Custom cache manager
cache_manager = CacheManager(
    ttl=7200,  # 2 hours
    max_size=2000,
    cleanup_interval=600  # 10 minutes
)

compressor = ContextCompressor(cache_manager=cache_manager)
```

## 📈 Performance Optimization

### Batch Processing Tips

```python
# For large batches, adjust worker count
batch_result = compressor.compress_batch(
    texts=large_text_list,
    target_ratio=0.5,
    parallel=True,
    max_workers=8  # Adjust based on your system
)
```

### Memory Management

```python
# For memory-constrained environments
compressor = ContextCompressor(
    enable_caching=False,  # Disable caching
    enable_quality_evaluation=False  # Skip quality evaluation
)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=context_compressor

# Run only unit tests
pytest -m "not integration"

# Run specific test file
pytest tests/test_compressor.py
```

## 📚 Examples

Check out the `examples/` directory for comprehensive usage examples:

- `examples/basic_usage.py` - Basic compression examples
- `examples/batch_processing.py` - Batch processing examples
- `examples/quality_evaluation.py` - Quality metrics examples
- `examples/custom_strategy.py` - Custom strategy development
- `examples/integration_examples.py` - Framework integration examples
- `examples/api_client.py` - REST API client examples

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/Huzaifa785/context-compressor.git
cd context-compressor
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest
black .
isort .
flake8 .
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://context-compressor.readthedocs.io](https://context-compressor.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/Huzaifa785/context-compressor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Huzaifa785/context-compressor/discussions)
- **PyPI Package**: [https://pypi.org/project/context-compressor/](https://pypi.org/project/context-compressor/)

## 🗺️ Roadmap

- [ ] Additional compression strategies (neural, attention-based)
- [ ] Multi-language support
- [ ] Integration with more LLM providers
- [ ] GUI interface
- [ ] Cloud deployment templates
- [ ] Performance benchmarking suite

## 📖 Citation

If you use Context Compressor in your research, please cite:

```bibtex
@software{context_compressor,
  title={Context Compressor: AI-Powered Text Compression for RAG Systems},
  author={Mohammed Huzaifa},
  url={https://github.com/Huzaifa785/context-compressor},
  year={2024},
  version={1.0.0}
}
```

---

**Made with ❤️ by Mohammed Huzaifa for the AI community**

## 🏆 Why Choose Context Compressor?

- **Production Ready**: Version 1.0.0 with comprehensive testing and documentation
- **Maximum Performance**: State-of-the-art compression algorithms with up to 80% token reduction
- **Enterprise Support**: Full-featured API, monitoring, and deployment tools
- **Complete Package**: All dependencies included by default - no complex setup required
- **Active Development**: Regular updates and feature additions
- **Community Driven**: Open source with active community support