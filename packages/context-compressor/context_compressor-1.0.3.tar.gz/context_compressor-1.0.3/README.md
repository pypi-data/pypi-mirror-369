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

**Expected Output:**
```
Original text:
Artificial Intelligence (AI) is a broad field of computer science focused on 
creating systems that can perform tasks that typically require human intelligence. 
These tasks include learning, reasoning, problem-solving, perception, and language 
understanding. AI has applications in various domains including healthcare, finance, 
transportation, and entertainment. Machine learning, a subset of AI, enables 
computers to learn and improve from experience without being explicitly programmed.

Compressed text (45.2% of original):
Artificial Intelligence (AI) creates systems performing human-like tasks: learning, 
reasoning, problem-solving, perception, language understanding. AI applications span 
healthcare, finance, transportation, entertainment. Machine learning enables computers 
to learn from experience without explicit programming.

Tokens saved: 32
Quality score: 0.87
```

### 📊 Complete Response Structure

The `compress()` method returns a `CompressionResult` object with comprehensive information:

```python
from context_compressor import ContextCompressor

compressor = ContextCompressor(enable_quality_evaluation=True)
result = compressor.compress(text, target_ratio=0.5)

# Access all result properties
print(f"Strategy used: {result.strategy_used}")
print(f"Original tokens: {result.original_tokens}")
print(f"Compressed tokens: {result.compressed_tokens}")
print(f"Target ratio: {result.target_ratio}")
print(f"Actual ratio: {result.actual_ratio:.3f}")
print(f"Processing time: {result.processing_time:.3f}s")
print(f"Timestamp: {result.timestamp}")

# Quality metrics (if enabled)
if result.quality_metrics:
    metrics = result.quality_metrics
    print(f"\nQuality Metrics:")
    print(f"  Semantic similarity: {metrics.semantic_similarity:.3f}")
    print(f"  ROUGE-1: {metrics.rouge_1:.3f}")
    print(f"  ROUGE-2: {metrics.rouge_2:.3f}")
    print(f"  ROUGE-L: {metrics.rouge_l:.3f}")
    print(f"  Entity preservation: {metrics.entity_preservation_rate:.3f}")
    print(f"  Readability score: {metrics.readability_score:.1f}")
    print(f"  Overall score: {metrics.overall_score:.3f}")

# Additional properties
print(f"\nDerived Properties:")
print(f"  Tokens saved: {result.tokens_saved}")
print(f"  Token savings %: {result.token_savings_percentage:.1f}%")
print(f"  Compression efficiency: {result.compression_efficiency:.3f}")

# Export to dictionary or JSON
result_dict = result.to_dict()
result_json = result.to_json(indent=2)
result.save_to_file('compression_result.json')
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
print(f"Query used: {result.query}")
print(f"Compression ratio: {result.actual_ratio:.1%}")
```

**Output with Query Focus:**
```
Query-focused compression: Machine learning, AI subset, enables computers 
to learn from experience. AI applications include healthcare, finance, 
transportation, entertainment domains.

Query used: machine learning applications
Compression ratio: 28.3%
```

**Comparison - Without Query:**
```python
result_no_query = compressor.compress(text, target_ratio=0.3)
print(f"Without query: {result_no_query.compressed_text}")
# Output: Artificial Intelligence creates systems performing human tasks. 
# Learning, reasoning, problem-solving, perception, language understanding.
```

### Batch Processing

```python
texts = [
    "Artificial Intelligence revolutionizes industries through automated decision-making, "
    "pattern recognition, and predictive analytics across healthcare, finance, and technology sectors.",
    "Natural Language Processing enables computers to understand, interpret, and generate "
    "human language through tokenization, sentiment analysis, and semantic understanding.",
    "Computer Vision allows machines to identify, analyze, and interpret visual information "
    "from images and videos using convolutional neural networks and deep learning algorithms."
]

batch_result = compressor.compress_batch(
    texts=texts,
    target_ratio=0.4,
    parallel=True,
    max_workers=4
)

# Comprehensive batch results
print(f"Batch Processing Results:")
print(f"  Processed: {len(batch_result.results)} texts")
print(f"  Success rate: {batch_result.success_rate:.1%}")
print(f"  Total processing time: {batch_result.total_processing_time:.3f}s")
print(f"  Parallel processing: {batch_result.parallel_processing}")
print(f"  Average compression ratio: {batch_result.average_compression_ratio:.1%}")
print(f"  Total tokens saved: {batch_result.total_tokens_saved}")
print(f"  Average quality score: {batch_result.average_quality_score:.3f}")

# Individual results
for i, result in enumerate(batch_result.results):
    print(f"\nText {i+1}:")
    print(f"  Original length: {len(result.original_text)} chars")
    print(f"  Compressed: {result.compressed_text[:100]}...")
    print(f"  Compression: {result.actual_ratio:.1%}")
    print(f"  Tokens saved: {result.tokens_saved}")

# Failed items (if any)
if batch_result.failed_items:
    print(f"\nFailed items: {len(batch_result.failed_items)}")
    for failed in batch_result.failed_items:
        print(f"  Error: {failed['error']}")
```

**Expected Batch Output:**
```
Batch Processing Results:
  Processed: 3 texts
  Success rate: 100.0%
  Total processing time: 0.245s
  Parallel processing: True
  Average compression ratio: 42.1%
  Total tokens saved: 87
  Average quality score: 0.854

Text 1:
  Original length: 142 chars
  Compressed: AI revolutionizes industries through automated decisions, pattern recognition, predictive...
  Compression: 41.5%
  Tokens saved: 28

Text 2:
  Original length: 138 chars
  Compressed: NLP enables computers to understand, interpret, generate human language via tokenization...
  Compression: 43.2%
  Tokens saved: 31

Text 3:
  Original length: 145 chars
  Compressed: Computer Vision allows machines to analyze visual information using CNNs, deep learning...
  Compression: 41.7%
  Tokens saved: 28
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

## 🎯 Compression Strategies with Examples

### 1. Extractive Strategy (Default) 🎫

Extracts the most important sentences using advanced scoring algorithms:

```python
from context_compressor import ContextCompressor
from context_compressor.strategies import ExtractiveStrategy

# Configure extractive strategy
strategy = ExtractiveStrategy(
    scoring_method="combined",  # "tfidf", "frequency", "position", "combined"
    min_sentence_length=10,
    position_bias=0.2,
    query_weight=0.3
)

compressor = ContextCompressor(strategies=[strategy])

