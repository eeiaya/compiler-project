"""create_parser_fixtures.py — wipe and recreate parser test fixtures."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARSER_DIR = ROOT / "tests" / "parser"

FIXTURES = {
    # ── expressions ────────────────────────────────────────────
    "tests/parser/valid/expressions/test_arithmetic.src":
        "fn f() { int x = 1 + 2 * 3; }\n",
    "tests/parser/valid/expressions/test_arithmetic.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        VarDecl: int x = (1 + (2 * 3)) [line 1]\n",

    "tests/parser/valid/expressions/test_left_assoc.src":
        "fn f() { int x = 10 - 3 - 2; }\n",
    "tests/parser/valid/expressions/test_left_assoc.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        VarDecl: int x = ((10 - 3) - 2) [line 1]\n",

    "tests/parser/valid/expressions/test_unary.src":
        "fn f() { int x = -5; bool b = !true; }\n",
    "tests/parser/valid/expressions/test_unary.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        VarDecl: int x = (-5) [line 1]\n"
        "        VarDecl: bool b = (!true) [line 1]\n",

    "tests/parser/valid/expressions/test_logical.src":
        "fn f() { bool b = a && b || c; }\n",
    "tests/parser/valid/expressions/test_logical.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        VarDecl: bool b = ((a && b) || c) [line 1]\n",

    "tests/parser/valid/expressions/test_call.src":
        "fn f() { foo(1, 2, 3); }\n",
    "tests/parser/valid/expressions/test_call.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        ExprStmt: foo(1, 2, 3) [line 1]\n",

    "tests/parser/valid/expressions/test_assignment.src":
        "fn f() { a = b = 5; }\n",
    "tests/parser/valid/expressions/test_assignment.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        ExprStmt: (a = (b = 5)) [line 1]\n",

    # ── statements ─────────────────────────────────────────────
    "tests/parser/valid/statements/test_if_else.src":
        "fn f() { if (x > 0) { y = 1; } else { y = 2; } }\n",
    "tests/parser/valid/statements/test_if_else.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        If [line 1]:\n"
        "          Condition: (x > 0)\n"
        "          Then:\n"
        "            Block [line 1]:\n"
        "              ExprStmt: (y = 1) [line 1]\n"
        "          Else:\n"
        "            Block [line 1]:\n"
        "              ExprStmt: (y = 2) [line 1]\n",

    "tests/parser/valid/statements/test_while.src":
        "fn f() { while (n > 0) { n = n - 1; } }\n",
    "tests/parser/valid/statements/test_while.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        While [line 1]:\n"
        "          Condition: (n > 0)\n"
        "          Body:\n"
        "            Block [line 1]:\n"
        "              ExprStmt: (n = (n - 1)) [line 1]\n",

    "tests/parser/valid/statements/test_for.src":
        "fn f() { for (int i = 0; i < 10; i = i + 1) { x = i; } }\n",
    "tests/parser/valid/statements/test_for.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        For [line 1]:\n"
        "          Init:\n"
        "            VarDecl: int i = 0 [line 1]\n"
        "          Condition: (i < 10)\n"
        "          Update: (i = (i + 1))\n"
        "          Body:\n"
        "            Block [line 1]:\n"
        "              ExprStmt: (x = i) [line 1]\n",

    "tests/parser/valid/statements/test_return.src":
        "fn f() { return 42; }\n",
    "tests/parser/valid/statements/test_return.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        Return: 42 [line 1]\n",

    "tests/parser/valid/statements/test_empty_block.src":
        "fn f() { }\n",
    "tests/parser/valid/statements/test_empty_block.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: f -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        (empty)\n",

    # ── declarations ───────────────────────────────────────────
    "tests/parser/valid/declarations/test_function_no_params.src":
        "fn main() { return; }\n",
    "tests/parser/valid/declarations/test_function_no_params.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: main -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        Return [line 1]\n",

    "tests/parser/valid/declarations/test_function_with_params.src":
        "fn add(int a, int b) -> int { return a + b; }\n",
    "tests/parser/valid/declarations/test_function_with_params.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: add -> int [line 1]:\n"
        "    Parameters: [int a, int b]\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        Return: (a + b) [line 1]\n",

    "tests/parser/valid/declarations/test_struct.src":
        "struct Point { int x; int y; }\n",
    "tests/parser/valid/declarations/test_struct.expected":
        "Program [line 1]:\n"
        "  StructDecl: Point [line 1]:\n"
        "    VarDecl: int x [line 1]\n"
        "    VarDecl: int y [line 1]\n",

    "tests/parser/valid/declarations/test_global_var.src":
        "int counter = 0;\n",
    "tests/parser/valid/declarations/test_global_var.expected":
        "Program [line 1]:\n"
        "  VarDecl: int counter = 0 [line 1]\n",

    # ── full programs ──────────────────────────────────────────
    "tests/parser/valid/full_programs/test_factorial.src":
        "fn main() {\n"
        "    int n = 5;\n"
        "    int result = 1;\n"
        "    while (n > 0) {\n"
        "        result = result * n;\n"
        "        n = n - 1;\n"
        "    }\n"
        "    return;\n"
        "}\n",
    "tests/parser/valid/full_programs/test_factorial.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: main -> void [line 1]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        VarDecl: int n = 5 [line 2]\n"
        "        VarDecl: int result = 1 [line 3]\n"
        "        While [line 4]:\n"
        "          Condition: (n > 0)\n"
        "          Body:\n"
        "            Block [line 4]:\n"
        "              ExprStmt: (result = (result * n)) [line 5]\n"
        "              ExprStmt: (n = (n - 1)) [line 6]\n"
        "        Return [line 8]\n",

    "tests/parser/valid/full_programs/test_two_functions.src":
        "fn add(int a, int b) -> int { return a + b; }\n"
        "fn main() { int x = add(1, 2); }\n",
    "tests/parser/valid/full_programs/test_two_functions.expected":
        "Program [line 1]:\n"
        "  FunctionDecl: add -> int [line 1]:\n"
        "    Parameters: [int a, int b]\n"
        "    Body:\n"
        "      Block [line 1]:\n"
        "        Return: (a + b) [line 1]\n"
        "  FunctionDecl: main -> void [line 2]:\n"
        "    Parameters: []\n"
        "    Body:\n"
        "      Block [line 2]:\n"
        "        VarDecl: int x = add(1, 2) [line 2]\n",

    # ── invalid: syntax errors ─────────────────────────────────
    "tests/parser/invalid/syntax_errors/test_missing_semicolon.src":
        "fn f() { int x = 5 }\n",

    "tests/parser/invalid/syntax_errors/test_missing_rparen.src":
        "fn f() { if (x { y = 1; } }\n",

    "tests/parser/invalid/syntax_errors/test_missing_rbrace.src":
        "fn f() { int x = 1;\n",

    "tests/parser/invalid/syntax_errors/test_unexpected_token.src":
        "fn f() { return + ; }\n",

    "tests/parser/invalid/syntax_errors/test_bad_declaration.src":
        "@ fn f() { }\n",
}


def main() -> None:
    if PARSER_DIR.exists():
        shutil.rmtree(PARSER_DIR)
        print(f"  deleted  {PARSER_DIR.relative_to(ROOT)}/")

    for rel_path, content in FIXTURES.items():
        full = ROOT / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8", newline="\n")
        print(f"  created  {rel_path}")

    src_count = sum(1 for k in FIXTURES if k.endswith(".src"))
    print(f"\nDone — {src_count} parser test cases.")


if __name__ == "__main__":
    main()