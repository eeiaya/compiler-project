from __future__ import annotations

from .token import LexError, Token, TokenType

ScannerState = tuple[int, int, int]


class Scanner:
    KEYWORDS: dict[str, TokenType] = {
        "if": TokenType.KW_IF,
        "else": TokenType.KW_ELSE,
        "while": TokenType.KW_WHILE,
        "for": TokenType.KW_FOR,
        "int": TokenType.KW_INT,
        "float": TokenType.KW_FLOAT,
        "bool": TokenType.KW_BOOL,
        "return": TokenType.KW_RETURN,
        "true": TokenType.KW_TRUE,
        "false": TokenType.KW_FALSE,
        "void": TokenType.KW_VOID,
        "struct": TokenType.KW_STRUCT,
        "fn": TokenType.KW_FN,
    }

    TWO_CHAR_TOKENS: dict[str, TokenType] = {
        "==": TokenType.EQUAL_EQUAL,
        "!=": TokenType.BANG_EQUAL,
        "<=": TokenType.LESS_EQUAL,
        ">=": TokenType.GREATER_EQUAL,
        "&&": TokenType.AND_AND,
        "||": TokenType.OR_OR,
        "+=": TokenType.PLUS_EQUAL,
        "-=": TokenType.MINUS_EQUAL,
        "*=": TokenType.STAR_EQUAL,
        "/=": TokenType.SLASH_EQUAL,
        "%=": TokenType.PERCENT_EQUAL,
    }

    ONE_CHAR_TOKENS: dict[str, TokenType] = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "%": TokenType.PERCENT,
        "=": TokenType.ASSIGN,
        "<": TokenType.LESS,
        ">": TokenType.GREATER,
        "!": TokenType.BANG,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        ",": TokenType.COMMA,
        ";": TokenType.SEMICOLON,
        ".": TokenType.DOT,
    }

    def __init__(self, source: str):
        self.source = source
        self.current = 0
        self.line = 1
        self.column = 1
        self.errors: list[LexError] = []
        self._lookahead_token: Token | None = None
        self._lookahead_state: ScannerState | None = None

    def next_token(self) -> Token:
        if self._lookahead_token is not None:
            token = self._lookahead_token
            assert self._lookahead_state is not None
            self._restore_state(self._lookahead_state)
            self._lookahead_token = None
            self._lookahead_state = None
            return token

        return self._scan_token()

    def peek_token(self) -> Token:
        if self._lookahead_token is None:
            saved_state = self._snapshot_state()
            token = self._scan_token()
            self._lookahead_token = token
            self._lookahead_state = self._snapshot_state()
            self._restore_state(saved_state)

        return self._lookahead_token

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def get_line(self) -> int:
        return self.line

    def get_column(self) -> int:
        return self.column

    def _scan_token(self) -> Token:
        while True:
            self._skip_whitespace_and_comments()

            if self.is_at_end():
                return Token(TokenType.END_OF_FILE, "", self.line, self.column, None)

            start_index = self.current
            start_line = self.line
            start_column = self.column
            ch = self._peek_char()

            if self._is_ascii_letter(ch):
                token = self._scan_identifier_or_keyword(
                    start_index, start_line, start_column
                )
                if token is not None:
                    return token
                continue

            if ch.isdigit():
                token = self._scan_number(start_index, start_line, start_column)
                if token is not None:
                    return token
                continue

            if ch == '"':
                token = self._scan_string(start_index, start_line, start_column)
                if token is not None:
                    return token
                continue

            two_chars = ch + self._peek_char(1)
            if two_chars in self.TWO_CHAR_TOKENS:
                self._advance()
                self._advance()
                return Token(
                    self.TWO_CHAR_TOKENS[two_chars],
                    self.source[start_index:self.current],
                    start_line,
                    start_column,
                    None,
                )

            if ch in self.ONE_CHAR_TOKENS:
                self._advance()
                return Token(
                    self.ONE_CHAR_TOKENS[ch],
                    self.source[start_index:self.current],
                    start_line,
                    start_column,
                    None,
                )

            self._error(start_line, start_column, f"Invalid character {ch!r}")
            self._advance()

    def _scan_identifier_or_keyword(
        self, start_index: int, start_line: int, start_column: int
    ) -> Token | None:
        while self._is_identifier_part(self._peek_char()):
            self._advance()

        lexeme = self.source[start_index:self.current]

        if len(lexeme) > 255:
            self._error(
                start_line,
                start_column,
                f"Identifier exceeds maximum length of 255 characters: '{lexeme}'",
            )
            return None

        token_type = self.KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        literal_value = None

        if token_type == TokenType.KW_TRUE:
            literal_value = True
        elif token_type == TokenType.KW_FALSE:
            literal_value = False

        return Token(token_type, lexeme, start_line, start_column, literal_value)

    def _scan_number(
        self, start_index: int, start_line: int, start_column: int
    ) -> Token | None:
        while self._peek_char().isdigit():
            self._advance()

        is_float = False
        if self._peek_char() == "." and self._peek_char(1).isdigit():
            is_float = True
            self._advance()
            while self._peek_char().isdigit():
                self._advance()

        if self._peek_char() == "." and (is_float or self._peek_char(1).isdigit()):
            while self._peek_char() and (
                self._peek_char() == "."
                or self._peek_char().isdigit()
                or self._is_identifier_part(self._peek_char())
            ):
                self._advance()

            lexeme = self.source[start_index:self.current]
            self._error(start_line, start_column, f"Malformed number literal '{lexeme}'")
            return None

        if self._is_identifier_part(self._peek_char()):
            while self._peek_char() and (
                self._peek_char() == "."
                or self._peek_char().isdigit()
                or self._is_identifier_part(self._peek_char())
            ):
                self._advance()

            lexeme = self.source[start_index:self.current]
            self._error(start_line, start_column, f"Malformed number literal '{lexeme}'")
            return None

        lexeme = self.source[start_index:self.current]

        if is_float:
            value = float(lexeme)
            return Token(
                TokenType.FLOAT_LITERAL, lexeme, start_line, start_column, value
            )

        value = int(lexeme)
        if value > (2**31 - 1):
            self._error(
                start_line,
                start_column,
                f"Integer literal out of range '{lexeme}'",
            )
            return None

        return Token(TokenType.INT_LITERAL, lexeme, start_line, start_column, value)

    def _scan_string(
        self, start_index: int, start_line: int, start_column: int
    ) -> Token | None:
        self._advance()  # opening quote
        literal_chars: list[str] = []

        while not self.is_at_end():
            ch = self._peek_char()

            if ch == '"':
                self._advance()
                lexeme = self.source[start_index:self.current]
                return Token(
                    TokenType.STRING_LITERAL,
                    lexeme,
                    start_line,
                    start_column,
                    "".join(literal_chars),
                )

            if ch in ("\n", "\r"):
                self._error(start_line, start_column, "Unterminated string literal")
                return None

            if ch == "\\":
                self._advance()
                next_char = self._peek_char()

                if next_char in ("", "\n", "\r"):
                    self._error(start_line, start_column, "Unterminated string literal")
                    return None

                escaped = self._advance()
                literal_chars.append(self._decode_escape(escaped))
                continue

            literal_chars.append(self._advance())

        self._error(start_line, start_column, "Unterminated string literal")
        return None

    def _skip_whitespace_and_comments(self) -> None:
        while not self.is_at_end():
            ch = self._peek_char()

            if ch in (" ", "\t", "\n", "\r"):
                self._advance()
                continue

            if ch == "/" and self._peek_char(1) == "/":
                self._advance()
                self._advance()
                while not self.is_at_end() and self._peek_char() not in ("\n", "\r"):
                    self._advance()
                continue

            if ch == "/" and self._peek_char(1) == "*":
                self._skip_block_comment()
                continue

            break

    def _skip_block_comment(self) -> None:
        start_line = self.line
        start_column = self.column

        self._advance()  # /
        self._advance()  # *
        nesting_depth = 1

        while nesting_depth > 0 and not self.is_at_end():
            if self._peek_char() == "/" and self._peek_char(1) == "*":
                self._advance()
                self._advance()
                nesting_depth += 1
                continue

            if self._peek_char() == "*" and self._peek_char(1) == "/":
                self._advance()
                self._advance()
                nesting_depth -= 1
                continue

            self._advance()

        if nesting_depth > 0:
            self._error(start_line, start_column, "Unterminated multi-line comment")

    def _snapshot_state(self) -> ScannerState:
        return (self.current, self.line, self.column)

    def _restore_state(self, state: ScannerState) -> None:
        self.current, self.line, self.column = state

    def _peek_char(self, offset: int = 0) -> str:
        index = self.current + offset
        if index >= len(self.source):
            return ""
        return self.source[index]

    def _advance(self) -> str:
        if self.is_at_end():
            return ""

        ch = self.source[self.current]

        if ch == "\r":
            self.current += 1
            if self.current < len(self.source) and self.source[self.current] == "\n":
                self.current += 1
            self.line += 1
            self.column = 1
            return "\n"

        if ch == "\n":
            self.current += 1
            self.line += 1
            self.column = 1
            return "\n"

        self.current += 1
        self.column += 1
        return ch

    def _error(self, line: int, column: int, message: str) -> None:
        self.errors.append(LexError(line, column, message))

    @staticmethod
    def _is_ascii_letter(ch: str) -> bool:
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z")

    @classmethod
    def _is_identifier_part(cls, ch: str) -> bool:
        return cls._is_ascii_letter(ch) or ch.isdigit() or ch == "_"

    @staticmethod
    def _decode_escape(ch: str) -> str:
        escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            '"': '"',
            "\\": "\\",
        }
        return escape_map.get(ch, ch)


def scan_all(source: str) -> tuple[list[Token], list[LexError]]:
    scanner = Scanner(source)
    tokens: list[Token] = []

    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.token_type == TokenType.END_OF_FILE:
            break

    return tokens, scanner.errors