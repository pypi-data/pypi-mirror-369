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

## Advanced Usage

### Custom Tokenization Rules

```python
from ultra_tokenizer import Tokenizer
import re

# Custom tokenization with regex pattern
custom_tokenizer = Tokenizer(
    tokenization_pattern=r"\b\w+\b|\S"  # Words or non-whitespace characters
)
```

### Batch Processing

```python
# Process multiple texts efficiently
texts = ["First sentence.", "Second sentence.", "Third sentence."]
all_tokens = [tokenizer.tokenize(text) for text in texts]
```

## Customization

### Special Tokens

```python
from ultra_tokenizer import Tokenizer

# Initialize with custom special tokens
tokenizer = Tokenizer(
    special_tokens={
        "unk_token": "[UNK]",
        "pad_token": "[PAD]",
        "cls_token": "[CLS]",
        "sep_token": "[SEP]"
    }
)
```

### Custom Preprocessing

```python
def custom_preprocessor(text):
    # Your custom preprocessing logic here
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

tokenizer = Tokenizer(preprocessing_fn=custom_preprocessor)
```

## Fine-tuning

### Updating an Existing Tokenizer

```python
# Continue training on new data
with open("new_data.txt", "r", encoding="utf-8") as f:
    trainer = TokenizerTrainer(vocab_size=35000)  # Slightly larger vocab
    tokenizer = trainer.train_from_files(
        ["new_data.txt"],
        initial_tokenizer=tokenizer  # Start from existing tokenizer
    )
```

### Domain-Specific Fine-tuning

```python
# Fine-tune on domain-specific data
domain_trainer = TokenizerTrainer(
    vocab_size=32000,
    min_frequency=1,  # Include rare terms
    special_tokens={"additional_special_tokens": ["[MED]", "[DISEASE]", "[TREATMENT]"]}
)

domain_tokenizer = domain_trainer.train_from_files(
    ["medical_corpus.txt"],
    initial_tokenizer=tokenizer  # Start from base tokenizer
)
```

### Performance Optimization

```python
# Optimize for inference
tokenizer.enable_caching()  # Cache tokenization results
fast_tokens = tokenizer.tokenize("Optimized for speed!")
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