text = """
Climate change is one of the most pressing issues of our time. Rising global temperatures 
have led to melting ice caps and rising sea levels. Scientists worldwide are studying 
the effects of greenhouse gas emissions on our planet's atmosphere. The Paris Agreement 
of 2015 brought together 196 countries to combat climate change. Renewable energy sources 
like solar and wind power are becoming increasingly important. Governments and corporations 
are investing heavily in clean technology solutions. Individual actions like reducing 
carbon footprints also play a crucial role in addressing this global challenge.
"""

result = compressor.compress(text, target_ratio=0.5)

print(f"Strategy: {result.strategy_used}")
print(f"Compression: {result.actual_ratio:.1%}")
print(f"Output: {result.compressed_text}")
```

**Extractive Output Example:**
```
Strategy: extractive
Compression: 48.3%
Output: Climate change is one of the most pressing issues of our time. Rising global 
temperatures have led to melting ice caps and rising sea levels. The Paris Agreement 
of 2015 brought together 196 countries to combat climate change. Renewable energy 
sources like solar and wind power are becoming increasingly important.
```

### 2. Abstractive Strategy (AI-Powered) 🤖

Generates new, concise text using transformer models:

```python
from context_compressor.strategies import AbstractiveStrategy

# Configure abstractive strategy
strategy = AbstractiveStrategy(
    model_name="facebook/bart-large-cnn",
    max_length=150,
    min_length=50,
    do_sample=False,
    early_stopping=True
)

compressor = ContextCompressor(strategies=[strategy])
result = compressor.compress(text, target_ratio=0.4)

print(f"Strategy: {result.strategy_used}")
print(f"Compression: {result.actual_ratio:.1%}")
print(f"Output: {result.compressed_text}")
print(f"Quality Score: {result.quality_metrics.overall_score:.3f}")
```

**Abstractive Output Example:**
```
Strategy: abstractive
Compression: 39.7%
Output: Climate change, driven by greenhouse gas emissions, causes rising temperatures 
and sea levels. The 2015 Paris Agreement united 196 countries to address this challenge 
through renewable energy investments and clean technology solutions.

Quality Score: 0.912
```

### 3. Semantic Strategy (Clustering-Based) 🧠

Groups similar content and selects representative sentences:

```python
from context_compressor.strategies import SemanticStrategy

# Configure semantic strategy
strategy = SemanticStrategy(
    embedding_model="all-MiniLM-L6-v2",
    clustering_method="kmeans",
    n_clusters="auto",  # or specific number like 3
    similarity_threshold=0.7
)

compressor = ContextCompressor(strategies=[strategy])
result = compressor.compress(text, target_ratio=0.6)

print(f"Strategy: {result.strategy_used}")
print(f"Compression: {result.actual_ratio:.1%}")
print(f"Output: {result.compressed_text}")
print(f"Semantic Similarity: {result.quality_metrics.semantic_similarity:.3f}")
```

**Semantic Output Example:**
```
Strategy: semantic
Compression: 58.2%
Output: Climate change is one of the most pressing issues of our time. Scientists 
worldwide are studying the effects of greenhouse gas emissions. The Paris Agreement 
of 2015 brought together 196 countries to combat climate change. Governments and 
corporations are investing heavily in clean technology solutions.

Semantic Similarity: 0.887
```

### 4. Hybrid Strategy (Best of All Worlds) ✨

Combines multiple strategies for optimal results:

```python
from context_compressor.strategies import HybridStrategy

# Configure hybrid strategy
strategy = HybridStrategy(
    primary_strategy="extractive",
    secondary_strategy="semantic",
    combination_method="weighted",
    primary_weight=0.7,
    secondary_weight=0.3
)

compressor = ContextCompressor(strategies=[strategy])
result = compressor.compress(text, target_ratio=0.45)

print(f"Strategy: {result.strategy_used}")
print(f"Compression: {result.actual_ratio:.1%}")
print(f"Output: {result.compressed_text}")
print(f"Compression Efficiency: {result.compression_efficiency:.3f}")
```

**Hybrid Output Example:**
```
Strategy: hybrid
Compression: 44.1%
Output: Climate change is one of the most pressing issues of our time. Rising global 
temperatures have led to melting ice caps and rising sea levels. The Paris Agreement 
brought together 196 countries to combat climate change. Renewable energy sources 
are becoming increasingly important for clean technology solutions.

Compression Efficiency: 0.394
```

### 📈 Strategy Comparison

```python
# Compare all strategies on the same text
strategies = [
    ("extractive", ExtractiveStrategy()),
    ("abstractive", AbstractiveStrategy(model_name="facebook/bart-large-cnn")),
    ("semantic", SemanticStrategy()),
    ("hybrid", HybridStrategy())
]

comparison_results = []
for name, strategy in strategies:
    compressor = ContextCompressor(strategies=[strategy])
    result = compressor.compress(text, target_ratio=0.5)
    comparison_results.append({
        'strategy': name,
        'compression': result.actual_ratio,
        'tokens_saved': result.tokens_saved,
        'quality': result.quality_metrics.overall_score if result.quality_metrics else None,
        'time': result.processing_time
    })

# Display comparison
for result in comparison_results:
    print(f"{result['strategy']:<12} | "
          f"Compression: {result['compression']:<5.1%} | "
          f"Tokens Saved: {result['tokens_saved']:<3} | "
          f"Quality: {result['quality']:<5.3f} | "
          f"Time: {result['time']:<6.3f}s")
```

**Strategy Comparison Output:**
```
extractive    | Compression: 48.3% | Tokens Saved: 31  | Quality: 0.854 | Time: 0.089s
abstractive  | Compression: 39.7% | Tokens Saved: 38  | Quality: 0.912 | Time: 1.245s
semantic     | Compression: 58.2% | Tokens Saved: 26  | Quality: 0.887 | Time: 0.234s
hybrid       | Compression: 44.1% | Tokens Saved: 35  | Quality: 0.891 | Time: 0.156s
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

### 📚 API Endpoints & Response Structures

#### Compress Text

**Request:**
```bash
curl -X POST "http://localhost:8000/compress" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial Intelligence (AI) is transforming industries through automation, machine learning, and data analytics. Companies leverage AI for predictive modeling, natural language processing, and computer vision applications across healthcare, finance, and technology sectors.",
    "target_ratio": 0.5,
    "strategy": "extractive",
    "query": "AI applications in healthcare",
    "enable_quality_evaluation": true
  }'
```

