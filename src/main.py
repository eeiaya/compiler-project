from __future__ import annotations

import argparse
import sys

from src.lexer.formatter import format_error, format_tokens
from src.lexer.scanner import scan_all
from src.utils.files import read_text, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="compiler", description="MiniCompiler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lex_parser = subparsers.add_parser("lex", help="Tokenize a source file")
    lex_parser.add_argument("--input", required=True, help="Path to input .src file")
    lex_parser.add_argument("--output", help="Path to output token file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "lex":
        source = read_text(args.input)
        tokens, errors = scan_all(source)
        token_output = format_tokens(tokens)

        if args.output:
            write_text(args.output, token_output + ("\n" if token_output else ""))
        else:
            print(token_output)

        if errors:
            for error in errors:
                print(format_error(error), file=sys.stderr)
            return 1

        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())