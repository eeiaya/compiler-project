"""generate_invalid_expected.py — capture actual parser output for invalid fixtures."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.lexer.scanner import Scanner
from src.lexer.token import TokenType
from src.parser.parser import Parser
from src.parser.pretty_printer import PrettyPrinter


def scan_tokens(source: str):
    scanner = Scanner(source)
    tokens = []
    while True:
        t = scanner.next_token()
        tokens.append(t)
        if t.token_type == TokenType.END_OF_FILE:
            break
    return tokens


def render(source: str) -> str:
    tokens = scan_tokens(source)
    parser = Parser(tokens)
    ast = parser.parse()
    text = PrettyPrinter().print(ast).rstrip()
    errs = "\n".join(str(e) for e in parser.errors)
    return f"{text}\n{errs}\n" if errs else f"{text}\n"


def main() -> None:
    invalid_dir = ROOT / "tests" / "parser" / "invalid"
    for src_file in sorted(invalid_dir.rglob("*.src")):
        source = src_file.read_text(encoding="utf-8")
        output = render(source)
        expected_file = src_file.with_suffix(".expected")
        expected_file.write_text(output, encoding="utf-8", newline="\n")
        print(f"  wrote  {expected_file.relative_to(ROOT)}")
    print("\nDone.")


if __name__ == "__main__":
    main()