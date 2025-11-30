"""
AST (Abstract Syntax Tree) Module
Defines all node types for representing mathematical expressions.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def __repr__(self) -> str:
        pass


class Number(ASTNode):
    """Represents a numeric constant (integer)."""
    
    def __init__(self, value: int):
        self.value = value
    
    def __repr__(self) -> str:
        return f"Number({self.value})"
    
    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value
    
    def __hash__(self):
        return hash(('Number', self.value))


class Variable(ASTNode):
    """Represents a single-letter variable (x, y, z, etc.)."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self) -> str:
        return f"Variable({self.name})"
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self):
        return hash(('Variable', self.name))


class BinOp(ASTNode):
    """Represents a binary operation (e.g., a + b, a * b, a ^ b)."""
    
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op  # '+', '-', '*', '/', '^'
        self.right = right
    
    def __repr__(self) -> str:
        return f"BinOp({self.left!r}, '{self.op}', {self.right!r})"
    
    def __eq__(self, other):
        return (isinstance(other, BinOp) and 
                self.left == other.left and 
                self.op == other.op and 
                self.right == other.right)


class UnaryOp(ASTNode):
    """Represents a unary operation (e.g., -x)."""
    
    def __init__(self, op: str, operand: ASTNode):
        self.op = op  # '-' (unary minus)
        self.operand = operand
    
    def __repr__(self) -> str:
        return f"UnaryOp('{self.op}', {self.operand!r})"
    
    def __eq__(self, other):
        return (isinstance(other, UnaryOp) and 
                self.op == other.op and 
                self.operand == other.operand)


class FunctionCall(ASTNode):
    """Represents a function call (sin, cos, tan, ln, sqrt)."""
    
    def __init__(self, func_name: str, arg: ASTNode):
        self.func_name = func_name  # 'sin', 'cos', 'tan', 'ln', 'sqrt'
        self.arg = arg
    
    def __repr__(self) -> str:
        return f"FunctionCall('{self.func_name}', {self.arg!r})"
    
    def __eq__(self, other):
        return (isinstance(other, FunctionCall) and 
                self.func_name == other.func_name and 
                self.arg == other.arg)


def print_ast(node: ASTNode, indent: int = 0) -> None:
    """Pretty print the AST structure."""
    prefix = "  " * indent
    
    if isinstance(node, Number):
        print(f"{prefix}Number: {node.value}")
    elif isinstance(node, Variable):
        print(f"{prefix}Variable: {node.name}")
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp: {node.op}")
        print(f"{prefix}  Left:")
        print_ast(node.left, indent + 2)
        print(f"{prefix}  Right:")
        print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp: {node.op}")
        print(f"{prefix}  Operand:")
        print_ast(node.operand, indent + 2)
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall: {node.func_name}")
        print(f"{prefix}  Argument:")
        print_ast(node.arg, indent + 2)