**Response Structure:**
```json
{
  "compressed_text": "AI transforms industries through automation, ML, analytics. Companies use AI for predictive modeling, NLP, computer vision in healthcare, finance, technology.",
  "original_text": "Artificial Intelligence (AI) is transforming...",
  "strategy_used": "extractive",
  "target_ratio": 0.5,
  "actual_ratio": 0.487,
  "original_tokens": 52,
  "compressed_tokens": 25,
  "tokens_saved": 27,
  "token_savings_percentage": 51.9,
  "processing_time": 0.145,
  "compression_efficiency": 0.423,
  "query": "AI applications in healthcare",
  "timestamp": "2024-01-15T10:30:45.123456",
  "quality_metrics": {
    "semantic_similarity": 0.892,
    "rouge_1": 0.756,
    "rouge_2": 0.634,
    "rouge_l": 0.723,
    "entity_preservation_rate": 0.889,
    "readability_score": 65.2,
    "compression_ratio": 0.487,
    "overall_score": 0.854
  },
  "strategy_metadata": {
    "name": "extractive",
    "description": "Sentence extraction based on importance scoring",
    "version": "1.0.0",
    "computational_complexity": "medium",
    "memory_requirements": "low"
  }
}
```

#### Batch Compression

**Request:**
```bash
curl -X POST "http://localhost:8000/compress/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Machine learning algorithms analyze vast datasets to identify patterns and make predictions.",
      "Deep learning neural networks mimic human brain structure for complex pattern recognition.",
      "Natural language processing enables computers to understand and generate human language."
    ],
    "target_ratio": 0.4,
    "strategy": "extractive",
    "parallel": true,
    "max_workers": 3
  }'
```

**Response Structure:**
```json
{
  "results": [
    {
      "compressed_text": "ML algorithms analyze datasets to identify patterns, make predictions.",
      "original_text": "Machine learning algorithms analyze vast datasets...",
      "strategy_used": "extractive",
      "actual_ratio": 0.423,
      "tokens_saved": 8,
      "processing_time": 0.089
    },
    {
      "compressed_text": "Deep learning networks mimic brain structure for pattern recognition.",
      "original_text": "Deep learning neural networks mimic human...",
      "strategy_used": "extractive",
      "actual_ratio": 0.398,
      "tokens_saved": 9,
      "processing_time": 0.094
    },
    {
      "compressed_text": "NLP enables computers to understand, generate human language.",
      "original_text": "Natural language processing enables computers...",
      "strategy_used": "extractive",
      "actual_ratio": 0.412,
      "tokens_saved": 7,
      "processing_time": 0.087
    }
  ],
  "total_processing_time": 0.298,
  "strategy_used": "extractive",
  "target_ratio": 0.4,
  "parallel_processing": true,
  "success_rate": 1.0,
  "average_compression_ratio": 0.411,
  "total_tokens_saved": 24,
  "average_quality_score": 0.867,
  "failed_items": [],
  "timestamp": "2024-01-15T10:35:22.456789"
}
```

#### List Available Strategies

**Request:**
```bash
curl "http://localhost:8000/strategies"
```

**Response:**
```json
{
  "strategies": [
    {
      "name": "extractive",
      "description": "Extracts important sentences based on TF-IDF and position scoring",
      "version": "1.0.0",
      "author": "Context Compressor Team",
      "supported_languages": ["en"],
      "optimal_compression_ratios": [0.3, 0.5, 0.7],
      "requires_query": false,
      "supports_batch": true,
      "computational_complexity": "medium",
      "memory_requirements": "low",
      "dependencies": ["scikit-learn", "numpy"]
    },
    {
      "name": "abstractive",
      "description": "Uses transformer models for content summarization",
      "version": "1.0.0",
      "supported_languages": ["en"],
      "optimal_compression_ratios": [0.2, 0.4, 0.6],
      "requires_query": false,
      "supports_batch": true,
      "computational_complexity": "high",
      "memory_requirements": "high",
      "dependencies": ["transformers", "torch"]
    }
  ],
  "total_strategies": 2,
  "default_strategy": "extractive"
}
```

#### Health Check

**Request:**
```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.2",
  "timestamp": "2024-01-15T10:40:15.789012",
  "uptime_seconds": 3600.5,
  "total_compressions": 1245,
  "cache_hit_rate": 23.7,
  "average_processing_time": 0.156
}
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📊 Quality Metrics & Evaluation

The system provides comprehensive quality evaluation with detailed metrics and examples:

### 🔍 Core Quality Metrics

#### Semantic Similarity (0.0 - 1.0)
Measures how well the compressed text preserves the original meaning using word embeddings.

```python
from context_compressor import ContextCompressor

compressor = ContextCompressor(enable_quality_evaluation=True)
result = compressor.compress(
    "The revolutionary breakthrough in quantum computing promises to solve complex problems "
    "that are currently intractable for classical computers, potentially transforming "
    "cryptography, drug discovery, and optimization challenges.",
    target_ratio=0.5
)

print(f"Semantic Similarity: {result.quality_metrics.semantic_similarity:.3f}")
# Output: Semantic Similarity: 0.892
# Interpretation: 89.2% of semantic meaning preserved
```

#### ROUGE Scores (0.0 - 1.0)
Standard summarization metrics comparing n-gram overlap between original and compressed text.

```python
metrics = result.quality_metrics
print(f"ROUGE-1 (unigram overlap): {metrics.rouge_1:.3f}")
print(f"ROUGE-2 (bigram overlap): {metrics.rouge_2:.3f}")
print(f"ROUGE-L (longest common subsequence): {metrics.rouge_l:.3f}")

# Example output:
# ROUGE-1 (unigram overlap): 0.756
# ROUGE-2 (bigram overlap): 0.634
# ROUGE-L (longest common subsequence): 0.723
```

**Interpretation:**
- **ROUGE-1 > 0.7**: Excellent word overlap
- **ROUGE-2 > 0.5**: Good phrase preservation
- **ROUGE-L > 0.6**: Strong structural similarity

#### Entity Preservation Rate (0.0 - 1.0)
Tracks retention of named entities, numbers, dates, and other important factual information.

```python
original = "Apple Inc. reported $394.3 billion revenue in 2022, with CEO Tim Cook "
           "announcing new products on September 7th at their Cupertino headquarters."

result = compressor.compress(original, target_ratio=0.6)

print(f"Entity Preservation: {result.quality_metrics.entity_preservation_rate:.3f}")
print(f"Compressed: {result.compressed_text}")

