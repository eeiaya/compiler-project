"""create_fixtures.py — wipe and recreate all lexer test fixtures."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VALID_DIR = ROOT / "tests" / "lexer" / "valid"
INVALID_DIR = ROOT / "tests" / "lexer" / "invalid"

FIXTURES = {
    # ── valid ──────────────────────────────────────────────────
    "tests/lexer/valid/test_identifiers.src":
        "alpha beta1 gamma_delta Zeta\n",
    "tests/lexer/valid/test_identifiers.expected":
        '1:1 IDENTIFIER "alpha"\n'
        '1:7 IDENTIFIER "beta1"\n'
        '1:13 IDENTIFIER "gamma_delta"\n'
        '1:25 IDENTIFIER "Zeta"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_numbers.src":
        "0 42 2147483647 3.14 10\n",
    "tests/lexer/valid/test_numbers.expected":
        '1:1 INT_LITERAL "0" 0\n'
        '1:3 INT_LITERAL "42" 42\n'
        '1:6 INT_LITERAL "2147483647" 2147483647\n'
        '1:17 FLOAT_LITERAL "3.14" 3.14\n'
        '1:22 INT_LITERAL "10" 10\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_keywords.src":
        "if else while for int float bool return true false void struct fn\n",
    "tests/lexer/valid/test_keywords.expected":
        '1:1 KW_IF "if"\n'
        '1:4 KW_ELSE "else"\n'
        '1:9 KW_WHILE "while"\n'
        '1:15 KW_FOR "for"\n'
        '1:19 KW_INT "int"\n'
        '1:23 KW_FLOAT "float"\n'
        '1:29 KW_BOOL "bool"\n'
        '1:34 KW_RETURN "return"\n'
        '1:41 KW_TRUE "true" true\n'
        '1:46 KW_FALSE "false" false\n'
        '1:52 KW_VOID "void"\n'
        '1:57 KW_STRUCT "struct"\n'
        '1:64 KW_FN "fn"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_operators.src":
        "+ - * / % == != < <= > >= && || ! = += -= *= /= %= ( ) { } [ ] , ; .\n",
    "tests/lexer/valid/test_operators.expected":
        '1:1 PLUS "+"\n'
        '1:3 MINUS "-"\n'
        '1:5 STAR "*"\n'
        '1:7 SLASH "/"\n'
        '1:9 PERCENT "%"\n'
        '1:11 EQUAL_EQUAL "=="\n'
        '1:14 BANG_EQUAL "!="\n'
        '1:17 LESS "<"\n'
        '1:19 LESS_EQUAL "<="\n'
        '1:22 GREATER ">"\n'
        '1:24 GREATER_EQUAL ">="\n'
        '1:27 AND_AND "&&"\n'
        '1:30 OR_OR "||"\n'
        '1:33 BANG "!"\n'
        '1:35 ASSIGN "="\n'
        '1:37 PLUS_EQUAL "+="\n'
        '1:40 MINUS_EQUAL "-="\n'
        '1:43 STAR_EQUAL "*="\n'
        '1:46 SLASH_EQUAL "/="\n'
        '1:49 PERCENT_EQUAL "%="\n'
        '1:52 LPAREN "("\n'
        '1:54 RPAREN ")"\n'
        '1:56 LBRACE "{"\n'
        '1:58 RBRACE "}"\n'
        '1:60 LBRACKET "["\n'
        '1:62 RBRACKET "]"\n'
        '1:64 COMMA ","\n'
        '1:66 SEMICOLON ";"\n'
        '1:68 DOT "."\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_comments.src":
        "int x; // comment\n"
        "/* block\n"
        "comment */\n"
        "return x;\n",
    "tests/lexer/valid/test_comments.expected":
        '1:1 KW_INT "int"\n'
        '1:5 IDENTIFIER "x"\n'
        '1:6 SEMICOLON ";"\n'
        '4:1 KW_RETURN "return"\n'
        '4:8 IDENTIFIER "x"\n'
        '4:9 SEMICOLON ";"\n'
        '5:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_strings.src":
        '"hello" "world" "test\\n123"\n',
    "tests/lexer/valid/test_strings.expected":
        '1:1 STRING_LITERAL "\\"hello\\"" "hello"\n'
        '1:9 STRING_LITERAL "\\"world\\"" "world"\n'
        '1:17 STRING_LITERAL "\\"test\\\\n123\\"" "test\\n123"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_mixed_tokens.src":
        "fn main() {\n"
        "    int x = 42;\n"
        "    return x;\n"
        "}\n",
    "tests/lexer/valid/test_mixed_tokens.expected":
        '1:1 KW_FN "fn"\n'
        '1:4 IDENTIFIER "main"\n'
        '1:8 LPAREN "("\n'
        '1:9 RPAREN ")"\n'
        '1:11 LBRACE "{"\n'
        '2:5 KW_INT "int"\n'
        '2:9 IDENTIFIER "x"\n'
        '2:11 ASSIGN "="\n'
        '2:13 INT_LITERAL "42" 42\n'
        '2:15 SEMICOLON ";"\n'
        '3:5 KW_RETURN "return"\n'
        '3:12 IDENTIFIER "x"\n'
        '3:13 SEMICOLON ";"\n'
        '4:1 RBRACE "}"\n'
        '5:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_empty.src":
        "\n",
    "tests/lexer/valid/test_empty.expected":
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_only_whitespace.src":
        "   \t  \n  \n",
    "tests/lexer/valid/test_only_whitespace.expected":
        '3:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_booleans.src":
        "true false\n",
    "tests/lexer/valid/test_booleans.expected":
        '1:1 KW_TRUE "true" true\n'
        '1:6 KW_FALSE "false" false\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_nested_comments.src":
        "int /* outer /* inner */ still outer */ x;\n",
    "tests/lexer/valid/test_nested_comments.expected":
        '1:1 KW_INT "int"\n'
        '1:41 IDENTIFIER "x"\n'
        '1:42 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_floats.src":
        "0.0 1.5 99.999\n",
    "tests/lexer/valid/test_floats.expected":
        '1:1 FLOAT_LITERAL "0.0" 0.0\n'
        '1:5 FLOAT_LITERAL "1.5" 1.5\n'
        '1:9 FLOAT_LITERAL "99.999" 99.999\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_assignment_operators.src":
        "+= -= *= /= %=\n",
    "tests/lexer/valid/test_assignment_operators.expected":
        '1:1 PLUS_EQUAL "+="\n'
        '1:4 MINUS_EQUAL "-="\n'
        '1:7 STAR_EQUAL "*="\n'
        '1:10 SLASH_EQUAL "/="\n'
        '1:13 PERCENT_EQUAL "%="\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_relational.src":
        "== != < <= > >=\n",
    "tests/lexer/valid/test_relational.expected":
        '1:1 EQUAL_EQUAL "=="\n'
        '1:4 BANG_EQUAL "!="\n'
        '1:7 LESS "<"\n'
        '1:9 LESS_EQUAL "<="\n'
        '1:12 GREATER ">"\n'
        '1:14 GREATER_EQUAL ">="\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_logical.src":
        "&& || !\n",
    "tests/lexer/valid/test_logical.expected":
        '1:1 AND_AND "&&"\n'
        '1:4 OR_OR "||"\n'
        '1:7 BANG "!"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_delimiters.src":
        "( ) { } [ ] , ; .\n",
    "tests/lexer/valid/test_delimiters.expected":
        '1:1 LPAREN "("\n'
        '1:3 RPAREN ")"\n'
        '1:5 LBRACE "{"\n'
        '1:7 RBRACE "}"\n'
        '1:9 LBRACKET "["\n'
        '1:11 RBRACKET "]"\n'
        '1:13 COMMA ","\n'
        '1:15 SEMICOLON ";"\n'
        '1:17 DOT "."\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_if_else.src":
        "if (x > 0) { return x; } else { return 0; }\n",
    "tests/lexer/valid/test_if_else.expected":
        '1:1 KW_IF "if"\n'
        '1:4 LPAREN "("\n'
        '1:5 IDENTIFIER "x"\n'
        '1:7 GREATER ">"\n'
        '1:9 INT_LITERAL "0" 0\n'
        '1:10 RPAREN ")"\n'
        '1:12 LBRACE "{"\n'
        '1:14 KW_RETURN "return"\n'
        '1:21 IDENTIFIER "x"\n'
        '1:22 SEMICOLON ";"\n'
        '1:24 RBRACE "}"\n'
        '1:26 KW_ELSE "else"\n'
        '1:31 LBRACE "{"\n'
        '1:33 KW_RETURN "return"\n'
        '1:40 INT_LITERAL "0" 0\n'
        '1:41 SEMICOLON ";"\n'
        '1:43 RBRACE "}"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_while_loop.src":
        "while (i < 10) { i += 1; }\n",
    "tests/lexer/valid/test_while_loop.expected":
        '1:1 KW_WHILE "while"\n'
        '1:7 LPAREN "("\n'
        '1:8 IDENTIFIER "i"\n'
        '1:10 LESS "<"\n'
        '1:12 INT_LITERAL "10" 10\n'
        '1:14 RPAREN ")"\n'
        '1:16 LBRACE "{"\n'
        '1:18 IDENTIFIER "i"\n'
        '1:20 PLUS_EQUAL "+="\n'
        '1:23 INT_LITERAL "1" 1\n'
        '1:24 SEMICOLON ";"\n'
        '1:26 RBRACE "}"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_struct.src":
        "struct Point { int x; int y; }\n",
    "tests/lexer/valid/test_struct.expected":
        '1:1 KW_STRUCT "struct"\n'
        '1:8 IDENTIFIER "Point"\n'
        '1:14 LBRACE "{"\n'
        '1:16 KW_INT "int"\n'
        '1:20 IDENTIFIER "x"\n'
        '1:21 SEMICOLON ";"\n'
        '1:23 KW_INT "int"\n'
        '1:27 IDENTIFIER "y"\n'
        '1:28 SEMICOLON ";"\n'
        '1:30 RBRACE "}"\n'
        '2:1 END_OF_FILE ""\n',

    "tests/lexer/valid/test_for_loop.src":
        "for (int i = 0; i < 5; i += 1) { x; }\n",
    "tests/lexer/valid/test_for_loop.expected":
        '1:1 KW_FOR "for"\n'
        '1:5 LPAREN "("\n'
        '1:6 KW_INT "int"\n'
        '1:10 IDENTIFIER "i"\n'
        '1:12 ASSIGN "="\n'
        '1:14 INT_LITERAL "0" 0\n'
        '1:15 SEMICOLON ";"\n'
        '1:17 IDENTIFIER "i"\n'
        '1:19 LESS "<"\n'
        '1:21 INT_LITERAL "5" 5\n'
        '1:22 SEMICOLON ";"\n'
        '1:24 IDENTIFIER "i"\n'
        '1:26 PLUS_EQUAL "+="\n'
        '1:29 INT_LITERAL "1" 1\n'
        '1:30 RPAREN ")"\n'
        '1:32 LBRACE "{"\n'
        '1:34 IDENTIFIER "x"\n'
        '1:35 SEMICOLON ";"\n'
        '1:37 RBRACE "}"\n'
        '2:1 END_OF_FILE ""\n',

    # ── invalid ────────────────────────────────────────────────
    "tests/lexer/invalid/test_invalid_char.src":
        "int @x;\n",
    "tests/lexer/invalid/test_invalid_char.expected":
        '1:1 KW_INT "int"\n'
        '1:6 IDENTIFIER "x"\n'
        '1:7 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:5 Invalid character '@'\n",

    "tests/lexer/invalid/test_unterminated_string.src":
        'return "hello\n'
        "x;\n",
    "tests/lexer/invalid/test_unterminated_string.expected":
        '1:1 KW_RETURN "return"\n'
        '2:1 IDENTIFIER "x"\n'
        '2:2 SEMICOLON ";"\n'
        '3:1 END_OF_FILE ""\n'
        "ERROR 1:8 Unterminated string literal\n",

    "tests/lexer/invalid/test_malformed_number.src":
        "value = 12.34.56;\n",
    "tests/lexer/invalid/test_malformed_number.expected":
        '1:1 IDENTIFIER "value"\n'
        '1:7 ASSIGN "="\n'
        '1:17 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:9 Malformed number literal '12.34.56'\n",

    "tests/lexer/invalid/test_unterminated_comment.src":
        "int x; /* never closed\n",
    "tests/lexer/invalid/test_unterminated_comment.expected":
        '1:1 KW_INT "int"\n'
        '1:5 IDENTIFIER "x"\n'
        '1:6 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:8 Unterminated multi-line comment\n",

    "tests/lexer/invalid/test_multiple_invalid.src":
        "int @x = #42;\n",
    "tests/lexer/invalid/test_multiple_invalid.expected":
        '1:1 KW_INT "int"\n'
        '1:6 IDENTIFIER "x"\n'
        '1:8 ASSIGN "="\n'
        '1:11 INT_LITERAL "42" 42\n'
        '1:13 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:5 Invalid character '@'\n"
        "ERROR 1:10 Invalid character '#'\n",

    "tests/lexer/invalid/test_integer_overflow.src":
        "2147483648\n",
    "tests/lexer/invalid/test_integer_overflow.expected":
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:1 Integer literal out of range '2147483648'\n",

    "tests/lexer/invalid/test_bad_string_escape.src":
        'return "abc\n'
        "next;\n",
    "tests/lexer/invalid/test_bad_string_escape.expected":
        '1:1 KW_RETURN "return"\n'
        '2:1 IDENTIFIER "next"\n'
        '2:5 SEMICOLON ";"\n'
        '3:1 END_OF_FILE ""\n'
        "ERROR 1:8 Unterminated string literal\n",

    "tests/lexer/invalid/test_lone_ampersand.src":
        "x & y;\n",
    "tests/lexer/invalid/test_lone_ampersand.expected":
        '1:1 IDENTIFIER "x"\n'
        '1:5 IDENTIFIER "y"\n'
        '1:6 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:3 Invalid character '&'\n",

    "tests/lexer/invalid/test_lone_pipe.src":
        "x | y;\n",
    "tests/lexer/invalid/test_lone_pipe.expected":
        '1:1 IDENTIFIER "x"\n'
        '1:5 IDENTIFIER "y"\n'
        '1:6 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:3 Invalid character '|'\n",

    "tests/lexer/invalid/test_identifier_too_long.src":
        "a" * 256 + ";\n",
    "tests/lexer/invalid/test_identifier_too_long.expected":
        '1:257 SEMICOLON ";"\n'
        '2:1 END_OF_FILE ""\n'
        "ERROR 1:1 Identifier exceeds maximum length of 255 characters: '"
        + "a" * 256 + "'\n",
}


def main() -> None:
    for d in (VALID_DIR, INVALID_DIR):
        if d.exists():
            shutil.rmtree(d)
            print(f"  deleted  {d.relative_to(ROOT)}/")

    for rel_path, content in FIXTURES.items():
        full_path = ROOT / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8", newline="\n")
        print(f"  created  {rel_path}")

    src_count = sum(1 for k in FIXTURES if k.endswith(".src"))
    print(f"\nDone — {src_count} test cases ({len(FIXTURES)} files total).")


if __name__ == "__main__":
    main()