# Contributing to AI Context Compressor

We welcome contributions to the AI Context Compressor project! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/ai-context-compressor.git
   cd ai-context-compressor
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all checks before committing:
```bash
black .
isort .
flake8 .
mypy src/
```

### Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=context_compressor

# Run specific tests
pytest tests/test_compressor.py

# Run fast tests only (skip slow/integration tests)
pytest -m "not slow"
```

### Documentation

- All public functions and classes must have docstrings
- Use Google-style docstrings
- Update README.md if adding new features
- Add examples for new functionality

## 📝 Types of Contributions

### 🐛 Bug Reports

When filing a bug report, please include:

- Python version
- Package version
- Minimal code example reproducing the issue
- Expected vs actual behavior
- Error messages and stack traces

### ✨ Feature Requests

For feature requests, please provide:

- Clear description of the feature
- Use case and motivation
- Proposed API if applicable
- Any relevant examples or references

### 🔧 Code Contributions

#### Adding New Compression Strategies

To add a new compression strategy:

1. Create a new file in `src/context_compressor/strategies/`
2. Inherit from `CompressionStrategy` base class
3. Implement required abstract methods
4. Add comprehensive tests
5. Update documentation

Example:
```python
from .base import CompressionStrategy
from ..core.models import StrategyMetadata

class MyStrategy(CompressionStrategy):
    def _create_metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            name="my_strategy",
            description="Description of my strategy",
            version="1.0.0",
            author="Your Name"
        )
    
    def _compress_text(self, text: str, target_ratio: float, **kwargs) -> str:
        # Implement your compression logic
        return compressed_text
```

#### Adding New Quality Metrics

To add new quality evaluation metrics:

1. Extend the `QualityEvaluator` class
2. Add new fields to `QualityMetrics` dataclass
3. Update the overall score calculation
4. Add tests for the new metrics

### 📚 Documentation Improvements

- Fix typos and grammatical errors
- Improve examples and tutorials
- Add missing documentation for existing features
- Translate documentation (future)

## 🎯 Pull Request Process

1. **Create a branch**: 
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   pytest
   python test_installation.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: your descriptive commit message"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Provide a clear title and description
   - Reference any related issues
   - Ensure all checks pass

### Pull Request Guidelines

- Keep PRs focused and atomic
- Write clear commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all CI checks pass

## 🏷️ Commit Message Guidelines

We follow conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test-related changes
- `chore:` - Maintenance tasks

Examples:
- `feat: add abstractive compression strategy`
- `fix: handle empty text input in extractive strategy`
- `docs: update API examples in README`

## 🧪 Testing Guidelines

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Performance tests**: Test speed and memory usage
- **Quality tests**: Test compression quality metrics

### Test Structure

```python
def test_feature_name():
    # Arrange
    compressor = ContextCompressor()
    text = "Sample text for testing"
    
    # Act
    result = compressor.compress(text, target_ratio=0.5)
    
    # Assert
    assert result.actual_ratio <= 0.6
    assert result.compressed_text != text
```

### Performance Testing

For performance-critical changes:

```python
import time

def test_compression_performance():
    compressor = ContextCompressor()
    text = "Large text for performance testing..." * 100
    
    start_time = time.time()
    result = compressor.compress(text, target_ratio=0.5)
    processing_time = time.time() - start_time
    
    assert processing_time < 0.1  # Should complete in under 100ms
```

## 🔍 Code Review Process

All contributions go through code review:

1. Automated checks must pass (tests, linting, etc.)
2. At least one maintainer approval required
3. Address any feedback or requested changes
4. Maintainer merges the PR

## 📋 Issue Triage

We use labels to organize issues:

- `bug`: Something isn't working
- `enhancement`: New feature request
- `documentation`: Improvements to docs
- `good first issue`: Good for newcomers
- `help wanted`: Community help needed
- `question`: Questions about usage

## 🎉 Recognition

Contributors are recognized in:

- CHANGELOG.md for their contributions
- GitHub contributors page
- Special thanks in releases

## 📞 Getting Help

- Create an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues and discussions first

## 📜 Code of Conduct

Please be respectful and inclusive in all interactions. We're building a welcoming community for everyone interested in AI text compression.

## 📈 Roadmap

Current priorities:

1. Additional compression strategies (abstractive, semantic, hybrid)
2. Multi-language support
3. Integration with more LLM providers
4. Performance optimizations
5. GUI interface

## 🙏 Thank You!

Thank you for contributing to AI Context Compressor! Your contributions help make text compression more accessible and effective for the AI community.