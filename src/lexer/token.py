from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

LiteralValue = int | float | str | bool | None


class TokenType(str, Enum):
    KW_IF = "KW_IF"
    KW_ELSE = "KW_ELSE"
    KW_WHILE = "KW_WHILE"
    KW_FOR = "KW_FOR"
    KW_INT = "KW_INT"
    KW_FLOAT = "KW_FLOAT"
    KW_BOOL = "KW_BOOL"
    KW_RETURN = "KW_RETURN"
    KW_TRUE = "KW_TRUE"
    KW_FALSE = "KW_FALSE"
    KW_VOID = "KW_VOID"
    KW_STRUCT = "KW_STRUCT"
    KW_FN = "KW_FN"

    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"

    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"

    ASSIGN = "ASSIGN"
    PLUS_EQUAL = "PLUS_EQUAL"
    MINUS_EQUAL = "MINUS_EQUAL"
    STAR_EQUAL = "STAR_EQUAL"
    SLASH_EQUAL = "SLASH_EQUAL"
    PERCENT_EQUAL = "PERCENT_EQUAL"

    EQUAL_EQUAL = "EQUAL_EQUAL"
    BANG_EQUAL = "BANG_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"

    AND_AND = "AND_AND"
    OR_OR = "OR_OR"
    BANG = "BANG"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"

    END_OF_FILE = "END_OF_FILE"


@dataclass(frozen=True, slots=True)
class Token:
    token_type: TokenType
    lexeme: str
    line: int
    column: int
    literal_value: LiteralValue = None


@dataclass(frozen=True, slots=True)
class LexError:
    line: int
    column: int
    message: str