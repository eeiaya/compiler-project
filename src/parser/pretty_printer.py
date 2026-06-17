from __future__ import annotations

from io import StringIO

from .ast import (
    ASTNode,
    AssignmentExprNode,
    BinaryExprNode,
    BlockStmtNode,
    CallExprNode,
    ExprStmtNode,
    ForStmtNode,
    FunctionDeclNode,
    IdentifierExprNode,
    IfStmtNode,
    LiteralExprNode,
    ParamNode,
    ProgramNode,
    ReturnStmtNode,
    StructDeclNode,
    UnaryExprNode,
    VarDeclStmtNode,
    WhileStmtNode,
)


class PrettyPrinter:
    def __init__(self) -> None:
        self.buffer = StringIO()
        self.indent_level = 0

    def print(self, node: ASTNode) -> str:
        self.buffer = StringIO()
        self.indent_level = 0
        self._write_node(node)
        return self.buffer.getvalue().rstrip() + "\n"

    # ── helpers ────────────────────────────────────────────────

    def _emit(self, text: str) -> None:
        self.buffer.write("  " * self.indent_level)
        self.buffer.write(text)
        self.buffer.write("\n")

    def _loc(self, node: ASTNode) -> str:
        return f"[line {node.line}]"

    # ── dispatch ───────────────────────────────────────────────

    def _write_node(self, node: ASTNode) -> None:
        method = getattr(self, f"_write_{type(node).__name__}", None)
        if method is None:
            self._emit(f"{type(node).__name__} {self._loc(node)}")
            return
        method(node)

    # ── program & declarations ─────────────────────────────────

    def _write_ProgramNode(self, node: ProgramNode) -> None:
        self._emit(f"Program {self._loc(node)}:")
        self.indent_level += 1
        for decl in node.declarations:
            self._write_node(decl)
        self.indent_level -= 1

    def _write_FunctionDeclNode(self, node: FunctionDeclNode) -> None:
        self._emit(
            f"FunctionDecl: {node.name} -> {node.return_type} {self._loc(node)}:"
        )
        self.indent_level += 1
        params_str = ", ".join(f"{p.param_type} {p.name}" for p in node.parameters)
        self._emit(f"Parameters: [{params_str}]")
        self._emit("Body:")
        self.indent_level += 1
        self._write_node(node.body)
        self.indent_level -= 1
        self.indent_level -= 1

    def _write_StructDeclNode(self, node: StructDeclNode) -> None:
        self._emit(f"StructDecl: {node.name} {self._loc(node)}:")
        self.indent_level += 1
        for field_node in node.fields:
            self._write_node(field_node)
        self.indent_level -= 1

    # ── statements ─────────────────────────────────────────────

    def _write_BlockStmtNode(self, node: BlockStmtNode) -> None:
        self._emit(f"Block {self._loc(node)}:")
        self.indent_level += 1
        if not node.statements:
            self._emit("(empty)")
        for stmt in node.statements:
            self._write_node(stmt)
        self.indent_level -= 1

    def _write_VarDeclStmtNode(self, node: VarDeclStmtNode) -> None:
        if node.initializer is None:
            self._emit(f"VarDecl: {node.var_type} {node.name} {self._loc(node)}")
            return
        init_str = self._expr_string(node.initializer)
        self._emit(
            f"VarDecl: {node.var_type} {node.name} = {init_str} {self._loc(node)}"
        )

    def _write_ExprStmtNode(self, node: ExprStmtNode) -> None:
        self._emit(
            f"ExprStmt: {self._expr_string(node.expression)} {self._loc(node)}"
        )

    def _write_IfStmtNode(self, node: IfStmtNode) -> None:
        self._emit(f"If {self._loc(node)}:")
        self.indent_level += 1
        self._emit(f"Condition: {self._expr_string(node.condition)}")
        self._emit("Then:")
        self.indent_level += 1
        self._write_node(node.then_branch)
        self.indent_level -= 1
        if node.else_branch is not None:
            self._emit("Else:")
            self.indent_level += 1
            self._write_node(node.else_branch)
            self.indent_level -= 1
        self.indent_level -= 1

    def _write_WhileStmtNode(self, node: WhileStmtNode) -> None:
        self._emit(f"While {self._loc(node)}:")
        self.indent_level += 1
        self._emit(f"Condition: {self._expr_string(node.condition)}")
        self._emit("Body:")
        self.indent_level += 1
        self._write_node(node.body)
        self.indent_level -= 1
        self.indent_level -= 1

    def _write_ForStmtNode(self, node: ForStmtNode) -> None:
        self._emit(f"For {self._loc(node)}:")
        self.indent_level += 1
        if node.initializer is not None:
            self._emit("Init:")
            self.indent_level += 1
            self._write_node(node.initializer)
            self.indent_level -= 1
        else:
            self._emit("Init: (none)")

        cond_str = self._expr_string(node.condition) if node.condition else "(none)"
        self._emit(f"Condition: {cond_str}")

        upd_str = self._expr_string(node.update) if node.update else "(none)"
        self._emit(f"Update: {upd_str}")

        self._emit("Body:")
        self.indent_level += 1
        self._write_node(node.body)
        self.indent_level -= 1
        self.indent_level -= 1

    def _write_ReturnStmtNode(self, node: ReturnStmtNode) -> None:
        if node.value is None:
            self._emit(f"Return {self._loc(node)}")
        else:
            self._emit(f"Return: {self._expr_string(node.value)} {self._loc(node)}")

    # ── expression rendering ───────────────────────────────────

    def _expr_string(self, node: ASTNode) -> str:
        if isinstance(node, LiteralExprNode):
            if node.literal_type == "string":
                return f'"{node.value}"'
            if node.literal_type == "bool":
                return "true" if node.value else "false"
            return str(node.value)
        if isinstance(node, IdentifierExprNode):
            return node.name
        if isinstance(node, BinaryExprNode):
            return (
                f"({self._expr_string(node.left)} "
                f"{node.operator} "
                f"{self._expr_string(node.right)})"
            )
        if isinstance(node, UnaryExprNode):
            return f"({node.operator}{self._expr_string(node.operand)})"
        if isinstance(node, AssignmentExprNode):
            return (
                f"({self._expr_string(node.target)} "
                f"{node.operator} "
                f"{self._expr_string(node.value)})"
            )
        if isinstance(node, CallExprNode):
            args = ", ".join(self._expr_string(a) for a in node.arguments)
            return f"{self._expr_string(node.callee)}({args})"
        return f"<{type(node).__name__}>"