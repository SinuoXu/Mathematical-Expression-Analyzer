"""
Equality Checking Module
Determines if two expressions are equivalent through symbolic simplification.
"""

from ast_nodes import ASTNode, Number, Variable, BinOp, UnaryOp, FunctionCall
from polynomial import normalize_expression, Polynomial, is_expandable
from fractions import Fraction


def simplify_to_rational(node: ASTNode) -> tuple:
    """
    Simplify an expression to a rational function form: numerator/denominator.
    Both numerator and denominator are represented as polynomials (or expressions).
    
    Returns:
        (numerator_ast, denominator_ast) where both are AST nodes
    """
    if isinstance(node, Number):
        # Constant: n/1
        return node, Number(1)
    
    elif isinstance(node, Variable):
        # Variable: x/1
        return node, Number(1)
    
    elif isinstance(node, UnaryOp):
        if node.op == '-':
            # -expr = (-numerator)/denominator
            num, den = simplify_to_rational(node.operand)
            return UnaryOp('-', num), den
        else:
            raise ValueError(f"Unsupported unary operator: {node.op}")
    
    elif isinstance(node, BinOp):
        if node.op == '+':
            # a/b + c/d = (a*d + c*b)/(b*d)
            num1, den1 = simplify_to_rational(node.left)
            num2, den2 = simplify_to_rational(node.right)
            
            # numerator = num1*den2 + num2*den1
            new_num = BinOp(
                BinOp(num1, '*', den2),
                '+',
                BinOp(num2, '*', den1)
            )
            # denominator = den1*den2
            new_den = BinOp(den1, '*', den2)
            
            return new_num, new_den
        
        elif node.op == '-':
            # a/b - c/d = (a*d - c*b)/(b*d)
            num1, den1 = simplify_to_rational(node.left)
            num2, den2 = simplify_to_rational(node.right)
            
            # numerator = num1*den2 - num2*den1
            new_num = BinOp(
                BinOp(num1, '*', den2),
                '-',
                BinOp(num2, '*', den1)
            )
            # denominator = den1*den2
            new_den = BinOp(den1, '*', den2)
            
            return new_num, new_den
        
        elif node.op == '*':
            # (a/b) * (c/d) = (a*c)/(b*d)
            num1, den1 = simplify_to_rational(node.left)
            num2, den2 = simplify_to_rational(node.right)
            
            new_num = BinOp(num1, '*', num2)
            new_den = BinOp(den1, '*', den2)
            
            return new_num, new_den
        
        elif node.op == '/':
            # (a/b) / (c/d) = (a*d)/(b*c)
            num1, den1 = simplify_to_rational(node.left)
            num2, den2 = simplify_to_rational(node.right)
            
            new_num = BinOp(num1, '*', den2)
            new_den = BinOp(den1, '*', num2)
            
            return new_num, new_den
        
        elif node.op == '^':
            # For now, treat power as atomic (can't simplify further)
            return node, Number(1)
        
        else:
            raise ValueError(f"Unsupported binary operator: {node.op}")
    
    elif isinstance(node, FunctionCall):
        # Functions are atomic
        return node, Number(1)
    
    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")


def expand_and_normalize(node: ASTNode) -> Polynomial:
    """
    Expand and normalize an expression to polynomial form.
    This handles multiplication and addition/subtraction.
    """
    try:
        return normalize_expression(node)
    except Exception:
        # If normalization fails, return as-is
        return None


