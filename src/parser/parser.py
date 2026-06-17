from __future__ import annotations

from src.lexer.token import Token, TokenType

from .ast import (
    AssignmentExprNode,
    BinaryExprNode,
    BlockStmtNode,
    CallExprNode,
    DeclarationNode,
    ExpressionNode,
    ExprStmtNode,
    ForStmtNode,
    FunctionDeclNode,
    IdentifierExprNode,
    IfStmtNode,
    LiteralExprNode,
    ParamNode,
    ProgramNode,
    ReturnStmtNode,
    StatementNode,
    StructDeclNode,
    UnaryExprNode,
    VarDeclStmtNode,
    WhileStmtNode,
)


class ParseError(Exception):
    def __init__(self, line: int, column: int, message: str):
        super().__init__(f"[line {line}:{column}] Parse error: {message}")
        self.line = line
        self.column = column
        self.message = message


TYPE_KEYWORDS = {
    TokenType.KW_INT: "int",
    TokenType.KW_FLOAT: "float",
    TokenType.KW_BOOL: "bool",
    TokenType.KW_VOID: "void",
}

ASSIGNMENT_OPS = {
    TokenType.ASSIGN: "=",
    TokenType.PLUS_EQUAL: "+=",
    TokenType.MINUS_EQUAL: "-=",
    TokenType.STAR_EQUAL: "*=",
    TokenType.SLASH_EQUAL: "/=",
    TokenType.PERCENT_EQUAL: "%=",
}

