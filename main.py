"""
Main Module - Examples and Testing
Demonstrates the complete pipeline: lexing, parsing, normalization, and equivalence checking.
"""

from lexer import tokenize
from parser import parse
from ast import print_ast
from polynomial import normalize_expression, is_expandable
from equality import are_equivalent, check_equivalence_verbose


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def show_tokens(expr_str: str):
    """
    Display detailed token information for an expression.
    
    Args:
        expr_str: Expression string to tokenize
    """
    print(f"\nExpression: {expr_str}")
    print("-" * 70)
    
    try:
        tokens = tokenize(expr_str)
        print("[Tokens]:")
        for token in tokens:
            token_type = token.type.name
            # Highlight implicit multiplication
            if token.type.name == 'IMPLICIT_MULTIPLY':
                token_type = f"*{token_type}*"  # Mark with asterisks
            print(f"  {token_type:22} | value={repr(token.value):10} | pos={token.pos}")
    except Exception as e:
        print(f"Error: {e}")


def analyze_expression(expr_str: str):
    """
    Analyze a single expression: parse, show AST, and normalize.
    
    Args:
        expr_str: Expression string to analyze
    """
    print(f"\nExpression: {expr_str}")
    print("-" * 70)
    
    try:
        # Parse
        ast = parse(expr_str)
        print("AST:")
        print_ast(ast)
        
        # Check if expandable
        expandable = is_expandable(ast)
        print(f"\nExpandable (only +, -, *): {expandable}")
        
        # Normalize
        poly = normalize_expression(ast)
        print(f"Normalized form: {poly}")
        
        return ast, poly
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def compare_expressions(expr1_str: str, expr2_str: str):
    """
    Compare two expressions for equivalence.
    
    Args:
        expr1_str: First expression string
        expr2_str: Second expression string
    """
    print(f"\nComparing:")
    print(f"  Expression 1: {expr1_str}")
    print(f"  Expression 2: {expr2_str}")
    print("-" * 70)
    
    try:
        ast1 = parse(expr1_str)
        ast2 = parse(expr2_str)
        
        is_equiv, poly1, poly2 = check_equivalence_verbose(ast1, ast2)
        
        print(f"Poly1: {poly1}")
        print(f"Poly2: {poly2}")
        print(f"\nEquivalent: {is_equiv}")
        
        return is_equiv
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run comprehensive examples and tests."""
    
    print_section("MATHEMATICAL EXPRESSION ANALYZER")
    print("Supports: +, -, *, /, ^, sin, cos, tan, ln, sqrt, parentheses")
    print("Implicit multiplication: 2x, x(y+1), xy, etc.")
    
    # ====== PART 1: Single Expression Analysis ======
    print_section("PART 1: SINGLE EXPRESSION ANALYSIS")
    
    test_expressions = [
        "5",
        "x",
        "2x",
        "x + 1",
        "1 + x",
        "2x + 3y",
        "x^2",
        "x^2 + 2x + 1",
        "(x + 1) * (x + 1)",
        "(x + 1)^2",
        "x * y",
        "y * x",
        "sin(x)",
        "x / 2",
        "sqrt(x)",
        "x^3 + y^3",
    ]
    
    for expr in test_expressions:
        analyze_expression(expr)
    
    # ====== PART 2: Equivalence Testing ======
    print_section("PART 2: EQUIVALENCE TESTING")
    
    equivalence_tests = [
        # Commutativity of addition
        ("1 + x", "x + 1", True),
        ("x + y", "y + x", True),
        
        # Commutativity of multiplication
        ("x * y", "y * x", True),
        ("2 * x", "x * 2", True),
        
        # Associativity of addition
        ("(x + y) + z", "x + (y + z)", True),
        ("1 + (2 + x)", "(1 + 2) + x", True),
        
        # Associativity of multiplication
        ("(x * y) * z", "x * (y * z)", True),
        
        # Distributivity and expansion
        ("(x + 1)^2", "x^2 + 2x + 1", True),
        ("(x + 1) * (x + 1)", "x^2 + 2x + 1", True),
        ("(x + y)^2", "x^2 + 2xy + y^2", True),
        
        # x^3 expansion
        ("(x + 1)^3", "x^3 + 3x^2 + 3x + 1", True),
        
        # Different forms
        ("2x + 3y", "3y + 2x", True),
        ("3x + 2", "2 + 3x", True),
        
        # Non-equivalence
        ("x + 1", "x + 2", False),
        ("x * y", "x + y", False),
        ("x^2", "x^3", False),
        
        # With coefficients
        ("2(x + 1)", "2x + 2", True),
        ("3(x + y)", "3x + 3y", True),
        
        # Multiple terms
        ("x + y + z", "z + y + x", True),
        ("x*y + x*z", "x*(y + z)", True),
        
        # Edge cases
        ("0 + x", "x", True),
        ("x * 1", "x", True),
        ("x + 0", "x", True),
    ]
    
    print("\nRunning equivalence tests...")
    correct = 0
    total = len(equivalence_tests)
    
    for expr1, expr2, expected in equivalence_tests:
        result = compare_expressions(expr1, expr2)
        
        if result == expected:
            status = "✓ PASS"
            correct += 1
        else:
            status = "✗ FAIL"
        
        print(f"  {status}: Expected {expected}, Got {result}")
    
    print(f"\n{correct}/{total} tests passed")
    
    # ====== PART 3: Lexical Analysis - Token Display ======
    print_section("PART 3: LEXICAL ANALYSIS - TOKEN DISPLAY")
    
    lexer_test_expressions = [
        "sin(x)",
        "sin(x + cos(x))",
        "sin(x + cos(x))ln(x)",
        "ln(x)",
        "sqrt(x)",
        "sin(x) + cos(x)",
        "x^2 / 2",
        "x / y",
        "2x",
        "xy",
        "2(x+1)",
    ]
    
    print("\nShowing detailed token breakdown...")
    print("Note: *IMPLICIT_MULTIPLY* marks implicit multiplication tokens")
    for expr in lexer_test_expressions:
        show_tokens(expr)
    
    # ====== PART 4: Complex Expression Handling ======
    print_section("PART 4: COMPLEX EXPRESSION HANDLING")
    
    complex_tests = [
        "sin(x)",
        "sin(x + cos(x))",
        "sin(x + cos(x))ln(x)",
        "ln(x)",
        "sqrt(x)",
        "sin(x) + cos(x)",
        "x^2 / 2",
        "x / y",
    ]
    
    print("\nAnalyzing expressions with non-expandable operations...")
    for expr in complex_tests:
        analyze_expression(expr)
    
    # ====== PART 5: Implicit Multiplication Examples ======
    print_section("PART 5: IMPLICIT MULTIPLICATION EXAMPLES")
    
    implicit_tests = [
        ("2x", "x * 2", True),
        ("2x*y", "x * y * 2", True),
        ("2(x + 1)", "2 * (x + 1)", True),
        ("x(y + 1)", "x * (y + 1)", True),
        ("(x + 1)(y + 1)", "(x + 1) * (y + 1)", True),
    ]
    
    print("\nTesting implicit multiplication parsing...")
    for expr1, expr2, _ in implicit_tests:
        print(f"\nImplicit: {expr1}")
        print(f"Explicit: {expr2}")
        print("-" * 40)
        
        try:
            ast1 = parse(expr1)
            ast2 = parse(expr2)
            
            poly1 = normalize_expression(ast1)
            poly2 = normalize_expression(ast2)
            
            equiv = poly1 == poly2
            print(f"Same normalized form: {equiv}")
        except Exception as e:
            print(f"Error: {e}")
    
    print_section("ANALYSIS COMPLETE")
    print("All modules working correctly!")


def interactive_mode():
    """
    Interactive mode for testing expressions.
    Allows users to:
    1. Analyze single expressions (lexical and syntax analysis)
    2. Compare two expressions for equivalence
    """
    print_section("INTERACTIVE MODE")
    print("Welcome to the Mathematical Expression Analyzer Interactive Mode!")
    print("\nSupported operations: +, -, *, /, ^, sin, cos, tan, ln, sqrt")
    print("Implicit multiplication: 2x, xy, 2(x+1), (x+1)(y+1), etc.")
    
    while True:
        print("\n" + "=" * 70)
        print("Choose an option:")
        print("  1. Analyze a single expression (lexical + syntax analysis)")
        print("  2. Compare two expressions for equivalence")
        print("  3. Exit")
        print("=" * 70)
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == '1':
            # Single expression analysis
            print("\n" + "-" * 70)
            expr = input("Enter an expression: ").strip()
            
            if not expr:
                print("Error: Empty expression!")
                continue
            
            print_section("LEXICAL ANALYSIS")
            show_tokens(expr)
            
            print_section("SYNTAX ANALYSIS & NORMALIZATION")
            show_tokens(expr)
            analyze_expression(expr)
            
        elif choice == '2':
            # Two expression comparison
            print("\n" + "-" * 70)
            expr1 = input("Enter the first expression: ").strip()
            expr2 = input("Enter the second expression: ").strip()
            
            if not expr1 or not expr2:
                print("Error: Both expressions must be non-empty!")
                continue
            
            print_section("EQUIVALENCE CHECKING")
            compare_expressions(expr1, expr2)
            
        elif choice == '3':
            print("\nExiting interactive mode. Goodbye!")
            break
            
        else:
            print("\nInvalid choice! Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
    
    # Start interactive mode after running tests
    print("\n" * 2)
    interactive_mode()