# Output:
# Entity Preservation: 0.889
# Compressed: Apple Inc. reported $394.3 billion revenue in 2022, with CEO Tim Cook 
#            announcing new products at Cupertino headquarters.
# Analysis: 8/9 entities preserved (missing "September 7th")
```

#### Readability Score (0-100, Flesch Reading Ease)
Measures text readability - higher scores indicate easier reading.

```python
print(f"Readability Score: {result.quality_metrics.readability_score:.1f}")

# Interpretation:
# 90-100: Very Easy (5th grade)
# 80-89:  Easy (6th grade)
# 70-79:  Fairly Easy (7th grade)
# 60-69:  Standard (8th-9th grade)
# 50-59:  Fairly Difficult (10th-12th grade)
# 30-49:  Difficult (College level)
# 0-29:   Very Difficult (Graduate level)
```

#### Overall Quality Score (0.0 - 1.0)
Weighted combination of all metrics, providing a single quality indicator.

```python
overall = result.quality_metrics.overall_score
print(f"Overall Quality: {overall:.3f}")

# Quality Thresholds:
if overall >= 0.9:
    quality_level = "Excellent"
elif overall >= 0.8:
    quality_level = "Very Good"
elif overall >= 0.7:
    quality_level = "Good"
elif overall >= 0.6:
    quality_level = "Acceptable"
else:
    quality_level = "Poor"

print(f"Quality Level: {quality_level}")
```

### 📈 Quality Analysis Examples

#### Detailed Quality Report

```python
def generate_quality_report(result):
    """Generate comprehensive quality analysis report."""
    if not result.quality_metrics:
        return "Quality evaluation not enabled"
    
    metrics = result.quality_metrics
    
    report = f"""
📊 COMPRESSION QUALITY REPORT
{'='*50}

📝 Text Statistics:
   Original tokens: {result.original_tokens}
   Compressed tokens: {result.compressed_tokens}
   Compression ratio: {result.actual_ratio:.1%}
   Tokens saved: {result.tokens_saved}

🎯 Quality Metrics:
   Semantic Similarity: {metrics.semantic_similarity:.3f} {'✅' if metrics.semantic_similarity >= 0.8 else '⚠️' if metrics.semantic_similarity >= 0.6 else '❌'}
   ROUGE-1: {metrics.rouge_1:.3f} {'✅' if metrics.rouge_1 >= 0.7 else '⚠️' if metrics.rouge_1 >= 0.5 else '❌'}
   ROUGE-2: {metrics.rouge_2:.3f} {'✅' if metrics.rouge_2 >= 0.5 else '⚠️' if metrics.rouge_2 >= 0.3 else '❌'}
   ROUGE-L: {metrics.rouge_l:.3f} {'✅' if metrics.rouge_l >= 0.6 else '⚠️' if metrics.rouge_l >= 0.4 else '❌'}
   Entity Preservation: {metrics.entity_preservation_rate:.3f} {'✅' if metrics.entity_preservation_rate >= 0.8 else '⚠️' if metrics.entity_preservation_rate >= 0.6 else '❌'}
   Readability: {metrics.readability_score:.1f} {'✅' if 60 <= metrics.readability_score <= 80 else '⚠️'}
   
🏆 Overall Score: {metrics.overall_score:.3f} {'✅ Excellent' if metrics.overall_score >= 0.9 else '✅ Very Good' if metrics.overall_score >= 0.8 else '⚠️ Good' if metrics.overall_score >= 0.7 else '⚠️ Acceptable' if metrics.overall_score >= 0.6 else '❌ Poor'}

⚡ Efficiency Score: {result.compression_efficiency:.3f}
   (Balances compression ratio with quality)
    """
    
    return report

# Usage
result = compressor.compress(long_text, target_ratio=0.4)
print(generate_quality_report(result))
```

#### Quality Comparison Across Strategies

```python
def compare_quality_across_strategies(text, target_ratio=0.5):
    """Compare quality metrics across different compression strategies."""
    strategies = [
        ("Extractive", ExtractiveStrategy()),
        ("Semantic", SemanticStrategy()),
        ("Hybrid", HybridStrategy())
    ]
    
    results = []
    
    for name, strategy in strategies:
        compressor = ContextCompressor(
            strategies=[strategy],
            enable_quality_evaluation=True
        )
        result = compressor.compress(text, target_ratio=target_ratio)
        
        if result.quality_metrics:
            results.append({
                'strategy': name,
                'compression': result.actual_ratio,
                'semantic_sim': result.quality_metrics.semantic_similarity,
                'rouge_1': result.quality_metrics.rouge_1,
                'rouge_l': result.quality_metrics.rouge_l,
                'entity_preservation': result.quality_metrics.entity_preservation_rate,
                'overall': result.quality_metrics.overall_score,
                'efficiency': result.compression_efficiency
            })
    
    # Display comparison table
    print(f"{'Strategy':<12} | {'Comp.':<6} | {'Sem.':<6} | {'R-1':<6} | {'R-L':<6} | {'Ent.':<6} | {'Overall':<7} | {'Effic.':<7}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['strategy']:<12} | "
              f"{r['compression']:<6.1%} | "
              f"{r['semantic_sim']:<6.3f} | "
              f"{r['rouge_1']:<6.3f} | "
              f"{r['rouge_l']:<6.3f} | "
              f"{r['entity_preservation']:<6.3f} | "
              f"{r['overall']:<7.3f} | "
              f"{r['efficiency']:<7.3f}")
    
    return results

# Usage
comparison = compare_quality_across_strategies(sample_text)
```

**Example Output:**
```
Strategy     | Comp.  | Sem.   | R-1    | R-L    | Ent.   | Overall | Effic. 
--------------------------------------------------------------------------------
Extractive   | 48.3%  | 0.854  | 0.756  | 0.723  | 0.889  | 0.854   | 0.412  
Semantic     | 58.2%  | 0.887  | 0.712  | 0.698  | 0.845  | 0.836   | 0.486  
Hybrid       | 44.1%  | 0.891  | 0.789  | 0.756  | 0.923  | 0.891   | 0.393  
```

### 🎯 Quality Optimization Strategies

```python
def optimize_for_quality_metric(text, target_metric='overall', min_score=0.8):
    """Optimize compression for specific quality metrics."""
    strategies_config = {
        'semantic_similarity': [
            SemanticStrategy(similarity_threshold=0.8),
            HybridStrategy(primary_weight=0.3, secondary_weight=0.7)
        ],
        'entity_preservation': [
            ExtractiveStrategy(entity_boost=0.4),
            HybridStrategy(entity_preservation_weight=0.3)
        ],
        'rouge_scores': [
            ExtractiveStrategy(scoring_method="tfidf"),
            AbstractiveStrategy(model_name="facebook/bart-large-cnn")
        ],
        'overall': [
            HybridStrategy(),
            ExtractiveStrategy(scoring_method="combined")
        ]
    }
    
    target_strategies = strategies_config.get(target_metric, strategies_config['overall'])
    
    best_result = None
    best_score = 0
    
    for strategy in target_strategies:
        compressor = ContextCompressor(strategies=[strategy])
        result = compressor.compress(text, target_ratio=0.5)
        
        if result.quality_metrics:
            score = getattr(result.quality_metrics, target_metric, result.quality_metrics.overall_score)
            
            if score > best_score and score >= min_score:
                best_score = score
                best_result = result
    
    return best_result

