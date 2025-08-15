#!/usr/bin/env python3
"""
Framework Integration Examples for AI Context Compressor.

This script demonstrates integration with popular AI frameworks and services
including LangChain, OpenAI API, and other common use cases.
"""

import sys
import os
from typing import List, Dict, Any

# Add the src directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_compressor import ContextCompressor


def simulate_langchain_documents():
    """Create mock LangChain documents for testing."""
    
    class MockDocument:
        """Mock LangChain Document class."""
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}
    
    return [
        MockDocument(
            page_content="""
            Machine learning is a subset of artificial intelligence that enables computers 
            to learn and make decisions from data without being explicitly programmed. 
            It involves the development of algorithms that can identify patterns in large 
            datasets and use these patterns to make predictions or classifications on new, 
            unseen data. Popular machine learning techniques include supervised learning, 
            unsupervised learning, and reinforcement learning.
            """,
            metadata={"source": "ml_guide.pdf", "page": 1}
        ),
        MockDocument(
            page_content="""
            Deep learning is a specialized subset of machine learning that uses neural 
            networks with multiple layers to process complex data. These deep neural 
            networks can automatically learn hierarchical representations of data, 
            making them particularly effective for tasks such as image recognition, 
            natural language processing, and speech recognition. The success of deep 
            learning has revolutionized many fields of artificial intelligence.
            """,
            metadata={"source": "deep_learning.pdf", "page": 1}
        ),
        MockDocument(
            page_content="""
            Natural language processing (NLP) is a branch of artificial intelligence 
            that focuses on the interaction between computers and human language. 
            NLP techniques enable machines to understand, interpret, and generate 
            human language in a meaningful way. Applications of NLP include machine 
            translation, sentiment analysis, chatbots, and text summarization. 
            Modern NLP systems often use deep learning approaches for better performance.
            """,
            metadata={"source": "nlp_overview.pdf", "page": 1}
        )
    ]


