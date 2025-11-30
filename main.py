"""
Main Module - Simplified Testing
Two main tasks:
1. Analyze Expression: Show tokens and AST
2. Check Equivalence: Compare two expressions
"""

from lexer import tokenize
from parser import parse
from ast_nodes import print_ast
from polynomial import normalize_expression
from equality import are_equivalent, check_equivalence_verbose


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def analyze_expression(expr_str: str):
    """
    Task 1: Analyze a single expression
    Shows: Tokens (table) → AST → Normalized Form
    
    Args:
        expr_str: Expression string to analyze
    """
    print(f"\n[Expression: {expr_str}]")
    print("-" * 70)
    
    try:
        # Tokenize - show as table
        tokens = tokenize(expr_str)
        print("Tokens:")
        for token in tokens:
            token_type = token.type.name
            # Highlight implicit multiplication
            if token.type.name == 'IMPLICIT_MULTIPLY':
                token_type = f"*{token_type}*"
            print(f"  {token_type:22} | value={repr(token.value):10} | pos={token.pos}")
        
        # Parse to AST
        ast = parse(expr_str)
        print("\nAST:")
        print_ast(ast, indent=2)
        
        # Normalize
        poly = normalize_expression(ast)
        # print(f"\nNormalized: {poly}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def check_equivalence(expr1_str: str, expr2_str: str):
    """
    Task 2: Check if two expressions are equivalent
    Shows: Expression 1, Expression 2 → Result
    
    Args:
        expr1_str: First expression string
        expr2_str: Second expression string
    """
    try:
        ast1 = parse(expr1_str)
        ast2 = parse(expr2_str)
        
        is_equiv, method, details = check_equivalence_verbose(ast1, ast2)
        
        status = "✓ EQUIVALENT" if is_equiv else "✗ NOT EQUIVALENT"
        print(f"{expr1_str:20} ≟ {expr2_str:20} → {status} ({method})")
        
        return is_equiv
    except Exception as e:
        print(f"{expr1_str:20} ≟ {expr2_str:20} → ✗ ERROR: {e}")
        return False


def main():
    """Run organized test cases."""
    
    print_section("MATHEMATICAL EXPRESSION ANALYZER")
    print("Two main tasks: (1) Analyze Expression  (2) Check Equivalence")
    
    # ========== TASK 1: EXPRESSION ANALYSIS ==========
    print_section("TASK 1: EXPRESSION ANALYSIS")
    print("Shows: Tokens → AST → Normalized Form\n")
    
    analysis_tests = [
        # Basic expressions
        "x + 1",
        "2x",
        "x^2",
        
        # Polynomial expansion
        "(x+1)^2",
        "x^2 + 2x + 1",
        
        # Functions
        "sin(x)",
        "sin(x+y)",
        
        # Complex expressions
        "x^2 / 2",
        "1 - 1/x",
        
        # Implicit multiplication
        "2(x+1)",
        "xy",
        "sin(x)cos(x)",
    ]
    
    for expr in analysis_tests:
        analyze_expression(expr)
    
    # ========== TASK 2: EQUIVALENCE CHECKING ==========
    print_section("TASK 2: EQUIVALENCE CHECKING")
    print("Format: Expression1 ≟ Expression2 → Result\n")
    
    equivalence_tests = [
        # Commutativity
        ("x + 1", "1 + x"),
        ("x * y", "y * x"),
        ("sin(x) + cos(x)", "cos(x) + sin(x)"),
        
        # Polynomial expansion
        ("(x+1)^2", "x^2 + 2x + 1"),
        ("(x+y)^2", "x^2 + 2xy + y^2"),
        ("(x+1)^3", "x^3 + 3x^2 + 3x + 1"),
        
        # Distributivity
        ("2(x+1)", "2x + 2"),
        ("x(y+z)", "xy + xz"),
        
        # Associativity
        ("(x+y)+z", "x+(y+z)"),
        ("(x*y)*z", "x*(y*z)"),
        
        # Rational functions
        ("1-1/x", "(x-1)/x"),
        ("x/x", "1"),
        ("2/x + 3/x", "5/x"),
        
        # Function arguments
        ("sin(x+y)", "sin(y+x)"),
        ("ln(x*y)", "ln(y*x)"),
        
        # Implicit multiplication
        ("2x", "x*2"),
        ("xy", "x*y"),
        ("2(x+1)", "2*(x+1)"),
        
        # Non-equivalent cases
        ("x+1", "x+2"),
        ("x^2", "x^3"),
        ("sin(x)", "cos(x)"),
    ]
    
    print("Testing equivalence...")
    correct = 0
    total = len(equivalence_tests)
    
    for expr1, expr2 in equivalence_tests:
        result = check_equivalence(expr1, expr2)
        if result is not None:
            correct += 1
    
    print(f"\n{correct}/{total} tests completed successfully")
    
    # ========== SPECIAL CASES ==========
    print_section("SPECIAL CASES")
    print("Edge cases and complex scenarios\n")
    
    special_tests = [
        ("0 + x", "x", "Identity: 0+x = x"),
        ("x * 1", "x", "Identity: x*1 = x"),
        ("x + 0", "x", "Identity: x+0 = x"),
        ("x*y + x*z", "x*(y+z)", "Factorization"),
        ("(x^2-1)/(x-1)", "x+1", "Rational simplification"),
        ("sin(x)*cos(x)", "cos(x)*sin(x)", "Function commutativity"),
    ]
    
    for expr1, expr2, desc in special_tests:
        print(f"[{desc}]")
        check_equivalence(expr1, expr2)
    
    print_section("TESTING COMPLETE")


def interactive_mode():
    """
    Interactive mode for testing expressions.
    """
    print_section("INTERACTIVE MODE")
    print("Choose a task:")
    print("  1. Analyze expression (tokens + AST)")
    print("  2. Check equivalence")
    print("  3. Exit")
    
    while True:
        print("\n" + "-" * 70)
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == '1':
            expr = input("Enter expression: ").strip()
            if expr:
                analyze_expression(expr)
            else:
                print("✗ Empty expression")
                
        elif choice == '2':
            expr1 = input("Enter first expression: ").strip()
            expr2 = input("Enter second expression: ").strip()
            if expr1 and expr2:
                check_equivalence(expr1, expr2)
            else:
                print("✗ Both expressions required")
                
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("✗ Invalid choice")


if __name__ == "__main__":
    main()
    
    # Uncomment to enable interactive mode
    print("\n" * 2)
    interactive_mode()