# Usage examples
best_semantic = optimize_for_quality_metric(text, 'semantic_similarity', 0.85)
best_entity = optimize_for_quality_metric(text, 'entity_preservation_rate', 0.9)
best_overall = optimize_for_quality_metric(text, 'overall', 0.8)
```

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

## 🚀 Advanced Techniques & Best Practices

### 🎨 Advanced Strategy Configuration

#### Dynamic Strategy Selection

```python
from context_compressor import ContextCompressor
from context_compressor.strategies import ExtractiveStrategy, AbstractiveStrategy

def select_strategy_by_content(text: str, target_ratio: float):
    """Dynamically select strategy based on content characteristics."""
    text_length = len(text.split())
    
    if text_length < 100:
        # Short text: use extractive for speed
        return ExtractiveStrategy(scoring_method="tfidf")
    elif target_ratio < 0.3:
        # Aggressive compression: use abstractive
        return AbstractiveStrategy(model_name="facebook/bart-large-cnn")
    else:
        # Balanced: use hybrid approach
        return ExtractiveStrategy(scoring_method="combined")

# Usage
text = "Your content here..."
strategy = select_strategy_by_content(text, target_ratio=0.4)
compressor = ContextCompressor(strategies=[strategy])
result = compressor.compress(text, target_ratio=0.4)
```

#### Custom Scoring Functions

```python
from context_compressor.strategies import ExtractiveStrategy
import numpy as np

def custom_importance_scorer(sentences, query=None):
    """Custom sentence importance scoring."""
    scores = []
    for sentence in sentences:
        score = 0.0
        
        # Length-based scoring
        if 10 <= len(sentence.split()) <= 25:
            score += 0.3
        
        # Question sentences get higher scores
        if sentence.strip().endswith('?'):
            score += 0.4
        
        # Keyword boosting
        keywords = ['important', 'key', 'main', 'primary', 'essential']
        for keyword in keywords:
            if keyword.lower() in sentence.lower():
                score += 0.2
        
        # Query relevance (if provided)
        if query:
            query_words = set(query.lower().split())
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words.intersection(sentence_words))
            score += overlap * 0.1
        
        scores.append(score)
    
    return np.array(scores)

# Create custom strategy
strategy = ExtractiveStrategy(
    scoring_method="custom",
    custom_scorer=custom_importance_scorer
)
```

### 📊 Advanced Quality Control

#### Quality-Aware Compression

```python
def compress_with_quality_threshold(compressor, text, target_ratio, min_quality=0.8):
    """Compress text while maintaining minimum quality threshold."""
    result = compressor.compress(text, target_ratio=target_ratio)
    
    if result.quality_metrics and result.quality_metrics.overall_score < min_quality:
        # Try with less aggressive compression
        adjusted_ratio = min(target_ratio + 0.2, 0.9)
        print(f"Quality too low ({result.quality_metrics.overall_score:.3f}), "
              f"adjusting ratio from {target_ratio} to {adjusted_ratio}")
        result = compressor.compress(text, target_ratio=adjusted_ratio)
    
    return result

# Usage
compressor = ContextCompressor(enable_quality_evaluation=True)
result = compress_with_quality_threshold(
    compressor, text, target_ratio=0.3, min_quality=0.85
)
print(f"Final quality: {result.quality_metrics.overall_score:.3f}")
```

#### Multi-Metric Quality Optimization

```python
def multi_objective_compression(compressor, text, target_ratio):
    """Optimize for multiple quality metrics simultaneously."""
    strategies = [
        ("extractive", ExtractiveStrategy()),
        ("semantic", SemanticStrategy()),
        ("hybrid", HybridStrategy())
    ]
    
    best_result = None
    best_score = -1
    
    for name, strategy in strategies:
        temp_compressor = ContextCompressor(strategies=[strategy])
        result = temp_compressor.compress(text, target_ratio=target_ratio)
        
        if result.quality_metrics:
            # Weighted quality score
            composite_score = (
                result.quality_metrics.semantic_similarity * 0.3 +
                result.quality_metrics.rouge_l * 0.3 +
                result.quality_metrics.entity_preservation_rate * 0.2 +
                (1 - result.actual_ratio) * 0.2  # Compression bonus
            )
            
            print(f"{name:<12}: Quality={composite_score:.3f}, "
                  f"Compression={result.actual_ratio:.1%}")
            
            if composite_score > best_score:
                best_score = composite_score
                best_result = result
    
    return best_result
```

### 🔄 Pipeline Integration Patterns

#### RAG System Integration

```python
from context_compressor.integrations.langchain import ContextCompressorTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def create_compressed_rag_pipeline():
    """Create a RAG pipeline with context compression."""
    # Initialize components
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(documents, embeddings)
    compressor = ContextCompressor(
        default_strategy="hybrid",
        enable_quality_evaluation=True
    )
    
    # Create compression transformer
    transformer = ContextCompressorTransformer(
        compressor=compressor,
        target_ratio=0.6,
        min_quality_threshold=0.8
    )
    
    def query_with_compression(query: str, k: int = 5):
        # Retrieve relevant documents
        docs = vectorstore.similarity_search(query, k=k)
        
        # Compress retrieved context
        compressed_docs = transformer.transform_documents(docs)
        
        # Calculate compression statistics
        original_length = sum(len(doc.page_content) for doc in docs)
        compressed_length = sum(len(doc.page_content) for doc in compressed_docs)
        compression_ratio = compressed_length / original_length
        
        print(f"Retrieved {len(docs)} documents")
        print(f"Compression: {compression_ratio:.1%} of original")
        print(f"Context length: {original_length} → {compressed_length} chars")
        
        return compressed_docs
    
    return query_with_compression

