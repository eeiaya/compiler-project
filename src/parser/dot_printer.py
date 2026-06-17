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


NODE_COLORS = {
    "ProgramNode": "lightblue",
    "FunctionDeclNode": "lightgreen",
    "StructDeclNode": "lightgreen",
    "BlockStmtNode": "lightyellow",
    "IfStmtNode": "khaki",
    "WhileStmtNode": "khaki",
    "ForStmtNode": "khaki",
    "ReturnStmtNode": "khaki",
    "VarDeclStmtNode": "lightcyan",
    "ExprStmtNode": "lightcyan",
    "BinaryExprNode": "mistyrose",
    "UnaryExprNode": "mistyrose",
    "AssignmentExprNode": "mistyrose",
    "CallExprNode": "mistyrose",
    "LiteralExprNode": "white",
    "IdentifierExprNode": "white",
    "ParamNode": "lavender",
}


class DotPrinter:
    def __init__(self) -> None:
        self.buffer = StringIO()
        self.counter = 0

    def print(self, node: ASTNode) -> str:
        self.buffer = StringIO()
        self.counter = 0
        self.buffer.write("digraph AST {\n")
        self.buffer.write('  node [shape=box, style=filled, fontname="Courier"];\n')
        self._emit(node)
        self.buffer.write("}\n")
        return self.buffer.getvalue()

    def _new_id(self) -> str:
        self.counter += 1
        return f"n{self.counter}"

    def _escape(self, text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"')

    def _node(self, node_id: str, label: str, type_name: str) -> None:
        color = NODE_COLORS.get(type_name, "white")
        self.buffer.write(
            f'  {node_id} [label="{self._escape(label)}", fillcolor="{color}"];\n'
        )

    def _edge(self, parent: str, child: str, label: str = "") -> None:
        if label:
            self.buffer.write(f'  {parent} -> {child} [label="{label}"];\n')
        else:
            self.buffer.write(f"  {parent} -> {child};\n")

    def _emit(self, node: ASTNode, parent: str | None = None, label: str = "") -> str:
        node_id = self._new_id()
        type_name = type(node).__name__
        text = self._label_for(node)
        self._node(node_id, text, type_name)
        if parent is not None:
            self._edge(parent, node_id, label)
        self._children(node, node_id)
        return node_id

    def _label_for(self, node: ASTNode) -> str:
        if isinstance(node, ProgramNode):
            return "Program"
        if isinstance(node, FunctionDeclNode):
            return f"FunctionDecl\\n{node.name} -> {node.return_type}"
        if isinstance(node, StructDeclNode):
            return f"StructDecl\\n{node.name}"
        if isinstance(node, ParamNode):
            return f"Param\\n{node.param_type} {node.name}"
        if isinstance(node, BlockStmtNode):
            return "Block"
        if isinstance(node, VarDeclStmtNode):
            return f"VarDecl\\n{node.var_type} {node.name}"
        if isinstance(node, ExprStmtNode):
            return "ExprStmt"
        if isinstance(node, IfStmtNode):
            return "If"
        if isinstance(node, WhileStmtNode):
            return "While"
        if isinstance(node, ForStmtNode):
            return "For"
        if isinstance(node, ReturnStmtNode):
            return "Return"
        if isinstance(node, BinaryExprNode):
            return f"Binary\\n{node.operator}"
        if isinstance(node, UnaryExprNode):
            return f"Unary\\n{node.operator}"
        if isinstance(node, AssignmentExprNode):
            return f"Assignment\\n{node.operator}"
        if isinstance(node, CallExprNode):
            return "Call"
        if isinstance(node, LiteralExprNode):
            return f"Literal ({node.literal_type})\\n{node.value}"
        if isinstance(node, IdentifierExprNode):
            return f"Identifier\\n{node.name}"
        return type(node).__name__

    def _children(self, node: ASTNode, node_id: str) -> None:
        if isinstance(node, ProgramNode):
            for decl in node.declarations:
                self._emit(decl, node_id)
        elif isinstance(node, FunctionDeclNode):
            for param in node.parameters:
                self._emit(param, node_id, "param")
            if node.body is not None:
                self._emit(node.body, node_id, "body")
        elif isinstance(node, StructDeclNode):
            for field_node in node.fields:
                self._emit(field_node, node_id, "field")
        elif isinstance(node, BlockStmtNode):
            for stmt in node.statements:
                self._emit(stmt, node_id)
        elif isinstance(node, VarDeclStmtNode):
            if node.initializer is not None:
                self._emit(node.initializer, node_id, "init")
        elif isinstance(node, ExprStmtNode):
            if node.expression is not None:
                self._emit(node.expression, node_id)
        elif isinstance(node, IfStmtNode):
            self._emit(node.condition, node_id, "cond")
            self._emit(node.then_branch, node_id, "then")
            if node.else_branch is not None:
                self._emit(node.else_branch, node_id, "else")
        elif isinstance(node, WhileStmtNode):
            self._emit(node.condition, node_id, "cond")
            self._emit(node.body, node_id, "body")
        elif isinstance(node, ForStmtNode):
            if node.initializer is not None:
                self._emit(node.initializer, node_id, "init")
            if node.condition is not None:
                self._emit(node.condition, node_id, "cond")
            if node.update is not None:
                self._emit(node.update, node_id, "update")
            self._emit(node.body, node_id, "body")
        elif isinstance(node, ReturnStmtNode):
            if node.value is not None:
                self._emit(node.value, node_id)
        elif isinstance(node, BinaryExprNode):
            self._emit(node.left, node_id, "L")
            self._emit(node.right, node_id, "R")
        elif isinstance(node, UnaryExprNode):
            self._emit(node.operand, node_id)
        elif isinstance(node, AssignmentExprNode):
            self._emit(node.target, node_id, "target")
            self._emit(node.value, node_id, "value")
        elif isinstance(node, CallExprNode):
            self._emit(node.callee, node_id, "callee")
            for arg in node.arguments:
                self._emit(arg, node_id, "arg")