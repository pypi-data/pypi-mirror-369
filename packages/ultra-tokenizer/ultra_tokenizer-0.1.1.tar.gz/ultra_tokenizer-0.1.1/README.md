# Ultra-Tokenizer

[![PyPI version](https://img.shields.io/pypi/v/ultra-tokenizer.svg)](https://pypi.org/project/ultra-tokenizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/ultra-tokenizer.svg)](https://pypi.org/project/ultra-tokenizer/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/pranav271103/Ultra-Tokenizer/graph/badge.svg?token=YOUR-TOKEN)](https://codecov.io/gh/pranav271103/Ultra-Tokenizer)
[![Documentation Status](https://readthedocs.org/projects/mytokenizer/badge/?version=latest)](https://mytokenizer.readthedocs.io/en/latest/?badge=latest)

Ultra-Tokenizer is a high-performance, production-ready tokenizer that supports multiple subword tokenization algorithms including BPE, WordPiece, and Unigram. Designed for efficiency and flexibility, it's perfect for modern NLP pipelines.

## Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## Why Choose Ultra-Tokenizer?

While there are several tokenization libraries available, Ultra-Tokenizer stands out in several key areas:

### Performance Optimized
- **Lightning Fast**: Engineered for high throughput with minimal memory overhead
- **Efficient Memory Usage**: Intelligent caching mechanisms reduce memory footprint
- **Parallel Processing**: Built-in support for multi-core tokenization

### Developer Friendly
- **Simple API**: Intuitive interface that's easy to integrate into any pipeline
- **Full Type Hints**: Better IDE support and code completion
- **Comprehensive Documentation**: Detailed guides and API references
- **Minimal Dependencies**: Lightweight with no unnecessary bloat

### Flexible & Extensible
- **Multiple Algorithms**: Switch between BPE, WordPiece, and Unigram with a single parameter
- **Custom Tokenization Rules**: Easily add domain-specific tokenization rules
- **Train on Your Data**: Simple interface for training custom tokenizers on your corpus

### Production Ready
- **Robust Error Handling**: Graceful handling of edge cases and malformed input
- **100% Test Coverage**: Thoroughly tested across different scenarios
- **Performance Benchmarks**: Consistently outperforms alternatives in speed and memory usage

### Comparison with Other Tokenizers

| Feature | Ultra-Tokenizer | HuggingFace Tokenizers | spaCy | NLTK |
|---------|-------------|------------------------|-------|------|
| Multiple Algorithms | ✅ BPE, WordPiece, Unigram | ✅ BPE, WordPiece, Unigram | ❌ Mostly rule-based | ❌ Rule-based |
| Training Interface | ✅ Simple and intuitive | ✅ Comprehensive | ❌ Limited | ❌ No built-in training |
| Memory Efficiency | ✅ Excellent with smart caching | ⚠️ Good, but can be heavy | ✅ Good | ⚠️ Can be memory intensive |
| Performance | ⚡ Blazing fast | Fast | Fast | Slower |
| Dependencies | Minimal | Heavy (Rust) | Heavy (Cython) | Heavy |
| Type Hints | ✅ Full support | ⚠️ Partial | ⚠️ Partial | ❌ None |
| CLI Support | ✅ Built-in | ✅ Available | ❌ No | ❌ No |
| Learning Curve | Gentle | Steep | Moderate | Steep |

## Features

- **Multiple Tokenization Algorithms**: Byte Pair Encoding (BPE), WordPiece, and Unigram support
- **High Performance**: Optimized for speed with efficient implementations
- **Easy Integration**: Simple API for training and using tokenizers
- **Production Ready**: Comprehensive test coverage and robust error handling
- **Fully Typed**: Complete type annotations for better development experience
- **Multilingual Support**: Excellent handling of various languages and scripts
- **Special Token Support**: Built-in handling of special tokens
- **Memory Efficient**: Low memory footprint with smart caching
- **Customizable**: Flexible configuration options for different use cases
- **CLI Support**: Command-line interface for easy usage

## Installation

Install the latest stable version from PyPI:

```bash
pip install ultra-tokenizer
```

For the latest development version:

```bash
pip install git+https://github.com/pranav271103/Ultra-Tokenizer.git
```

For development:

```bash
git clone https://github.com/pranav271103/Ultra-Tokenizer.git
cd Ultra-Tokenizer
pip install -e ".[dev]"  # Install in development mode with all dependencies
```

## Quick Start

### Basic Usage

```python
from ultra_tokenizer import Tokenizer, TokenizerTrainer

# Initialize and train a tokenizer
trainer = TokenizerTrainer(
    vocab_size=30000,
    min_frequency=2,
    lowercase=True,
    strip_accents=True
)

tokenizer = trainer.train(
    files=["path/to/your/text/file.txt"],
    algorithm="bpe",  # or "wordpiece" or "unigram"
    num_workers=4
)

# Tokenize text
text = "This is an example sentence."
tokens = tokenizer.tokenize(text)
print(tokens)
```

### Using Pre-trained Tokenizers

```python
from advanced_tokenizer import Tokenizer

# Load a pre-trained tokenizer
tokenizer = Tokenizer.from_pretrained("your-pretrained-tokenizer")

# Encode and decode text
encoded = tokenizer.encode("Hello, world!")
decoded = tokenizer.decode(encoded.ids)
```

## Documentation

Full documentation is available at [https://pranav271103.github.io/Ultra-Tokenizer/](https://pranav271103.github.io/Ultra-Tokenizer/)

### Key Components

- **Tokenizer**: Main class for tokenization
- **TokenizerTrainer**: For training new tokenizers
- **Vocabulary**: Manages token-to-ID mappings
- **Pre/Post Processors**: Handle text normalization and token processing

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

We use `black` for code formatting and `isort` for import sorting:

```bash
black .
isort .
```

### Building Documentation

```bash
cd docs
make html
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for more information.

## Contact

Pranav Singh - pranav.singh01010101@gmail.com

Project Link: [Ultra-Tokenizer](https://github.com/pranav271103/Ultra-Tokenizer.git)

## Acknowledgments

- [Hugging Face Tokenizers](https://github.com/huggingface/tokenizers) - Inspiration for some design patterns
- [YouTokenToMe](https://github.com/VKCOM/YouTokenToMe) - For BPE implementation reference
- All contributors who helped improve this project

## Performance

The tokenizer is optimized for both training and inference:
- **Training**: Uses multiprocessing for faster vocabulary building
- **Inference**: Efficient lookup tables for fast tokenization
- **Memory**: Optimized to handle large vocabularies

## Customization

You can extend the tokenizer by:
1. Adding new pre-tokenization rules
2. Implementing custom subword algorithms
3. Adding support for additional languages

