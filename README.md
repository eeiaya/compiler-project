# MiniCompiler

MiniCompiler is a course project for the Compilers subject.

- **Sprint 1**: project foundation and lexical analyzer.
- **Sprint 2**: formal grammar and parser building an AST.

## Supported Platforms
- Linux
- macOS
- Windows

## Build / Install

```bash
python -m pip install -e .
```
## Usage
### Lexer
```Bash
compiler lex --input examples/hello.src --output tokens.txt
```
### Parser
Pretty-print AST as text:

```Bash
compiler parse --input examples/factorial.src --output ast.txt
```
Generate Graphviz DOT file:

```Bash
compiler parse --input examples/factorial.src --ast-format dot --output ast.dot
dot -Tpng ast.dot -o ast.png
```
Output AST as JSON:

```Bash
compiler parse --input examples/factorial.src --ast-format json --output ast.json
```
Verbose mode:

```Bash
compiler parse --input examples/factorial.src --verbose
```
## Example AST output (text format)
```text
Program [line 1]:
  FunctionDecl: main -> void [line 1]:
    Parameters: []
    Body:
      Block [line 1]:
        VarDecl: int n = 5 [line 2]
        VarDecl: int result = 1 [line 3]
        While [line 4]:
          Condition: (n > 0)
          Body:
            Block [line 4]:
              ExprStmt: (result = (result * n)) [line 5]
              ExprStmt: (n = (n - 1)) [line 6]
        Return [line 8]
```
### Specifications
* Lexical specification: docs/language_spec.md
* Grammar specification: docs/grammar.md
* Grammar source file: src/parser/grammar.txt
## Running Tests
```Bash
python tests/test_runner/run_tests.py
```
This runs:

* Lexer fixture tests (tests/lexer/)
* Parser fixture tests (tests/parser/)
* Unit tests for both modules