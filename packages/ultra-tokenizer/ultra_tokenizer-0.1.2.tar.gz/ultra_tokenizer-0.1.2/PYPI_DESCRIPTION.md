# Ultra-Tokenizer

[![PyPI version](https://img.shields.io/pypi/v/ultra-tokenizer.svg)](https://pypi.org/project/ultra-tokenizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/ultra-tokenizer.svg)](https://pypi.org/project/ultra-tokenizer/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/ultra-tokenizer/badge/?version=latest)](https://pranav271103.github.io/Ultra-Tokenizer/)

## Features

- **Multiple Tokenization Algorithms**: Supports BPE, WordPiece, and Unigram algorithms
- **High Performance**: Optimized for speed and memory efficiency
- **Easy Integration**: Simple API for training and using tokenizers
- **Production Ready**: Battle-tested with comprehensive test coverage
- **Type Hints**: Full Python type support for better development experience

## Installation

Install the latest stable version from PyPI:

```bash
pip install ultra-tokenizer
```

## Quick Start

### Basic Usage

```python
from ultra_tokenizer import Tokenizer

# Initialize tokenizer with default settings
tokenizer = Tokenizer()

# Tokenize text
text = "Hello, world! This is Ultra-Tokenizer in action."
tokens = tokenizer.tokenize(text)
print(tokens)
# Output: ['Hello', ',', 'world', '!', 'This', 'is', 'Ultra', '-', 'Token', '##izer', 'in', 'action', '.']
```

### Training a New Tokenizer

```python
from ultra_tokenizer import TokenizerTrainer

# Initialize trainer
trainer = TokenizerTrainer(
    vocab_size=30000,
    min_frequency=2,
    show_progress=True
)

# Train on text files
tokenizer = trainer.train_from_files(["file1.txt", "file2.txt"])

# Save tokenizer
tokenizer.save("my_tokenizer.json")

# Load tokenizer
from ultra_tokenizer import Tokenizer
tokenizer = Tokenizer.from_file("my_tokenizer.json")
```

## Documentation

For detailed documentation, examples, and API reference, please visit:

[Ultra-Tokenizer Documentation](https://pranav271103.github.io/Ultra-Tokenizer/)

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please [open an issue](https://github.com/pranav271103/Ultra-Tokenizer/issues) or contact [pranav.singh01010101@gmail.com](mailto:pranav.singh01010101@gmail.com).