# Usage
rag_query = create_compressed_rag_pipeline()
compressed_context = rag_query("What are the benefits of renewable energy?")
```

#### API Cost Optimization

```python
from context_compressor.integrations.openai import compress_for_openai
import openai

def cost_optimized_api_call(prompt: str, context: str, model: str = "gpt-4"):
    """Optimize API costs through intelligent compression."""
    # Estimate original cost
    original_tokens = len(context.split()) * 1.3  # Rough token estimate
    
    # Determine optimal compression ratio based on model pricing
    if model.startswith("gpt-4"):
        target_ratio = 0.4  # Aggressive compression for expensive models
    elif model.startswith("gpt-3.5"):
        target_ratio = 0.6  # Moderate compression
    else:
        target_ratio = 0.8  # Light compression for cheaper models
    
    # Compress context
    compressed_context = compress_for_openai(
        text=context,
        target_ratio=target_ratio,
        model=model,
        preserve_entities=True
    )
    
    # Calculate savings
    compressed_tokens = len(compressed_context.split()) * 1.3
    token_savings = original_tokens - compressed_tokens
    
    # Make API call
    full_prompt = f"{prompt}\n\nContext: {compressed_context}"
    
    print(f"Token reduction: {original_tokens:.0f} → {compressed_tokens:.0f} "
          f"({token_savings/original_tokens:.1%} savings)")
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}]
    )
    
    return response, token_savings
```

## 📈 Performance Optimization

### 📊 Performance Tips & Best Practices

#### Optimal Worker Configuration

```python
import multiprocessing as mp

def get_optimal_workers(text_count: int, avg_text_length: int) -> int:
    """Calculate optimal number of workers based on workload."""
    cpu_count = mp.cpu_count()
    
    # For small texts, use more workers
    if avg_text_length < 100:
        return min(cpu_count, text_count)
    # For large texts, use fewer workers to avoid memory issues
    elif avg_text_length > 1000:
        return max(1, cpu_count // 2)
    else:
        return max(1, int(cpu_count * 0.75))

# Dynamic batch processing
def smart_batch_processing(texts: list, target_ratio: float = 0.5):
    """Intelligently process batches based on content characteristics."""
    avg_length = sum(len(text.split()) for text in texts) / len(texts)
    optimal_workers = get_optimal_workers(len(texts), avg_length)
    
    print(f"Processing {len(texts)} texts with {optimal_workers} workers")
    print(f"Average text length: {avg_length:.0f} words")
    
    compressor = ContextCompressor()
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=target_ratio,
        parallel=True,
        max_workers=optimal_workers
    )
    
    return batch_result
```

### 🛠️ Smart Caching Strategies

```python
from context_compressor.utils.cache import CacheManager
import hashlib

def create_intelligent_cache_manager():
    """Create cache manager with intelligent eviction policies."""
    
    def content_based_key(text: str, target_ratio: float, strategy: str) -> str:
        """Generate cache key based on content characteristics."""
        # Hash content but consider similar texts
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        length_bucket = len(text) // 1000  # Group by content length
        ratio_bucket = int(target_ratio * 10)  # Group by compression ratio
        
        return f"{strategy}_{length_bucket}k_{ratio_bucket}_{content_hash}"
    
    cache_manager = CacheManager(
        ttl=7200,  # 2 hours
        max_size=1000,
        cleanup_interval=300,  # 5 minutes
        key_generator=content_based_key
    )
    
    return cache_manager

# Usage
cache = create_intelligent_cache_manager()
compressor = ContextCompressor(cache_manager=cache)
```

### 🚀 Optimized Batch Processing

```python
def optimized_batch_processing(texts: list, target_ratio: float = 0.5):
    """Optimize batch processing with intelligent partitioning."""
    import multiprocessing as mp
    
    # Partition texts by characteristics
    short_texts = [t for t in texts if len(t.split()) < 100]
    medium_texts = [t for t in texts if 100 <= len(t.split()) < 500]
    long_texts = [t for t in texts if len(t.split()) >= 500]
    
    results = []
    
    # Process short texts with extractive (fast)
    if short_texts:
        extractive_compressor = ContextCompressor(
            strategies=[ExtractiveStrategy()],
            enable_caching=True
        )
        short_results = extractive_compressor.compress_batch(
            short_texts, target_ratio=target_ratio,
            parallel=True, max_workers=mp.cpu_count()
        )
        results.extend(short_results.results)
    
    # Process medium texts with hybrid
    if medium_texts:
        hybrid_compressor = ContextCompressor(
            strategies=[HybridStrategy()]
        )
        medium_results = hybrid_compressor.compress_batch(
            medium_texts, target_ratio=target_ratio,
            parallel=True, max_workers=mp.cpu_count() // 2
        )
        results.extend(medium_results.results)
    
    # Process long texts with semantic (memory efficient)
    if long_texts:
        semantic_compressor = ContextCompressor(
            strategies=[SemanticStrategy()],
            enable_caching=False  # Save memory for large texts
        )
        for text in long_texts:
            result = semantic_compressor.compress(text, target_ratio=target_ratio)
            results.append(result)
    
    return results

# Usage
large_text_batch = ["text1...", "text2...", "text3..."]
results = optimized_batch_processing(large_text_batch, target_ratio=0.4)
print(f"Processed {len(results)} texts efficiently")
```

### 📊 Memory Management & Monitoring

```python
import psutil
import gc
from typing import List, Optional

def memory_aware_compression(compressor, texts: List[str], target_ratio=0.5):
    """Compress with memory monitoring and management."""
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    results = []
    for i, text in enumerate(texts):
        # Compress text
        result = compressor.compress(text, target_ratio=target_ratio)
        results.append(result)
        
        # Monitor memory every 10 items
        if i % 10 == 0:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"Processed {i+1}/{len(texts)} texts, Memory: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
            
            # Trigger cleanup if memory usage is high
            if memory_increase > 500:  # 500MB threshold
                print("High memory usage detected, performing cleanup...")
                gc.collect()  # Force garbage collection
                
                # Clear cache if available
                if hasattr(compressor, '_cache_manager') and compressor._cache_manager:
                    compressor._cache_manager.clear_expired()
    
    final_memory = psutil.Process().memory_info().rss / 1024 / 1024
    print(f"Final memory: {final_memory:.1f}MB (peak increase: {final_memory - initial_memory:.1f}MB)")
    
    return results

