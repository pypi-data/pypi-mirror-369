"""Command-line interface for the Advanced Tokenizer."""

import argparse
import json
import os
import sys
from typing import List, Optional, Dict, Any

from .tokenizer import Tokenizer
from .trainer import TokenizerTrainer


def train_command(args: argparse.Namespace) -> None:
    """Handle the train subcommand."""
    trainer = TokenizerTrainer(
        vocab_size=args.vocab_size,
        min_frequency=args.min_frequency,
        lowercase=args.lowercase,
        strip_accents=args.strip_accents,
    )

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    tokenizer = trainer.train(
        files=args.files,
        algorithm=args.algorithm,
        num_workers=args.num_workers,
    )

    trainer.save(os.path.join(args.output_dir, "tokenizer"))
    print(f"Tokenizer trained and saved to {args.output_dir}")


def tokenize_command(args: argparse.Namespace) -> None:
    """Handle the tokenize subcommand."""
    if not os.path.exists(args.model):
        print(f"Error: Model directory '{args.model}' not found.", file=sys.stderr)
        sys.exit(1)

    trainer = TokenizerTrainer.load(args.model)
    tokenizer = trainer.tokenizer

    if args.text:
        tokens = tokenizer.tokenize(args.text)
        if args.output_format == "json":
            print(json.dumps({"tokens": tokens}))
        else:
            print(" ".join(tokens))
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        tokens = tokenizer.tokenize(text)
        if args.output_format == "json":
            print(json.dumps({"tokens": tokens}))
        else:
            print("\n".join(tokens))
    else:
        print("No input provided. Use --text or --file.", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Advanced Tokenizer - A high-performance tokenizer for NLP tasks"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a new tokenizer")
    train_parser.add_argument("files", nargs="+", help="Input text files for training")
    train_parser.add_argument(
        "--output-dir",
        "-o",
        default="./models",
        help="Directory to save the trained tokenizer (default: ./models)",
    )
    train_parser.add_argument(
        "--vocab-size",
        type=int,
        default=30000,
        help="Maximum vocabulary size (default: 30000)",
    )
    train_parser.add_argument(
        "--min-frequency",
        type=int,
        default=2,
        help="Minimum frequency of tokens (default: 2)",
    )
    train_parser.add_argument(
        "--algorithm",
        choices=["bpe", "wordpiece", "unigram"],
        default="bpe",
        help="Tokenization algorithm (default: bpe)",
    )
    train_parser.add_argument(
        "--num-workers",
        type=int,
        default=4,
        help="Number of worker processes (default: 4)",
    )
    train_parser.add_argument(
        "--lowercase", action="store_true", help="Convert text to lowercase"
    )
    train_parser.add_argument(
        "--strip-accents", action="store_true", help="Strip accents from text"
    )
    train_parser.set_defaults(func=train_command)

    # Tokenize command
    tokenize_parser = subparsers.add_parser("tokenize", help="Tokenize text")
    tokenize_input = tokenize_parser.add_mutually_exclusive_group(required=True)
    tokenize_input.add_argument("--text", help="Text to tokenize")
    tokenize_input.add_argument("--file", help="File containing text to tokenize")
    tokenize_parser.add_argument(
        "--model", "-m", required=True, help="Path to the trained tokenizer model"
    )
    tokenize_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    tokenize_parser.set_defaults(func=tokenize_command)

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
