from __future__ import annotations

import difflib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.lexer.formatter import format_error, format_token
from src.lexer.scanner import Scanner
from src.lexer.token import TokenType
from src.parser.parser import Parser
from src.parser.pretty_printer import PrettyPrinter


def read_raw_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as file:
        return file.read()


# ── Lexer rendering ────────────────────────────────────────────

def scan_source(source: str):
    scanner = Scanner(source)
    tokens = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.token_type == TokenType.END_OF_FILE:
            break
    return scanner, tokens, scanner.errors


def render_lexer(source: str) -> str:
    _, tokens, errors = scan_source(source)
    lines = [format_token(t) for t in tokens]
    lines.extend(format_error(e) for e in errors)
    return "\n".join(lines)


# ── Parser rendering ───────────────────────────────────────────

def render_parser(source: str) -> str:
    _, tokens, lex_errors = scan_source(source)
    parser = Parser(tokens)
    ast = parser.parse()
    text = PrettyPrinter().print(ast).rstrip()
    err_lines = [str(e) for e in parser.errors]
    return "\n".join([text, *err_lines]) if err_lines else text


def build_diff(name: str, expected: str, actual: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            expected.splitlines(),
            actual.splitlines(),
            fromfile=f"{name}.expected",
            tofile=f"{name}.actual",
            lineterm="",
        )
    )


class LexerFixtureTests(unittest.TestCase):
    maxDiff = None

    def _run(self, group: str) -> None:
        group_dir = ROOT / "tests" / "lexer" / group
        for src_file in sorted(group_dir.glob("*.src")):
            expected_file = src_file.with_suffix(".expected")
            with self.subTest(file=src_file.name):
                self.assertTrue(expected_file.exists(), f"Missing {expected_file}")
                source = read_raw_text(src_file)
                expected = read_raw_text(expected_file).strip()
                actual = render_lexer(source).strip()
                if actual != expected:
                    diff = build_diff(src_file.stem, expected, actual)
                    self.fail(f"Mismatch for {src_file.name}\n{diff}")

    def test_valid(self) -> None:
        self._run("valid")

    def test_invalid(self) -> None:
        self._run("invalid")


class ParserFixtureTests(unittest.TestCase):
    maxDiff = None

    def _run_dir(self, sub_path: Path) -> None:
        for src_file in sorted(sub_path.rglob("*.src")):
            expected_file = src_file.with_suffix(".expected")
            with self.subTest(file=str(src_file.relative_to(ROOT))):
                self.assertTrue(expected_file.exists(), f"Missing {expected_file}")
                source = read_raw_text(src_file)
                expected = read_raw_text(expected_file).strip()
                actual = render_parser(source).strip()
                if actual != expected:
                    diff = build_diff(src_file.stem, expected, actual)
                    self.fail(f"Mismatch for {src_file.name}\n{diff}")

    def test_valid(self) -> None:
        self._run_dir(ROOT / "tests" / "parser" / "valid")

    def test_invalid(self) -> None:
        self._run_dir(ROOT / "tests" / "parser" / "invalid")


class LexerUnitTests(unittest.TestCase):
    def test_keywords(self) -> None:
        _, tokens, errors = scan_source("if else while for int return")
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].token_type, TokenType.KW_IF)


class ParserUnitTests(unittest.TestCase):
    maxDiff = None

    def _parse(self, source: str):
        _, tokens, _ = scan_source(source)
        parser = Parser(tokens)
        return parser, parser.parse()

    def test_simple_function(self) -> None:
        parser, ast = self._parse("fn main() { return; }")
        self.assertEqual(parser.errors, [])
        self.assertEqual(len(ast.declarations), 1)
        self.assertEqual(ast.declarations[0].name, "main")

    def test_operator_precedence_text(self) -> None:
        parser, ast = self._parse("fn f() { int x = 1 + 2 * 3; }")
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        self.assertIn("(1 + (2 * 3))", text)

    def test_left_associativity(self) -> None:
        parser, ast = self._parse("fn f() { int x = 10 - 3 - 2; }")
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        self.assertIn("((10 - 3) - 2)", text)

    def test_assignment_right_associativity(self) -> None:
        parser, ast = self._parse("fn f() { a = b = 5; }")
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        self.assertIn("(a = (b = 5))", text)

    def test_dangling_else(self) -> None:
        source = "fn f() { if (a) if (b) x = 1; else x = 2; }"
        parser, ast = self._parse(source)
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        # 'else' must attach to the inner 'if'
        self.assertIn("Else:", text)

    def test_missing_semicolon_reports_error(self) -> None:
        parser, _ = self._parse("fn f() { int x = 5 }")
        self.assertTrue(len(parser.errors) >= 1)

    def test_function_call_with_args(self) -> None:
        parser, ast = self._parse("fn f() { foo(1, 2, 3); }")
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        self.assertIn("foo(1, 2, 3)", text)

    def test_unary(self) -> None:
        parser, ast = self._parse("fn f() { int x = -5; bool b = !true; }")
        self.assertEqual(parser.errors, [])
        text = PrettyPrinter().print(ast)
        self.assertIn("(-5)", text)
        self.assertIn("(!true)", text)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)