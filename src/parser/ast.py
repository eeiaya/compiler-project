from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Base classes ───────────────────────────────────────────────

@dataclass
class ASTNode:
    line: int = 0
    column: int = 0

    def accept(self, visitor: Any) -> Any:
        method_name = f"visit_{type(self).__name__}"
        visit = getattr(visitor, method_name, None)
        if visit is None:
            return visitor.generic_visit(self)
        return visit(self)


@dataclass
class ExpressionNode(ASTNode):
    pass


@dataclass
class StatementNode(ASTNode):
    pass


@dataclass
class DeclarationNode(ASTNode):
    pass


# ── Expression nodes ───────────────────────────────────────────

@dataclass
class LiteralExprNode(ExpressionNode):
    value: Any = None
    literal_type: str = ""  # "int" | "float" | "bool" | "string"


@dataclass
class IdentifierExprNode(ExpressionNode):
    name: str = ""


@dataclass
class BinaryExprNode(ExpressionNode):
    left: ExpressionNode = None
    operator: str = ""
    right: ExpressionNode = None


@dataclass
class UnaryExprNode(ExpressionNode):
    operator: str = ""
    operand: ExpressionNode = None


@dataclass
class CallExprNode(ExpressionNode):
    callee: ExpressionNode = None
    arguments: list[ExpressionNode] = field(default_factory=list)


@dataclass
class AssignmentExprNode(ExpressionNode):
    target: ExpressionNode = None
    operator: str = ""
    value: ExpressionNode = None


# ── Statement nodes ────────────────────────────────────────────

@dataclass
class BlockStmtNode(StatementNode):
    statements: list[StatementNode] = field(default_factory=list)


@dataclass
class ExprStmtNode(StatementNode):
    expression: ExpressionNode = None


@dataclass
class IfStmtNode(StatementNode):
    condition: ExpressionNode = None
    then_branch: StatementNode = None
    else_branch: StatementNode | None = None


@dataclass
class WhileStmtNode(StatementNode):
    condition: ExpressionNode = None
    body: StatementNode = None


@dataclass
class ForStmtNode(StatementNode):
    initializer: StatementNode | None = None
    condition: ExpressionNode | None = None
    update: ExpressionNode | None = None
    body: StatementNode = None


@dataclass
class ReturnStmtNode(StatementNode):
    value: ExpressionNode | None = None


@dataclass
class VarDeclStmtNode(StatementNode):
    var_type: str = ""
    name: str = ""
    initializer: ExpressionNode | None = None


# ── Declaration nodes ──────────────────────────────────────────

@dataclass
class ParamNode(ASTNode):
    param_type: str = ""
    name: str = ""


@dataclass
class FunctionDeclNode(DeclarationNode):
    return_type: str = "void"
    name: str = ""
    parameters: list[ParamNode] = field(default_factory=list)
    body: BlockStmtNode = None


@dataclass
class StructDeclNode(DeclarationNode):
    name: str = ""
    fields: list[VarDeclStmtNode] = field(default_factory=list)


# ── Root ───────────────────────────────────────────────────────

@dataclass
class ProgramNode(ASTNode):
    declarations: list[DeclarationNode] = field(default_factory=list)


# ── Visitor base ───────────────────────────────────────────────

class ASTVisitor:
    def generic_visit(self, node: ASTNode) -> Any:
        raise NotImplementedError(
            f"No visit_{type(node).__name__} method on {type(self).__name__}"
        )