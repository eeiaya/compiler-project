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


def read_raw_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as file:
        return file.read()


def scan_source(source: str):
    scanner = Scanner(source)
    tokens = []

    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.token_type == TokenType.END_OF_FILE:
            break

    return scanner, tokens, scanner.errors


def render_source(source: str) -> str:
    _, tokens, errors = scan_source(source)
    lines = [format_token(token) for token in tokens]
    lines.extend(format_error(error) for error in errors)
    return "\n".join(lines)


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


class FixtureComparisonTests(unittest.TestCase):
    maxDiff = None

    def _run_fixture_group(self, group_name: str) -> None:
        group_dir = ROOT / "tests" / "lexer" / group_name
        for src_file in sorted(group_dir.glob("*.src")):
            expected_file = src_file.with_suffix(".expected")
            with self.subTest(file=src_file.name):
                self.assertTrue(
                    expected_file.exists(),
                    f"Missing expected file for {src_file.name}",
                )
                source = read_raw_text(src_file)
                expected = read_raw_text(expected_file).strip()
                actual = render_source(source).strip()

                if actual != expected:
                    diff = build_diff(src_file.stem, expected, actual)
                    self.fail(
                        f"Fixture mismatch for {src_file.name}\n"
                        f"{diff if diff else 'No textual diff available.'}"
                    )

    def test_valid_fixtures(self) -> None:
        self._run_fixture_group("valid")

    def test_invalid_fixtures(self) -> None:
        self._run_fixture_group("invalid")


