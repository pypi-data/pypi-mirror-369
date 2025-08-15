#!/usr/bin/env python3
"""
Command-line interface for AI Context Compressor.

Provides a simple CLI for compressing text files and testing the package.
"""

import argparse
import sys
import json
import os
from pathlib import Path
from typing import Optional, List

from . import ContextCompressor, __version__


def compress_command(args):
    """Handle compression command."""
    compressor = ContextCompressor()
    
    # Read input text
    if args.input == '-':
        text = sys.stdin.read()
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # Perform compression
    result = compressor.compress(
        text=text,
        target_ratio=args.ratio,
        strategy=args.strategy,
        query=args.query,
        evaluate_quality=not args.no_quality
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result.compressed_text)
    else:
        print(result.compressed_text)
    
    # Print stats to stderr unless quiet
    if not args.quiet:
        print(f"Original tokens: {result.original_tokens}", file=sys.stderr)
        print(f"Compressed tokens: {result.compressed_tokens}", file=sys.stderr)
        print(f"Tokens saved: {result.tokens_saved}", file=sys.stderr)
        print(f"Compression ratio: {result.actual_ratio:.1%}", file=sys.stderr)
        print(f"Processing time: {result.processing_time:.3f}s", file=sys.stderr)
        
        if result.quality_metrics and not args.no_quality:
            print(f"Quality score: {result.quality_metrics.overall_score:.3f}", file=sys.stderr)


def batch_command(args):
    """Handle batch compression command."""
    compressor = ContextCompressor()
    
    # Read input files
    texts = []
    for input_file in args.inputs:
        if input_file == '-':
            texts.append(sys.stdin.read())
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                texts.append(f.read())
    
    # Perform batch compression
    batch_result = compressor.compress_batch(
        texts=texts,
        target_ratio=args.ratio,
        strategy=args.strategy,
        query=args.query,
        parallel=not args.no_parallel,
        evaluate_quality=not args.no_quality
    )
    
    # Output results
    if args.format == 'json':
        results = []
        for result in batch_result.results:
            results.append({
                'compressed_text': result.compressed_text,
                'original_tokens': result.original_tokens,
                'compressed_tokens': result.compressed_tokens,
                'tokens_saved': result.tokens_saved,
                'compression_ratio': result.actual_ratio,
                'processing_time': result.processing_time
            })
        
        output = {
            'results': results,
            'summary': {
                'total_texts': len(batch_result.results),
                'success_rate': batch_result.success_rate,
                'total_processing_time': batch_result.total_processing_time,
                'total_tokens_saved': batch_result.total_tokens_saved,
                'average_compression_ratio': batch_result.average_compression_ratio
            }
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)
        else:
            print(json.dumps(output, indent=2))
    else:
        # Text format
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(exist_ok=True)
            
            for i, result in enumerate(batch_result.results):
                output_file = output_dir / f"compressed_{i+1}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.compressed_text)
        else:
            for i, result in enumerate(batch_result.results):
                print(f"=== Result {i+1} ===")
                print(result.compressed_text)
                print()
    
    # Print summary to stderr unless quiet
    if not args.quiet:
        print(f"Processed: {len(batch_result.results)} texts", file=sys.stderr)
        print(f"Success rate: {batch_result.success_rate:.1%}", file=sys.stderr)
        print(f"Total tokens saved: {batch_result.total_tokens_saved}", file=sys.stderr)
        print(f"Processing time: {batch_result.total_processing_time:.3f}s", file=sys.stderr)


def list_strategies_command(args):
    """Handle list strategies command."""
    compressor = ContextCompressor()
    strategies = compressor.list_strategies()
    
    if args.format == 'json':
        strategy_info = []
        for strategy_name in strategies:
            info = compressor.get_strategy_info(strategy_name)
            if info:
                strategy_info.append(info)
        
        print(json.dumps(strategy_info, indent=2))
    else:
        print("Available strategies:")
        for strategy_name in strategies:
            info = compressor.get_strategy_info(strategy_name)
            if info:
                print(f"  {strategy_name}: {info['description']}")
            else:
                print(f"  {strategy_name}")


def server_command(args):
    """Handle server command."""
    try:
        from .api.main import app
        import uvicorn
        
        print(f"Starting Context Compressor API server on {args.host}:{args.port}")
        uvicorn.run(
            app, 
            host=args.host, 
            port=args.port,
            reload=args.reload
        )
    except ImportError:
        print("FastAPI not available. Install with: pip install 'context-compressor[api]'")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Context Compressor - Intelligent text compression for RAG systems",
        prog="context-compressor"
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'context-compressor {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress a single text')
    compress_parser.add_argument(
        'input', 
        help='Input file path (use "-" for stdin)'
    )
    compress_parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    compress_parser.add_argument(
        '-r', '--ratio',
        type=float,
        default=0.5,
        help='Target compression ratio (default: 0.5)'
    )
    compress_parser.add_argument(
        '-s', '--strategy',
        default='auto',
        help='Compression strategy (default: auto)'
    )
    compress_parser.add_argument(
        '-q', '--query',
        help='Query for context-aware compression'
    )
    compress_parser.add_argument(
        '--no-quality',
        action='store_true',
        help='Disable quality evaluation'
    )
    compress_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress statistics output'
    )
    compress_parser.set_defaults(func=compress_command)
    
    # Batch compress command
    batch_parser = subparsers.add_parser('batch', help='Compress multiple texts')
    batch_parser.add_argument(
        'inputs',
        nargs='+',
        help='Input file paths'
    )
    batch_parser.add_argument(
        '-o', '--output',
        help='Output directory (for text format) or file (for JSON format)'
    )
    batch_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    batch_parser.add_argument(
        '-r', '--ratio',
        type=float,
        default=0.5,
        help='Target compression ratio (default: 0.5)'
    )
    batch_parser.add_argument(
        '-s', '--strategy',
        default='auto',
        help='Compression strategy (default: auto)'
    )
    batch_parser.add_argument(
        '-q', '--query',
        help='Query for context-aware compression'
    )
    batch_parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel processing'
    )
    batch_parser.add_argument(
        '--no-quality',
        action='store_true',
        help='Disable quality evaluation'
    )
    batch_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress statistics output'
    )
    batch_parser.set_defaults(func=batch_command)
    
    # List strategies command
    list_parser = subparsers.add_parser('strategies', help='List available compression strategies')
    list_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    list_parser.set_defaults(func=list_strategies_command)
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start the API server')
    server_parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    server_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    server_parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )
    server_parser.set_defaults(func=server_command)
    
    # Parse arguments and execute command
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()