from __future__ import annotations

from collections.abc import Sequence

from .token import LexError, Token


def _escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def format_token(token: Token) -> str:
    literal_part = ""
    if token.literal_value is not None:
        value = token.literal_value
        if isinstance(value, bool):
            literal_part = f" {'true' if value else 'false'}"
        elif isinstance(value, str):
            literal_part = f' "{_escape_text(value)}"'
        else:
            literal_part = f" {value}"

    return (
        f'{token.line}:{token.column} '
        f'{token.token_type.value} '
        f'"{_escape_text(token.lexeme)}"{literal_part}'
    )


def format_tokens(tokens: Sequence[Token]) -> str:
    return "\n".join(format_token(token) for token in tokens)


def format_error(error: LexError) -> str:
    return f"ERROR {error.line}:{error.column} {error.message}"


def format_errors(errors: Sequence[LexError]) -> str:
    return "\n".join(format_error(error) for error in errors)