def ast_equal(node1: ASTNode, node2: ASTNode) -> bool:
    """
    Check if two AST nodes are structurally equal, considering commutativity.
    This is used for comparing function arguments and other subexpressions.
    """
    # Try polynomial normalization first
    try:
        poly1 = normalize_expression(node1)
        poly2 = normalize_expression(node2)
        if poly1 == poly2:
            return True
    except Exception:
        pass
    
    # Check structural equality
    if type(node1) != type(node2):
        return False
    
    if isinstance(node1, Number):
        return node1.value == node2.value
    
    elif isinstance(node1, Variable):
        return node1.name == node2.name
    
    elif isinstance(node1, UnaryOp):
        return node1.op == node2.op and ast_equal(node1.operand, node2.operand)
    
    elif isinstance(node1, BinOp):
        if node1.op != node2.op:
            return False
        
        # Check direct equality
        if ast_equal(node1.left, node2.left) and ast_equal(node1.right, node2.right):
            return True
        
        # Check commutative equality for +, *
        if node1.op in ('+', '*'):
            if ast_equal(node1.left, node2.right) and ast_equal(node1.right, node2.left):
                return True
        
        return False
    
    elif isinstance(node1, FunctionCall):
        return (node1.func_name == node2.func_name and 
                ast_equal(node1.arg, node2.arg))
    
    return False


def are_equivalent(expr1: ASTNode, expr2: ASTNode) -> bool:
    """
    Check if two expressions are equivalent through symbolic simplification.
    
    Strategy:
    1. Try direct polynomial normalization (for simple expandable expressions)
    2. Check structural equality with commutativity (for functions)
    3. Convert both to rational form (numerator/denominator)
    4. Cross-multiply and compare: a/b = c/d iff a*d = b*c
    
    Args:
        expr1: First expression AST
        expr2: Second expression AST
    
    Returns:
        True if expressions are provably equivalent, False otherwise
    """
    # Strategy 1: Try polynomial normalization (fast for simple cases)
    try:
        poly1 = normalize_expression(expr1)
        poly2 = normalize_expression(expr2)
        
        if poly1 == poly2:
            return True
    except Exception:
        pass
    
    # Strategy 2: Check structural equality (handles functions with equivalent arguments)
    if ast_equal(expr1, expr2):
        return True
    
    # Strategy 3: Rational form comparison
    try:
        # Convert both expressions to rational form
        num1, den1 = simplify_to_rational(expr1)
        num2, den2 = simplify_to_rational(expr2)
        
        # a/b = c/d iff a*d = b*c
        # So we need to check if num1*den2 = num2*den1
        
        left_side = BinOp(num1, '*', den2)
        right_side = BinOp(num2, '*', den1)
        
        # Try to normalize both sides
        try:
            left_poly = normalize_expression(left_side)
            right_poly = normalize_expression(right_side)
            
            return left_poly == right_poly
        except Exception:
            # If normalization fails, we can't prove equivalence
            return False
    
    except Exception:
        return False


def check_equivalence_verbose(expr1: ASTNode, expr2: ASTNode) -> tuple:
    """
    Check equivalence and return detailed information.
    
    Returns:
        (is_equivalent: bool, method: str, details: str)
    """
    # Try polynomial normalization first
    try:
        poly1 = normalize_expression(expr1)
        poly2 = normalize_expression(expr2)
        
        if poly1 == poly2:
            return True, "polynomial", f"{poly1} = {poly2}"
    except Exception:
        pass
    
    # Try structural equality (for functions with equivalent arguments)
    if ast_equal(expr1, expr2):
        return True, "structural", "Structurally equivalent (considering commutativity)"
    
    # Try rational form comparison
    try:
        num1, den1 = simplify_to_rational(expr1)
        num2, den2 = simplify_to_rational(expr2)
        
        # Cross multiply: a/b = c/d iff a*d = b*c
        left_side = BinOp(num1, '*', den2)
        right_side = BinOp(num2, '*', den1)
        
        try:
            left_poly = normalize_expression(left_side)
            right_poly = normalize_expression(right_side)
            
            if left_poly == right_poly:
                return True, "rational", f"Cross-multiplication: {left_poly} = {right_poly}"
            else:
                return False, "rational", f"Cross-multiplication differs: {left_poly} ≠ {right_poly}"
        except Exception as e:
            return False, "rational", f"Could not normalize: {e}"
    
    except Exception as e:
        return False, "error", str(e)
