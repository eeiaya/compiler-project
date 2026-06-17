from __future__ import annotations

import json
from typing import Any

from .ast import ASTNode


def ast_to_dict(node: Any) -> Any:
    if isinstance(node, ASTNode):
        result: dict[str, Any] = {"__type__": type(node).__name__}
        result["line"] = node.line
        result["column"] = node.column
        for key, value in node.__dict__.items():
            if key in ("line", "column"):
                continue
            result[key] = ast_to_dict(value)
        return result
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    return node


def ast_to_json(node: ASTNode, indent: int = 2) -> str:
    return json.dumps(ast_to_dict(node), indent=indent, ensure_ascii=False)