class LexerUnitTests(unittest.TestCase):
    maxDiff = None

    def test_keywords_are_reserved_words(self) -> None:
        _, tokens, errors = scan_source(
            "if else while for int float bool return true false void struct fn"
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.KW_IF,
                TokenType.KW_ELSE,
                TokenType.KW_WHILE,
                TokenType.KW_FOR,
                TokenType.KW_INT,
                TokenType.KW_FLOAT,
                TokenType.KW_BOOL,
                TokenType.KW_RETURN,
                TokenType.KW_TRUE,
                TokenType.KW_FALSE,
                TokenType.KW_VOID,
                TokenType.KW_STRUCT,
                TokenType.KW_FN,
                TokenType.END_OF_FILE,
            ],
        )

    def test_identifier_rules_and_length_limits(self) -> None:
        valid_identifier = "A" + ("b" * 254)
        _, tokens, errors = scan_source(valid_identifier)
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].token_type, TokenType.IDENTIFIER)
        self.assertEqual(len(tokens[0].lexeme), 255)

        too_long_identifier = "a" * 256
        _, tokens, errors = scan_source(too_long_identifier)
        self.assertEqual([token.token_type for token in tokens], [TokenType.END_OF_FILE])
        self.assertEqual(len(errors), 1)
        self.assertIn("maximum length of 255", errors[0].message)

    def test_integer_literals_and_range(self) -> None:
        _, tokens, errors = scan_source("0 2147483647")
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].literal_value, 0)
        self.assertEqual(tokens[1].literal_value, 2147483647)

        _, tokens, errors = scan_source("2147483648")
        self.assertEqual([token.token_type for token in tokens], [TokenType.END_OF_FILE])
        self.assertEqual(len(errors), 1)
        self.assertIn("out of range", errors[0].message)

    def test_float_and_string_literals(self) -> None:
        _, tokens, errors = scan_source('3.14 "hello\\nworld"')
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].token_type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[0].literal_value, 3.14)
        self.assertEqual(tokens[1].token_type, TokenType.STRING_LITERAL)
        self.assertEqual(tokens[1].literal_value, "hello\nworld")

    def test_boolean_literals_have_values(self) -> None:
        _, tokens, errors = scan_source("true false")
        self.assertEqual(errors, [])
        self.assertEqual(tokens[0].token_type, TokenType.KW_TRUE)
        self.assertEqual(tokens[0].literal_value, True)
        self.assertEqual(tokens[1].token_type, TokenType.KW_FALSE)
        self.assertEqual(tokens[1].literal_value, False)

    def test_operators_and_delimiters(self) -> None:
        source = "+ - * / % == != < <= > >= && || ! = += -= *= /= %= ( ) { } [ ] , ; ."
        _, tokens, errors = scan_source(source)
        self.assertEqual(errors, [])
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.PERCENT,
                TokenType.EQUAL_EQUAL,
                TokenType.BANG_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.AND_AND,
                TokenType.OR_OR,
                TokenType.BANG,
                TokenType.ASSIGN,
                TokenType.PLUS_EQUAL,
                TokenType.MINUS_EQUAL,
                TokenType.STAR_EQUAL,
                TokenType.SLASH_EQUAL,
                TokenType.PERCENT_EQUAL,
                TokenType.LPAREN,
                TokenType.RPAREN,
                TokenType.LBRACE,
                TokenType.RBRACE,
                TokenType.LBRACKET,
                TokenType.RBRACKET,
                TokenType.COMMA,
                TokenType.SEMICOLON,
                TokenType.DOT,
                TokenType.END_OF_FILE,
            ],
        )

    def test_comments_are_skipped(self) -> None:
        source = "int x; // line comment\n/* block comment */\nreturn x;"
        _, tokens, errors = scan_source(source)
        self.assertEqual(errors, [])
        self.assertEqual(
            [token.lexeme for token in tokens],
            ["int", "x", ";", "return", "x", ";", ""],
        )

    def test_line_endings_unix_windows_and_carriage_return(self) -> None:
        source = "int x;\rreturn y;\r\nfloat z;\n"
        _, tokens, errors = scan_source(source)
        self.assertEqual(errors, [])

        interesting = [
            (token.lexeme, token.line, token.column)
            for token in tokens
            if token.token_type != TokenType.END_OF_FILE
        ]
        self.assertEqual(
            interesting,
            [
                ("int", 1, 1),
                ("x", 1, 5),
                (";", 1, 6),
                ("return", 2, 1),
                ("y", 2, 8),
                (";", 2, 9),
                ("float", 3, 1),
                ("z", 3, 7),
                (";", 3, 8),
            ],
        )

    def test_invalid_character_error_recovery(self) -> None:
        _, tokens, errors = scan_source("int @x;")
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.KW_INT,
                TokenType.IDENTIFIER,
                TokenType.SEMICOLON,
                TokenType.END_OF_FILE,
            ],
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid character", errors[0].message)

    def test_unterminated_string_error_recovery(self) -> None:
        _, tokens, errors = scan_source('return "hello\nx;')
        self.assertEqual(tokens[0].token_type, TokenType.KW_RETURN)
        self.assertEqual(tokens[1].token_type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].token_type, TokenType.SEMICOLON)
        self.assertEqual(tokens[3].token_type, TokenType.END_OF_FILE)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].message, "Unterminated string literal")

    def test_unterminated_comment_error(self) -> None:
        _, tokens, errors = scan_source("int x; /* never closed")
        self.assertEqual(tokens[-1].token_type, TokenType.END_OF_FILE)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].message, "Unterminated multi-line comment")

    def test_malformed_number_error_recovery(self) -> None:
        _, tokens, errors = scan_source("value = 12.34.56;")
        self.assertEqual(
            [token.token_type for token in tokens],
            [
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.SEMICOLON,
                TokenType.END_OF_FILE,
            ],
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("Malformed number literal", errors[0].message)

    def test_peek_token_does_not_advance(self) -> None:
        scanner = Scanner("fn main")
        first_peek = scanner.peek_token()
        self.assertEqual(first_peek.token_type, TokenType.KW_FN)
        self.assertEqual(scanner.get_line(), 1)
        self.assertEqual(scanner.get_column(), 1)

        first_next = scanner.next_token()
        self.assertEqual(first_next.token_type, TokenType.KW_FN)

        second_next = scanner.next_token()
        self.assertEqual(second_next.token_type, TokenType.IDENTIFIER)
        self.assertEqual(second_next.lexeme, "main")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)