"""
Equality Checking Module
Determines if two expressions are equivalent based on polynomial normalization.
"""

from ast import ASTNode
from polynomial import normalize_expression, Polynomial, is_expandable


def are_equivalent(expr1: ASTNode, expr2: ASTNode) -> bool:
    """
    Check if two expressions are equivalent.
    
    Two expressions are equivalent if:
    1. They normalize to the same polynomial form (for expandable parts)
    2. Non-expandable subexpressions are identical
    
    Returns:
        True if expressions are equivalent, False otherwise
    """
    try:
        poly1 = normalize_expression(expr1)
        poly2 = normalize_expression(expr2)
        
        # Compare normalized polynomials
        return poly1 == poly2
    except Exception as e:
        print(f"Error during equivalence checking: {e}")
        return False


def check_equivalence_verbose(expr1: ASTNode, expr2: ASTNode) -> tuple:
    """
    Check equivalence and return detailed information.
    
    Returns:
        (is_equivalent: bool, poly1: Polynomial, poly2: Polynomial)
    """
    try:
        poly1 = normalize_expression(expr1)
        poly2 = normalize_expression(expr2)
        
        is_equiv = poly1 == poly2
        
        return is_equiv, poly1, poly2
    except Exception as e:
        print(f"Error during equivalence checking: {e}")
        return False, None, None
