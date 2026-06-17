# MiniCompiler Grammar Specification (Sprint 2)

The grammar is presented in EBNF notation.
The start symbol is **Program**.

## 1. Top-level

```ebnf
Program        = { Declaration } ;

Declaration    = FunctionDecl
               | StructDecl
               | VarDecl ;

FunctionDecl   = "fn" , Identifier , "(" , [ Parameters ] , ")" ,
                 [ "->" , Type ] , Block ;

StructDecl     = "struct" , Identifier , "{" , { VarDecl } , "}" ;

VarDecl        = Type , Identifier , [ "=" , Expression ] , ";" ;

Parameters     = Parameter , { "," , Parameter } ;
Parameter      = Type , Identifier ;
```
## 2. Statements
```ebnf

Statement      = Block
               | IfStmt
               | WhileStmt
               | ForStmt
               | ReturnStmt
               | VarDecl
               | ExprStmt
               | ";" ;

Block          = "{" , { Statement } , "}" ;
IfStmt         = "if" , "(" , Expression , ")" , Statement ,
                 [ "else" , Statement ] ;
WhileStmt      = "while" , "(" , Expression , ")" , Statement ;
ForStmt        = "for" , "(" , ( VarDecl | ExprStmt | ";" ) ,
                 [ Expression ] , ";" , [ Expression ] , ")" , Statement ;
ReturnStmt     = "return" , [ Expression ] , ";" ;
ExprStmt       = Expression , ";" ;
```
The "dangling else" ambiguity is resolved by binding else to the nearest preceding if.

## 3. Expressions
Expressions are listed from lowest to highest precedence.

```ebnf

Expression     = Assignment ;
Assignment     = LogicalOr , [ AssignOp , Assignment ] ;
AssignOp       = "=" | "+=" | "-=" | "*=" | "/=" | "%=" ;

LogicalOr      = LogicalAnd , { "||" , LogicalAnd } ;
LogicalAnd     = Equality   , { "&&" , Equality   } ;
Equality       = Relational , { ( "==" | "!=" ) , Relational } ;
Relational     = Additive   , { ( "<" | "<=" | ">" | ">=" ) , Additive } ;
Additive       = Multiplicative , { ( "+" | "-" ) , Multiplicative } ;
Multiplicative = Unary , { ( "*" | "/" | "%" ) , Unary } ;
Unary          = [ "-" | "!" ] , Call ;
Call           = Primary , { "(" , [ Arguments ] , ")" } ;
Arguments      = Expression , { "," , Expression } ;
Primary        = Literal
               | Identifier
               | "(" , Expression , ")" ;
```

## 4. Types and literals
```ebnf

Type           = "int" | "float" | "bool" | "void" | Identifier ;
Literal        = IntegerLiteral | FloatLiteral | StringLiteral
               | "true" | "false" ;
```
## 5. Precedence and associativity
|Precedence|	Operators|	Associativity|
|---|---|---|
|1 (high)|	() (call), () (grouping)|	left|
|2|	unary -, !|	right|
|3|	* / %|	left|
|4|	+ -|	left|
|5|	< <= > >=|	non-associative|
|6|	== !=|	non-associative|
|7|	&&|	left|
|8|	`|	
|9 (low)|	= += -= *= /= %=|	right|
## 6. Terminals
The terminals of the grammar correspond directly to token types produced by the lexer (Sprint 1):
keywords, identifiers, literals, operators, delimiters, and END_OF_FILE.

```text
---

# 9) Обновлённый `src/main.py`

```python
from __future__ import annotations

import argparse
import sys

from src.lexer.formatter import format_error, format_tokens
from src.lexer.scanner import scan_all
from src.parser.dot_printer import DotPrinter
from src.parser.json_printer import ast_to_json
from src.parser.parser import Parser
from src.parser.pretty_printer import PrettyPrinter
from src.utils.files import read_text, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="compiler", description="MiniCompiler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lex_parser = subparsers.add_parser("lex", help="Tokenize a source file")
    lex_parser.add_argument("--input", required=True)
    lex_parser.add_argument("--output")

    parse_parser = subparsers.add_parser("parse", help="Parse a source file into AST")
    parse_parser.add_argument("--input", required=True)
    parse_parser.add_argument("--output")
    parse_parser.add_argument(
        "--ast-format",
        choices=["text", "dot", "json"],
        default="text",
        help="AST output format",
    )
    parse_parser.add_argument("--verbose", action="store_true")

    return parser


def run_lex(args: argparse.Namespace) -> int:
    source = read_text(args.input)
    tokens, errors = scan_all(source)
    output = format_tokens(tokens)
    if args.output:
        write_text(args.output, output + ("\n" if output else ""))
    else:
        print(output)
    if errors:
        for err in errors:
            print(format_error(err), file=sys.stderr)
        return 1
    return 0


def run_parse(args: argparse.Namespace) -> int:
    source = read_text(args.input)
    tokens, lex_errors = scan_all(source)

    if lex_errors:
        for err in lex_errors:
            print(format_error(err), file=sys.stderr)
        return 1

    parser_obj = Parser(tokens)
    ast = parser_obj.parse()

    if args.verbose:
        print(f"Parsed {len(tokens)} tokens", file=sys.stderr)
        print(f"AST has {len(ast.declarations)} top-level declarations", file=sys.stderr)

    if args.ast_format == "text":
        output = PrettyPrinter().print(ast)
    elif args.ast_format == "dot":
        output = DotPrinter().print(ast)
    else:
        output = ast_to_json(ast) + "\n"

    if args.output:
        write_text(args.output, output)
    else:
        print(output, end="")

    if parser_obj.errors:
        for err in parser_obj.errors:
            print(str(err), file=sys.stderr)
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "lex":
        return run_lex(args)
    if args.command == "parse":
        return run_parse(args)
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```