SYNC_TOKENS = {
    TokenType.SEMICOLON,
    TokenType.RBRACE,
    TokenType.KW_FN,
    TokenType.KW_STRUCT,
    TokenType.KW_IF,
    TokenType.KW_WHILE,
    TokenType.KW_FOR,
    TokenType.KW_RETURN,
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: list[ParseError] = []

    # ── public ─────────────────────────────────────────────────

    def parse(self) -> ProgramNode:
        program = ProgramNode(line=1, column=1)

        while not self.is_at_end():
            before = self.current
            try:
                decl = self.parse_declaration()
                if decl is not None:
                    program.declarations.append(decl)
            except ParseError as error:
                self.errors.append(error)
                self.synchronize()
                # Guarantee progress: if synchronize didn't advance, skip a token.
                if self.current == before and not self.is_at_end():
                    self.advance()

        return program

    # ── helpers ────────────────────────────────────────────────

    def peek(self, offset: int = 0) -> Token:
        index = self.current + offset
        if index >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[index]

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.END_OF_FILE

    def check(self, *types: TokenType) -> bool:
        return self.peek().token_type in types

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def advance(self) -> Token:
        token = self.peek()
        if not self.is_at_end():
            self.current += 1
        return token

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise ParseError(token.line, token.column, message)

    def synchronize(self) -> None:
        while not self.is_at_end():
            if self.peek().token_type == TokenType.SEMICOLON:
                self.advance()
                return
            if self.peek().token_type in SYNC_TOKENS:
                return
            self.advance()

    # ── declarations ───────────────────────────────────────────

    def parse_declaration(self) -> DeclarationNode | StatementNode | None:
        token = self.peek()

        if token.token_type == TokenType.KW_FN:
            return self.parse_function_declaration()
        if token.token_type == TokenType.KW_STRUCT:
            return self.parse_struct_declaration()
        if self.is_type_start():
            return self.parse_var_declaration()

        raise ParseError(
            token.line,
            token.column,
            f"Expected declaration, got '{token.lexeme}'",
        )

    def parse_function_declaration(self) -> FunctionDeclNode:
        kw = self.consume(TokenType.KW_FN, "Expected 'fn'")
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        parameters: list[ParamNode] = []
        if not self.check(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                parameters.append(self.parse_parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        return_type = "void"
        if self.match(TokenType.MINUS):
            self.consume(TokenType.GREATER, "Expected '>' in '->'")
            return_type = self.parse_type_name()

        body = self.parse_block()

        return FunctionDeclNode(
            line=kw.line,
            column=kw.column,
            return_type=return_type,
            name=name_token.lexeme,
            parameters=parameters,
            body=body,
        )

    def parse_parameter(self) -> ParamNode:
        type_token = self.peek()
        param_type = self.parse_type_name()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
        return ParamNode(
            line=type_token.line,
            column=type_token.column,
            param_type=param_type,
            name=name_token.lexeme,
        )

    def parse_struct_declaration(self) -> StructDeclNode:
        kw = self.consume(TokenType.KW_STRUCT, "Expected 'struct'")
        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name")
        self.consume(TokenType.LBRACE, "Expected '{' before struct body")

        fields: list[VarDeclStmtNode] = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            fields.append(self.parse_var_declaration())

        self.consume(TokenType.RBRACE, "Expected '}' after struct body")

        return StructDeclNode(
            line=kw.line,
            column=kw.column,
            name=name_token.lexeme,
            fields=fields,
        )

    def parse_var_declaration(self) -> VarDeclStmtNode:
        type_token = self.peek()
        var_type = self.parse_type_name()
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")

        initializer: ExpressionNode | None = None
        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")

        return VarDeclStmtNode(
            line=type_token.line,
            column=type_token.column,
            var_type=var_type,
            name=name_token.lexeme,
            initializer=initializer,
        )

    def is_type_start(self) -> bool:
        return self.peek().token_type in TYPE_KEYWORDS

    def parse_type_name(self) -> str:
        token = self.peek()
        if token.token_type in TYPE_KEYWORDS:
            self.advance()
            return TYPE_KEYWORDS[token.token_type]
        if token.token_type == TokenType.IDENTIFIER:
            self.advance()
            return token.lexeme
        raise ParseError(token.line, token.column, f"Expected type, got '{token.lexeme}'")

    # ── statements ─────────────────────────────────────────────

    def parse_statement(self) -> StatementNode:
        token = self.peek()

        if token.token_type == TokenType.LBRACE:
            return self.parse_block()
        if token.token_type == TokenType.KW_IF:
            return self.parse_if_statement()
        if token.token_type == TokenType.KW_WHILE:
            return self.parse_while_statement()
        if token.token_type == TokenType.KW_FOR:
            return self.parse_for_statement()
        if token.token_type == TokenType.KW_RETURN:
            return self.parse_return_statement()
        if self.is_type_start():
            return self.parse_var_declaration()
        if token.token_type == TokenType.SEMICOLON:
            self.advance()
            return BlockStmtNode(line=token.line, column=token.column, statements=[])

        return self.parse_expression_statement()

    def parse_block(self) -> BlockStmtNode:
        lbrace = self.consume(TokenType.LBRACE, "Expected '{'")
        statements: list[StatementNode] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            try:
                statements.append(self.parse_statement())
            except ParseError as error:
                self.errors.append(error)
                self.synchronize()

        self.consume(TokenType.RBRACE, "Expected '}'")
        return BlockStmtNode(line=lbrace.line, column=lbrace.column, statements=statements)

    def parse_if_statement(self) -> IfStmtNode:
        kw = self.consume(TokenType.KW_IF, "Expected 'if'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after if condition")

        then_branch = self.parse_statement()
        else_branch: StatementNode | None = None
        if self.match(TokenType.KW_ELSE):
            else_branch = self.parse_statement()

        return IfStmtNode(
            line=kw.line,
            column=kw.column,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def parse_while_statement(self) -> WhileStmtNode:
        kw = self.consume(TokenType.KW_WHILE, "Expected 'while'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        body = self.parse_statement()
        return WhileStmtNode(
            line=kw.line, column=kw.column, condition=condition, body=body
        )

    def parse_for_statement(self) -> ForStmtNode:
        kw = self.consume(TokenType.KW_FOR, "Expected 'for'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'for'")

        initializer: StatementNode | None = None
        if self.check(TokenType.SEMICOLON):
            self.advance()
        elif self.is_type_start():
            initializer = self.parse_var_declaration()
        else:
            initializer = self.parse_expression_statement()

        condition: ExpressionNode | None = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for condition")

        update: ExpressionNode | None = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after for clauses")

        body = self.parse_statement()
        return ForStmtNode(
            line=kw.line,
            column=kw.column,
            initializer=initializer,
            condition=condition,
            update=update,
            body=body,
        )

    def parse_return_statement(self) -> ReturnStmtNode:
        kw = self.consume(TokenType.KW_RETURN, "Expected 'return'")
        value: ExpressionNode | None = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStmtNode(line=kw.line, column=kw.column, value=value)

    def parse_expression_statement(self) -> ExprStmtNode:
        token = self.peek()
        expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmtNode(line=token.line, column=token.column, expression=expression)

    # ── expressions ────────────────────────────────────────────

    def parse_expression(self) -> ExpressionNode:
        return self.parse_assignment()

    def parse_assignment(self) -> ExpressionNode:
        left = self.parse_logical_or()

        if self.peek().token_type in ASSIGNMENT_OPS:
            op_token = self.advance()
            value = self.parse_assignment()
            return AssignmentExprNode(
                line=op_token.line,
                column=op_token.column,
                target=left,
                operator=ASSIGNMENT_OPS[op_token.token_type],
                value=value,
            )

        return left

    def parse_logical_or(self) -> ExpressionNode:
        left = self.parse_logical_and()
        while self.check(TokenType.OR_OR):
            op = self.advance()
            right = self.parse_logical_and()
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator="||", right=right,
            )
        return left

    def parse_logical_and(self) -> ExpressionNode:
        left = self.parse_equality()
        while self.check(TokenType.AND_AND):
            op = self.advance()
            right = self.parse_equality()
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator="&&", right=right,
            )
        return left

    def parse_equality(self) -> ExpressionNode:
        left = self.parse_relational()
        while self.check(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self.advance()
            right = self.parse_relational()
            op_str = "==" if op.token_type == TokenType.EQUAL_EQUAL else "!="
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator=op_str, right=right,
            )
        return left

    def parse_relational(self) -> ExpressionNode:
        left = self.parse_additive()
        rel_map = {
            TokenType.LESS: "<",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER: ">",
            TokenType.GREATER_EQUAL: ">=",
        }
        while self.peek().token_type in rel_map:
            op = self.advance()
            right = self.parse_additive()
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator=rel_map[op.token_type], right=right,
            )
        return left

    def parse_additive(self) -> ExpressionNode:
        left = self.parse_multiplicative()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_multiplicative()
            op_str = "+" if op.token_type == TokenType.PLUS else "-"
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator=op_str, right=right,
            )
        return left

    def parse_multiplicative(self) -> ExpressionNode:
        left = self.parse_unary()
        mul_map = {
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.PERCENT: "%",
        }
        while self.peek().token_type in mul_map:
            op = self.advance()
            right = self.parse_unary()
            left = BinaryExprNode(
                line=op.line, column=op.column,
                left=left, operator=mul_map[op.token_type], right=right,
            )
        return left

    def parse_unary(self) -> ExpressionNode:
        if self.check(TokenType.MINUS, TokenType.BANG):
            op = self.advance()
            operand = self.parse_unary()
            op_str = "-" if op.token_type == TokenType.MINUS else "!"
            return UnaryExprNode(
                line=op.line, column=op.column,
                operator=op_str, operand=operand,
            )
        return self.parse_call()

    def parse_call(self) -> ExpressionNode:
        expr = self.parse_primary()
        while self.check(TokenType.LPAREN):
            lparen = self.advance()
            args: list[ExpressionNode] = []
            if not self.check(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_expression())
            self.consume(TokenType.RPAREN, "Expected ')' after arguments")
            expr = CallExprNode(
                line=lparen.line, column=lparen.column,
                callee=expr, arguments=args,
            )
        return expr

    def parse_primary(self) -> ExpressionNode:
        token = self.peek()

        if token.token_type == TokenType.INT_LITERAL:
            self.advance()
            return LiteralExprNode(
                line=token.line, column=token.column,
                value=token.literal_value, literal_type="int",
            )
        if token.token_type == TokenType.FLOAT_LITERAL:
            self.advance()
            return LiteralExprNode(
                line=token.line, column=token.column,
                value=token.literal_value, literal_type="float",
            )
        if token.token_type == TokenType.STRING_LITERAL:
            self.advance()
            return LiteralExprNode(
                line=token.line, column=token.column,
                value=token.literal_value, literal_type="string",
            )
        if token.token_type in (TokenType.KW_TRUE, TokenType.KW_FALSE):
            self.advance()
            return LiteralExprNode(
                line=token.line, column=token.column,
                value=(token.token_type == TokenType.KW_TRUE),
                literal_type="bool",
            )
        if token.token_type == TokenType.IDENTIFIER:
            self.advance()
            return IdentifierExprNode(
                line=token.line, column=token.column, name=token.lexeme,
            )
        if token.token_type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        raise ParseError(
            token.line, token.column,
            f"Expected expression, got '{token.lexeme}'",
        )