# For memory-constrained environments
def create_lightweight_compressor():
    """Create memory-optimized compressor configuration."""
    return ContextCompressor(
        strategies=[ExtractiveStrategy()],  # Lightweight strategy
        enable_caching=False,  # Disable caching
        enable_quality_evaluation=False,  # Skip quality evaluation
        max_concurrent_processes=2  # Limit parallel processing
    )

# Usage
lightweight_compressor = create_lightweight_compressor()
results = memory_aware_compression(lightweight_compressor, large_text_list)
```

### ⚡ Performance Monitoring & Benchmarking

```python
import time
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PerformanceMetrics:
    avg_processing_time: float
    tokens_per_second: float
    memory_efficiency: float
    quality_score: float
    cache_hit_rate: float

def benchmark_strategies(texts: List[str], target_ratio: float = 0.5) -> Dict[str, PerformanceMetrics]:
    """Comprehensive benchmarking of different strategies."""
    strategies = {
        "extractive": ExtractiveStrategy(),
        "semantic": SemanticStrategy(),
        "hybrid": HybridStrategy()
    }
    
    results = {}
    
    for name, strategy in strategies.items():
        print(f"\n📊 Benchmarking {name.title()} Strategy...")
        
        # Reset system state
        gc.collect()
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        # Create compressor with monitoring
        compressor = ContextCompressor(
            strategies=[strategy],
            enable_quality_evaluation=True,
            enable_caching=True
        )
        
        compression_results = []
        cache_hits = 0
        
        # Process texts
        for i, text in enumerate(texts):
            # Check cache before compression
            cache_key = f"{hash(text)}_{target_ratio}_{name}"
            
            result = compressor.compress(text, target_ratio=target_ratio)
            compression_results.append(result)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Processed {i+1}/{len(texts)} texts...")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        # Calculate comprehensive metrics
        total_time = end_time - start_time
        total_tokens = sum(r.original_tokens for r in compression_results)
        avg_quality = sum(
            r.quality_metrics.overall_score 
            for r in compression_results 
            if r.quality_metrics
        ) / len(compression_results)
        
        # Get cache statistics
        cache_stats = getattr(compressor, '_cache_stats', {'hits': 0, 'misses': len(texts)})
        cache_hit_rate = cache_stats.get('hits', 0) / max(1, cache_stats.get('hits', 0) + cache_stats.get('misses', 0))
        
        metrics = PerformanceMetrics(
            avg_processing_time=total_time / len(texts),
            tokens_per_second=total_tokens / max(0.001, total_time),
            memory_efficiency=(end_memory - start_memory) / len(texts) / 1024 / 1024,  # MB per text
            quality_score=avg_quality,
            cache_hit_rate=cache_hit_rate * 100
        )
        
        results[name] = metrics
        
        # Display results
        print(f"  ✅ Results:")
        print(f"    Avg time per text: {metrics.avg_processing_time:.3f}s")
        print(f"    Processing speed: {metrics.tokens_per_second:.1f} tokens/sec")
        print(f"    Memory per text: {metrics.memory_efficiency:.2f}MB")
        print(f"    Avg quality score: {metrics.quality_score:.3f}")
        print(f"    Cache hit rate: {metrics.cache_hit_rate:.1f}%")
    
    # Summary comparison
    print(f"\n🏆 Performance Summary:")
    print(f"{'Strategy':<12} | {'Time/Text':<10} | {'Tokens/Sec':<11} | {'Memory/Text':<12} | {'Quality':<8} | {'Cache':<7}")
    print("-" * 85)
    
    for name, metrics in results.items():
        print(f"{name.title():<12} | "
              f"{metrics.avg_processing_time:<10.3f} | "
              f"{metrics.tokens_per_second:<11.1f} | "
              f"{metrics.memory_efficiency:<12.2f} | "
              f"{metrics.quality_score:<8.3f} | "
              f"{metrics.cache_hit_rate:<7.1f}%")
    
    return results

# Usage
sample_texts = ["Sample text 1...", "Sample text 2...", "Sample text 3..."]
benchmark_results = benchmark_strategies(sample_texts, target_ratio=0.5)
```

### 🔧 Troubleshooting & Error Handling

#### Robust Compression with Fallbacks

```python
from typing import Optional
import logging
import time

def robust_compression(text: str, target_ratio: float = 0.5) -> Optional[CompressionResult]:
    """Compression with comprehensive error handling and fallback strategies."""
    strategies = [
        ("extractive", ExtractiveStrategy()),  # Most reliable
        ("semantic", SemanticStrategy()),     # Fallback 1
        ("simple", ExtractiveStrategy(scoring_method="frequency"))  # Fallback 2
    ]
    
    for i, (name, strategy) in enumerate(strategies):
        try:
            compressor = ContextCompressor(
                strategies=[strategy],
                enable_quality_evaluation=True,
                timeout=30  # 30 second timeout
            )
            
            # Attempt compression
            result = compressor.compress(text, target_ratio=target_ratio)
            
            # Validate result
            if result.compressed_text and len(result.compressed_text.strip()) > 0:
                logging.info(f"Compression successful with {name} strategy")
                return result
            else:
                raise ValueError("Empty compression result")
            
        except Exception as e:
            logging.warning(f"{name.title()} strategy failed: {str(e)}")
            if i == len(strategies) - 1:  # Last strategy failed
                logging.error(f"All compression strategies failed for text: {text[:100]}...")
                return None
            continue
    
    return None

