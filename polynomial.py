"""
Polynomial Normalization Module
Converts expressions containing only +, -, * operations into a canonical polynomial form.
Non-expandable subexpressions (containing /, ^, functions) are treated as atomic variables.
"""

from typing import Dict, Tuple, Set, Optional
from ast_nodes import ASTNode, Number, Variable, BinOp, UnaryOp, FunctionCall


class AtomicExpr:
    """Represents a non-expandable atomic expression."""
    
    _counter = 0
    _cache: Dict[str, 'AtomicExpr'] = {}
    
    def __init__(self, ast_node: ASTNode, expr_str: str):
        self.node = ast_node
        self.expr_str = expr_str
        self.id = AtomicExpr._counter
        AtomicExpr._counter += 1
    
    def __repr__(self) -> str:
        # Return the expression string directly without Atom() wrapper
        return self.expr_str
    
    def __str__(self) -> str:
        return self.expr_str
    
    def __eq__(self, other):
        return isinstance(other, AtomicExpr) and self.expr_str == other.expr_str
    
    def __hash__(self):
        return hash(('AtomicExpr', self.expr_str))
    
    def __lt__(self, other):
        """Enable sorting of AtomicExpr objects."""
        if isinstance(other, AtomicExpr):
            return self.expr_str < other.expr_str
        return str(self) < str(other)
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other


class Polynomial:
    """
    Represents a polynomial as a sum of monomials.
    Stored as a dictionary: {monomial: coefficient}
    where monomial is a frozenset of (variable_name, power) tuples.
    Variables can be regular variables (str) or atomic expressions.
    """
    
    def __init__(self, terms: Optional[Dict] = None):
        """
        Initialize polynomial.
        terms: dict mapping frozenset of (var, power) tuples to coefficient
        """
        self.terms: Dict[frozenset, int] = terms if terms else {}
        self._normalize()
    
    def _normalize(self):
        """Remove zero terms."""
        self.terms = {m: c for m, c in self.terms.items() if c != 0}
    
    def __repr__(self) -> str:
        if not self.terms:
            return "0"
        
        parts = []
        first = True
        for monomial, coeff in sorted(self.terms.items(), key=lambda x: str(x)):
            if coeff == 0:
                continue
            
            monomial_str = self._format_monomial(monomial, coeff)
            
            if first:
                parts.append(monomial_str)
                first = False
            else:
                # For subsequent terms, handle the sign
                if monomial_str.startswith('-'):
                    # Negative term: use - instead of + -
                    parts.append(f" - {monomial_str[1:]}")
                else:
                    # Positive term: use +
                    parts.append(f" + {monomial_str}")
        
        return "".join(parts) if parts else "0"
    
    @staticmethod
    def _format_monomial(monomial: frozenset, coeff: int) -> str:
        """Format a monomial for display with proper parentheses."""
        if not monomial:  # Constant term
            return str(coeff)
        
        # Format each variable with its power
        var_parts = []
        has_power = False
        for var, power in sorted(monomial):
            if power > 1:
                var_parts.append(f"{var}^{power}")
                has_power = True
            else:
                var_parts.append(str(var))
        
        # Join variables with *
        if len(var_parts) == 1:
            vars_str = var_parts[0]
        else:
            vars_str = "*".join(var_parts)
        
        # Format with coefficient
        if coeff == 1:
            return vars_str
        elif coeff == -1:
            return f"-{vars_str}"
        elif coeff < 0:
            # Negative coefficient: display as -abs(coeff)*vars
            abs_coeff = abs(coeff)
            return f"-{abs_coeff}*{vars_str}"
        else:
            # Positive coefficient: add parentheses only if vars contain ^ or multiple vars
            if has_power or len(var_parts) > 1:
                return f"{coeff}*({vars_str})"
            else:
                return f"{coeff}*{vars_str}"
    
    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        return self.terms == other.terms
    
    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        """Add two polynomials."""
        result = dict(self.terms)
        for monomial, coeff in other.terms.items():
            result[monomial] = result.get(monomial, 0) + coeff
        return Polynomial(result)
    
    def __sub__(self, other: 'Polynomial') -> 'Polynomial':
        """Subtract two polynomials."""
        result = dict(self.terms)
        for monomial, coeff in other.terms.items():
            result[monomial] = result.get(monomial, 0) - coeff
        return Polynomial(result)
    
    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        """Multiply two polynomials."""
        result = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                # Combine monomials
                combined = self._combine_monomials(m1, m2)
                coeff = c1 * c2
                result[combined] = result.get(combined, 0) + coeff
        return Polynomial(result)
    
    @staticmethod
    def _combine_monomials(m1: frozenset, m2: frozenset) -> frozenset:
        """Multiply two monomials."""
        # Convert to dict for easier manipulation
        vars_dict = {}
        for var, power in m1:
            vars_dict[var] = vars_dict.get(var, 0) + power
        for var, power in m2:
            vars_dict[var] = vars_dict.get(var, 0) + power
        
        return frozenset(vars_dict.items())
    
    def __neg__(self) -> 'Polynomial':
        """Negate polynomial."""
        return Polynomial({m: -c for m, c in self.terms.items()})