def main():
    """Run framework integration examples."""
    
    print("🔗 AI Context Compressor - Framework Integration Examples")
    print("=" * 60)
    
    # Initialize compressor
    compressor = ContextCompressor()
    
    # Sample texts for various examples
    sample_texts = {
        "technical_doc": """
        Artificial Intelligence (AI) systems are becoming increasingly sophisticated and 
        are being deployed across various industries. Machine learning algorithms can 
        process vast amounts of data to identify patterns and make predictions. Deep 
        learning networks use multiple layers of neurons to solve complex problems such 
        as image recognition and natural language understanding. The applications of AI 
        span healthcare, finance, transportation, and many other sectors. Companies are 
        investing heavily in AI research and development to gain competitive advantages. 
        However, ethical considerations around AI deployment remain important challenges 
        that need to be addressed through proper governance and regulation.
        """,
        
        "chat_conversation": [
            {"role": "system", "content": "You are a helpful AI assistant that provides concise and accurate information about technology topics."},
            {"role": "user", "content": "Can you explain what machine learning is and how it's different from traditional programming? I'm new to this field and want to understand the basics."},
            {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence where computers learn to make predictions or decisions by finding patterns in data, rather than following pre-programmed instructions. In traditional programming, developers write explicit rules and logic to solve problems. In machine learning, you provide the computer with examples (data) and the desired outcomes, and the algorithm figures out the patterns automatically. For example, instead of programming all the rules to recognize a cat in photos, you show the system thousands of cat photos labeled as 'cat' and let it learn the visual patterns that define cats."}
        ],
        
        "batch_content": [
            "Quantum computing represents a revolutionary approach to computation that leverages quantum mechanical phenomena.",
            "Blockchain technology provides a decentralized and secure method for recording transactions and data.",
            "Cloud computing enables on-demand access to computing resources over the internet without direct active management."
        ]
    }
    
    # 1. LangChain Integration Example (simulated)
    print("\n1. LangChain Integration Example (Simulated)")
    print("-" * 45)
    
    try:
        from context_compressor.integrations.langchain import (
            compress_documents, 
            compress_document_content,
            LANGCHAIN_AVAILABLE
        )
        
        if LANGCHAIN_AVAILABLE:
            print("✅ LangChain integration available")
        else:
            print("⚠️  LangChain not installed - showing simulated example")
        
        # Create mock documents
        documents = simulate_langchain_documents()
        
        print(f"📄 Processing {len(documents)} documents...")
        
        # Simulate document compression
        for i, doc in enumerate(documents):
            result = compressor.compress(
                text=doc.page_content,
                target_ratio=0.6,
                strategy="extractive"
            )
            
            print(f"\nDocument {i+1}:")
            print(f"   Source: {doc.metadata.get('source', 'unknown')}")
            print(f"   Original: {result.original_tokens} tokens")
            print(f"   Compressed: {result.compressed_tokens} tokens ({result.actual_ratio:.1%})")
            print(f"   Content: '{result.compressed_text[:100]}...'")
        
    except ImportError as e:
        print(f"❌ LangChain integration not available: {e}")
    
    # 2. OpenAI API Integration Example
    print("\n2. OpenAI API Integration Example")
    print("-" * 35)
    
    try:
        from context_compressor.integrations.openai import (
            compress_for_openai,
            compress_for_chat_completion,
            estimate_openai_cost_savings,
            TIKTOKEN_AVAILABLE,
            OPENAI_AVAILABLE
        )
        
        print(f"📊 Tiktoken available: {TIKTOKEN_AVAILABLE}")
        print(f"🔧 OpenAI SDK available: {OPENAI_AVAILABLE}")
        
        # Compress text for OpenAI API
        text = sample_texts["technical_doc"]
        
        # Test different OpenAI models
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        print(f"\n🤖 Testing compression for different OpenAI models:")
        
        for model in models:
            try:
                result = compress_for_openai(
                    text=text,
                    target_ratio=0.5,
                    model=model,
                    estimate_cost_savings=True
                )
                
                print(f"\n   {model}:")
                print(f"     Original tokens: {result['original_tokens']}")
                print(f"     Compressed tokens: {result['compressed_tokens']}")
                print(f"     Tokens saved: {result['tokens_saved']}")
                
                if 'cost_estimation' in result:
                    cost_info = result['cost_estimation']
                    print(f"     Cost savings: ${cost_info['cost_savings_usd']:.6f} ({cost_info['savings_percentage']:.1f}%)")
                
            except Exception as e:
                print(f"     ❌ Error with {model}: {e}")
        
    except ImportError as e:
        print(f"❌ OpenAI integration not available: {e}")
    
    # 3. Chat Completion Integration
    print("\n3. Chat Completion Integration")
    print("-" * 31)
    
    try:
        from context_compressor.integrations.openai import compress_for_chat_completion
        
        messages = sample_texts["chat_conversation"]
        
        print("💬 Original chat messages:")
        for msg in messages:
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"   {role}: {content}")
        
        # Compress user messages only
        compressed_messages = compress_for_chat_completion(
            messages=messages,
            target_ratio=0.6,
            compress_user=True,
            compress_assistant=True,
            compress_system=False
        )
        
        print(f"\n💬 Compressed chat messages:")
        for i, (original, compressed) in enumerate(zip(messages, compressed_messages)):
            if original["content"] != compressed["content"]:
                print(f"   Message {i+1} ({compressed['role']}) compressed:")
                print(f"     Before: {len(original['content'])} chars")
                print(f"     After:  {len(compressed['content'])} chars")
                print(f"     Content: '{compressed['content'][:100]}...'")
        
    except ImportError:
        print("❌ Chat completion integration not available")
    
    # 4. Batch Processing for APIs
    print("\n4. Batch Processing for API Usage")
    print("-" * 33)
    
    try:
        from context_compressor.integrations.openai import batch_compress_for_openai
        
        texts = sample_texts["batch_content"]
        
        result = batch_compress_for_openai(
            texts=texts,
            target_ratio=0.5,
            model="gpt-3.5-turbo",
            parallel=True,
            estimate_total_savings=True
        )
        
        print(f"📦 Batch processing results:")
        print(f"   Texts processed: {result['summary']['texts_processed']}")
        print(f"   Total original tokens: {result['summary']['total_original_tokens']}")
        print(f"   Total compressed tokens: {result['summary']['total_compressed_tokens']}")
        print(f"   Total tokens saved: {result['summary']['total_tokens_saved']}")
        
        if 'cost_estimation' in result['summary']:
            cost_info = result['summary']['cost_estimation']
            print(f"   Estimated cost savings: ${cost_info['cost_savings_usd']:.6f}")
        
        print(f"\n   Individual results:")
        for i, item_result in enumerate(result['results']):
            print(f"     Text {i+1}: {item_result['tokens_saved']} tokens saved "
                  f"({item_result['compression_ratio']:.1%} ratio)")
    
    except ImportError:
        print("❌ Batch processing integration not available")
    
    # 5. Custom Integration Example
    print("\n5. Custom Integration Example")
    print("-" * 29)
    
    class CustomAIService:
        """Example custom AI service integration."""
        
        def __init__(self, compressor: ContextCompressor):
            self.compressor = compressor
            self.max_tokens = 4096  # Simulated API limit
        
        def process_with_compression(self, text: str, query: str = None) -> Dict[str, Any]:
            """Process text with automatic compression if needed."""
            original_token_count = len(text.split())  # Simplified counting
            
            if original_token_count > self.max_tokens:
                # Calculate required compression ratio
                target_ratio = min(0.8, self.max_tokens / original_token_count)
                
                print(f"   🔧 Text too long ({original_token_count} tokens), compressing to {target_ratio:.1%}")
                
                result = self.compressor.compress(
                    text=text,
                    target_ratio=target_ratio,
                    query=query
                )
                
                processed_text = result.compressed_text
                final_token_count = result.compressed_tokens
            else:
                processed_text = text
                final_token_count = original_token_count
                result = None
            
            return {
                'processed_text': processed_text,
                'original_tokens': original_token_count,
                'final_tokens': final_token_count,
                'was_compressed': result is not None,
                'compression_result': result
            }
    
    # Test custom integration
    custom_service = CustomAIService(compressor)
    
    # Test with long text (will be compressed)
    long_text = sample_texts["technical_doc"] * 3  # Make it longer
    
    result = custom_service.process_with_compression(
        text=long_text,
        query="artificial intelligence applications"
    )
    
    print(f"🧪 Custom service processing:")
    print(f"   Original tokens: {result['original_tokens']}")
    print(f"   Final tokens: {result['final_tokens']}")
    print(f"   Was compressed: {result['was_compressed']}")
    
    if result['was_compressed']:
        comp_result = result['compression_result']
        print(f"   Compression ratio: {comp_result.actual_ratio:.1%}")
        print(f"   Processing time: {comp_result.processing_time:.3f}s")
    
    # 6. RAG System Integration Example
    print("\n6. RAG System Integration Example")
    print("-" * 33)
    
    class SimpleRAGSystem:
        """Example RAG system with compression."""
        
        def __init__(self, compressor: ContextCompressor):
            self.compressor = compressor
            self.document_store = []
        
        def add_document(self, content: str, metadata: Dict[str, Any] = None):
            """Add document to the store with optional compression."""
            self.document_store.append({
                'content': content,
                'metadata': metadata or {}
            })
        
        def retrieve_and_compress(
            self, 
            query: str, 
            max_context_tokens: int = 1000,
            compression_ratio: float = 0.5
        ) -> Dict[str, Any]:
            """Retrieve relevant documents and compress for context."""
            
            # Simulate retrieval (in real system, you'd use embeddings/search)
            relevant_docs = self.document_store[:2]  # Take first 2 docs
            
            # Combine documents
            combined_context = "\n\n".join([doc['content'] for doc in relevant_docs])
            
            # Check if compression is needed
            estimated_tokens = len(combined_context.split())
            
            if estimated_tokens > max_context_tokens:
                # Compress with query awareness
                result = self.compressor.compress(
                    text=combined_context,
                    target_ratio=compression_ratio,
                    query=query,
                    strategy="extractive"
                )
                
                final_context = result.compressed_text
                final_tokens = result.compressed_tokens
                was_compressed = True
            else:
                final_context = combined_context
                final_tokens = estimated_tokens
                was_compressed = False
            
            return {
                'context': final_context,
                'token_count': final_tokens,
                'was_compressed': was_compressed,
                'source_documents': len(relevant_docs),
                'query': query
            }
    
    # Test RAG system
    rag_system = SimpleRAGSystem(compressor)
    
    # Add sample documents
    documents = simulate_langchain_documents()
    for doc in documents:
        rag_system.add_document(doc.page_content, doc.metadata)
    
    # Test retrieval with compression
    query = "machine learning applications"
    rag_result = rag_system.retrieve_and_compress(
        query=query,
        max_context_tokens=200,  # Force compression
        compression_ratio=0.4
    )
    
    print(f"🔍 RAG system results:")
    print(f"   Query: '{rag_result['query']}'")
    print(f"   Source documents: {rag_result['source_documents']}")
    print(f"   Final token count: {rag_result['token_count']}")
    print(f"   Was compressed: {rag_result['was_compressed']}")
    print(f"   Context preview: '{rag_result['context'][:150]}...'")
    
    # 7. Performance Monitoring Integration
    print("\n7. Performance Monitoring Integration")
    print("-" * 37)
    
    class CompressionMonitor:
        """Monitor compression performance and costs."""
        
        def __init__(self):
            self.metrics = {
                'total_requests': 0,
                'total_tokens_saved': 0,
                'total_processing_time': 0,
                'strategies_used': {},
                'estimated_cost_savings': 0.0
            }
        
        def track_compression(self, result: Any, model: str = "gpt-3.5-turbo"):
            """Track compression metrics."""
            self.metrics['total_requests'] += 1
            self.metrics['total_tokens_saved'] += result.tokens_saved
            self.metrics['total_processing_time'] += result.processing_time
            
            strategy = result.strategy_used
            self.metrics['strategies_used'][strategy] = (
                self.metrics['strategies_used'].get(strategy, 0) + 1
            )
            
            # Estimate cost savings (simplified)
            cost_per_token = 0.0005 / 1000  # GPT-3.5-turbo pricing
            self.metrics['estimated_cost_savings'] += result.tokens_saved * cost_per_token
        
        def get_summary(self) -> Dict[str, Any]:
            """Get performance summary."""
            avg_processing_time = (
                self.metrics['total_processing_time'] / self.metrics['total_requests']
                if self.metrics['total_requests'] > 0 else 0
            )
            
            return {
                'total_requests': self.metrics['total_requests'],
                'total_tokens_saved': self.metrics['total_tokens_saved'],
                'average_processing_time_ms': avg_processing_time * 1000,
                'strategies_used': self.metrics['strategies_used'],
                'estimated_cost_savings_usd': self.metrics['estimated_cost_savings']
            }
    
    # Test monitoring
    monitor = CompressionMonitor()
    
    # Simulate some compressions
    test_texts = sample_texts["batch_content"]
    
    for i, text in enumerate(test_texts):
        result = compressor.compress(text, target_ratio=0.5)
        monitor.track_compression(result)
        print(f"   Processed text {i+1}: {result.tokens_saved} tokens saved")
    
    summary = monitor.get_summary()
    print(f"\n📊 Performance Summary:")
    print(f"   Total requests: {summary['total_requests']}")
    print(f"   Total tokens saved: {summary['total_tokens_saved']}")
    print(f"   Average processing time: {summary['average_processing_time_ms']:.1f}ms")
    print(f"   Estimated cost savings: ${summary['estimated_cost_savings_usd']:.6f}")
    print(f"   Strategies used: {summary['strategies_used']}")
    
    print("\n✅ All integration examples completed!")
    
    print("\n💡 Integration Tips:")
    print("   • Always check if optional dependencies are available")
    print("   • Use appropriate tokenizers for accurate token counting")
    print("   • Monitor compression performance and cost savings")
    print("   • Implement fallbacks for when compression fails")
    print("   • Consider query-aware compression for better relevance")
    print("   • Test with your specific use case and requirements")
    
    print("\n🔧 Next Steps:")
    print("   • Install optional dependencies: pip install langchain openai tiktoken")
    print("   • Adapt examples to your specific AI workflow")
    print("   • Implement monitoring and logging in production")
    print("   • Test with your actual API costs and limits")


if __name__ == "__main__":
    main()