def compress_with_retry(text: str, max_retries: int = 3, backoff_factor: float = 2.0) -> Optional[CompressionResult]:
    """Compress with exponential backoff retry mechanism."""
    for attempt in range(max_retries):
        try:
            result = robust_compression(text)
            if result:
                return result
        except Exception as e:
            logging.warning(f"Compression attempt {attempt + 1} failed: {str(e)}")
        
        if attempt < max_retries - 1:  # Don't sleep on last attempt
            sleep_time = backoff_factor ** attempt
            logging.info(f"Retrying in {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
    
    logging.error(f"Failed to compress text after {max_retries} attempts")
    return None

# Usage
result = compress_with_retry(problematic_text, max_retries=3)
if result:
    print(f"Successfully compressed: {result.actual_ratio:.1%} compression")
else:
    print("Compression failed after all retry attempts")
```

#### Common Issues & Solutions

```python
def diagnose_compression_issues(text: str, target_ratio: float = 0.5):
    """Diagnose and provide solutions for compression issues."""
    print(f"🔍 Diagnosing compression issues...\n")
    
    # Text characteristics
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    print(f"Text Statistics:")
    print(f"  Words: {word_count}")
    print(f"  Characters: {char_count}")
    print(f"  Sentences: {sentence_count}")
    print(f"  Avg words/sentence: {word_count/max(1, sentence_count):.1f}")
    
    # Issue detection
    issues = []
    solutions = []
    
    if word_count < 50:
        issues.append("⚠️ Text too short")
        solutions.append("Use lighter compression (target_ratio > 0.7) or skip compression")
    
    if sentence_count < 3:
        issues.append("⚠️ Too few sentences")
        solutions.append("Use extractive strategy with word-level compression")
    
    if word_count / sentence_count > 50:
        issues.append("⚠️ Very long sentences")
        solutions.append("Use semantic strategy for better sentence splitting")
    
    if target_ratio < 0.2:
        issues.append("⚠️ Aggressive compression ratio")
        solutions.append("Consider target_ratio >= 0.3 for better quality")
    
    # Memory check
    try:
        import psutil
        available_memory = psutil.virtual_memory().available / 1024 / 1024 / 1024  # GB
        if available_memory < 2.0:
            issues.append("⚠️ Low available memory")
            solutions.append("Use lightweight compressor or disable caching")
    except ImportError:
        pass
    
    # Report findings
    if issues:
        print(f"\n🚫 Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        
        print(f"\n💡 Recommended Solutions:")
        for solution in solutions:
            print(f"  {solution}")
    else:
        print(f"\n✅ No issues detected - text should compress well")
    
    # Provide optimal configuration
    print(f"\n🎯 Recommended Configuration:")
    
    if word_count < 100:
        strategy = "ExtractiveStrategy()"
        ratio = min(0.8, target_ratio + 0.2)
    elif word_count > 1000:
        strategy = "SemanticStrategy()"
        ratio = target_ratio
    else:
        strategy = "HybridStrategy()"
        ratio = target_ratio
    
    print(f"  Strategy: {strategy}")
    print(f"  Target Ratio: {ratio:.1f}")
    print(f"  Enable Caching: {available_memory > 2.0 if 'available_memory' in locals() else True}")
    print(f"  Quality Evaluation: {word_count > 50}")

# Usage
diagnose_compression_issues(problematic_text, target_ratio=0.3)
```

### 📊 Production Monitoring

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class ProductionMetrics:
    """Track production compression metrics."""
    total_requests: int = 0
    successful_compressions: int = 0
    failed_compressions: int = 0
    avg_processing_time: float = 0.0
    avg_compression_ratio: float = 0.0
    avg_quality_score: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: datetime = None

class ProductionMonitor:
    """Monitor compression performance in production."""
    
    def __init__(self):
        self.metrics = ProductionMetrics()
        self.request_history: List[Dict] = []
    
    def log_compression(self, result: CompressionResult, success: bool = True):
        """Log compression result for monitoring."""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_compressions += 1
            
            # Update running averages
            n = self.metrics.successful_compressions
            self.metrics.avg_processing_time = (
                (self.metrics.avg_processing_time * (n-1) + result.processing_time) / n
            )
            self.metrics.avg_compression_ratio = (
                (self.metrics.avg_compression_ratio * (n-1) + result.actual_ratio) / n
            )
            
            if result.quality_metrics:
                self.metrics.avg_quality_score = (
                    (self.metrics.avg_quality_score * (n-1) + result.quality_metrics.overall_score) / n
                )
        else:
            self.metrics.failed_compressions += 1
        
        self.metrics.last_updated = datetime.now()
        
        # Keep recent history
        self.request_history.append({
            'timestamp': datetime.now(),
            'success': success,
            'processing_time': result.processing_time if success else None,
            'compression_ratio': result.actual_ratio if success else None,
            'tokens_saved': result.tokens_saved if success else None
        })
        
        # Keep only last 1000 requests
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def get_health_status(self) -> Dict:
        """Get current system health status."""
        success_rate = (
            self.metrics.successful_compressions / max(1, self.metrics.total_requests) * 100
        )
        
        health_status = "healthy"
        if success_rate < 95:
            health_status = "degraded"
        if success_rate < 80:
            health_status = "unhealthy"
        
        return {
            'status': health_status,
            'success_rate': success_rate,
            'total_requests': self.metrics.total_requests,
            'avg_processing_time': self.metrics.avg_processing_time,
            'avg_compression_ratio': self.metrics.avg_compression_ratio,
            'avg_quality_score': self.metrics.avg_quality_score,
            'last_updated': self.metrics.last_updated.isoformat() if self.metrics.last_updated else None
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive monitoring report."""
        health = self.get_health_status()
        
        report = f"""
📊 PRODUCTION MONITORING REPORT
{'='*50}

🟢 System Health: {health['status'].upper()}
📊 Success Rate: {health['success_rate']:.1f}%
📝 Total Requests: {health['total_requests']}
⏱️ Avg Processing Time: {health['avg_processing_time']:.3f}s
📊 Avg Compression: {health['avg_compression_ratio']:.1%}
🎯 Avg Quality: {health['avg_quality_score']:.3f}
🔄 Last Updated: {health['last_updated'] or 'Never'}

📈 Recent Performance Trends:
        """
        
        # Analyze recent trends
        if len(self.request_history) >= 10:
            recent_requests = self.request_history[-10:]
            recent_success_rate = sum(1 for r in recent_requests if r['success']) / len(recent_requests) * 100
            recent_avg_time = sum(r['processing_time'] for r in recent_requests if r['success']) / max(1, sum(1 for r in recent_requests if r['success']))
            
            report += f"  Recent Success Rate (last 10): {recent_success_rate:.1f}%\n"
            report += f"  Recent Avg Time (last 10): {recent_avg_time:.3f}s\n"
        
        return report

# Usage in production
monitor = ProductionMonitor()

# In your compression endpoint
def compress_with_monitoring(text: str, target_ratio: float = 0.5):
    try:
        compressor = ContextCompressor()
        result = compressor.compress(text, target_ratio=target_ratio)
        monitor.log_compression(result, success=True)
        return result
    except Exception as e:
        # Create dummy result for failed compression
        failed_result = CompressionResult(
            original_text=text,
            compressed_text="",
            strategy_used="failed",
            target_ratio=target_ratio,
            actual_ratio=0.0,
            original_tokens=0,
            compressed_tokens=0,
            processing_time=0.0
        )
        monitor.log_compression(failed_result, success=False)
        raise e

# Health check endpoint
def health_check():
    return monitor.get_health_status()

# Monitoring dashboard
print(monitor.generate_report())
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