def is_expandable(node: ASTNode) -> bool:
    """Check if node contains only +, -, * operations."""
    if isinstance(node, (Number, Variable)):
        return True
    elif isinstance(node, UnaryOp):
        return node.op == '-' and is_expandable(node.operand)
    elif isinstance(node, BinOp):
        return node.op in ('+', '-', '*') and is_expandable(node.left) and is_expandable(node.right)
    else:
        return False


def ast_to_string(node: ASTNode, parent_op: str = None, is_right_of_power: bool = False) -> str:
    """Convert AST node to string representation with minimal parentheses."""
    if isinstance(node, Number):
        return str(node.value)
    elif isinstance(node, Variable):
        return node.name
    elif isinstance(node, BinOp):
        # For power operator (right-associative), add parentheses to right operand if it's also a power
        if node.op == '^':
            left_str = ast_to_string(node.left, node.op, False)
            right_str = ast_to_string(node.right, node.op, True)
            
            # If right operand is also a power operation, add parentheses
            if isinstance(node.right, BinOp) and node.right.op == '^':
                right_str = f"({right_str})"
            
            result = f"{left_str}^{right_str}"
        else:
            left_str = ast_to_string(node.left, node.op, False)
            right_str = ast_to_string(node.right, node.op, False)
            result = f"{left_str}{node.op}{right_str}"
        
        # Add outer parentheses only if this is a subexpression of a higher precedence operation
        if parent_op and needs_parens(node.op, parent_op):
            result = f"({result})"
        
        return result
    elif isinstance(node, UnaryOp):
        operand_str = ast_to_string(node.operand, node.op, False)
        return f"{node.op}{operand_str}"
    elif isinstance(node, FunctionCall):
        arg_str = ast_to_string(node.arg, None, False)
        return f"{node.func_name}({arg_str})"
    else:
        return str(node)


def needs_parens(op: str, parent_op: str) -> bool:
    """Check if operation needs parentheses based on parent operation."""
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    
    if op not in precedence or parent_op not in precedence:
        return False
    
    # Need parentheses if current op has lower precedence than parent
    return precedence[op] < precedence[parent_op]


def expand_to_polynomial(node: ASTNode) -> Polynomial:
    """
    Convert an expandable AST to a polynomial.
    Non-expandable subexpressions become atomic variables.
    """
    if isinstance(node, Number):
        # Constant term
        if node.value == 0:
            return Polynomial()
        return Polynomial({frozenset(): node.value})
    
    elif isinstance(node, Variable):
        # Single variable with power 1
        return Polynomial({frozenset([(node.name, 1)]): 1})
    
    elif isinstance(node, UnaryOp):
        if node.op == '-':
            return -expand_to_polynomial(node.operand)
        else:
            raise ValueError(f"Unsupported unary operator: {node.op}")
    
    elif isinstance(node, BinOp):
        if node.op == '+':
            left = expand_to_polynomial(node.left)
            right = expand_to_polynomial(node.right)
            return left + right
        
        elif node.op == '-':
            left = expand_to_polynomial(node.left)
            right = expand_to_polynomial(node.right)
            return left - right
        
        elif node.op == '*':
            left = expand_to_polynomial(node.left)
            right = expand_to_polynomial(node.right)
            return left * right
        
        elif node.op == '^':
            # Handle power: only expandable if right is constant and left is expandable
            if isinstance(node.right, Number) and node.right.value in (2, 3):
                base = expand_to_polynomial(node.left)
                result = base
                for _ in range(node.right.value - 1):
                    result = result * base
                return result
            else:
                # Non-expandable: treat as atomic
                expr_str = ast_to_string(node)
                atomic = AtomicExpr(node, expr_str)
                return Polynomial({frozenset([(atomic, 1)]): 1})
        
        elif node.op == '/':
            # Division is non-expandable: treat as atomic
            expr_str = ast_to_string(node)
            atomic = AtomicExpr(node, expr_str)
            return Polynomial({frozenset([(atomic, 1)]): 1})
        
        else:
            raise ValueError(f"Unsupported binary operator: {node.op}")
    
    elif isinstance(node, FunctionCall):
        # Functions are atomic and non-expandable
        expr_str = ast_to_string(node)
        atomic = AtomicExpr(node, expr_str)
        return Polynomial({frozenset([(atomic, 1)]): 1})
    
    else:
        raise ValueError(f"Unsupported AST node type: {type(node)}")


def normalize_expression(node: ASTNode) -> Polynomial:
    """
    Normalize an expression to polynomial form if possible.
    If the expression contains non-expandable operations, those become atomic variables.
    """
    return expand_to_polynomial(node)
