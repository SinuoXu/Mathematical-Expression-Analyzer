"""
Interactive Test Program
Allows users to interactively test the mathematical expression analyzer.
"""

from lexer import tokenize
from parser import parse
from ast_nodes import print_ast
from polynomial import normalize_expression, is_expandable
from equality import are_equivalent


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 70)
    print("  MATHEMATICAL EXPRESSION ANALYZER - INTERACTIVE MODE")
    print("=" * 70)
    print("\nPlease select an option:")
    print("  1. Analyze single expression (Lexer -> Parser -> Polynomial)")
    print("  2. Check equality of two expressions")
    print("  3. Exit")
    print("-" * 70)


def analyze_single_expression():
    """Analyze a single expression through all stages."""
    print("\n" + "=" * 70)
    print("  SINGLE EXPRESSION ANALYSIS")
    print("=" * 70)
    
    expr = input("\nEnter expression: ").strip()
    
    if not expr:
        print("Error: Empty expression")
        return
    
    print(f"\nAnalyzing: {expr}")
    print("-" * 70)
    
    try:
        # Stage 1: Lexical Analysis
        print("\n[STAGE 1: LEXICAL ANALYSIS]")
        tokens = tokenize(expr)
        print("Tokens:")
        for token in tokens:
            print(f"  {token.type.name:12} | value={repr(token.value):10} | pos={token.pos}")
        
        # Stage 2: Syntax Analysis (Parsing)
        print("\n[STAGE 2: SYNTAX ANALYSIS]")
        ast = parse(expr)
        print("Abstract Syntax Tree:")
        print_ast(ast, indent=2)
        
        # Stage 3: Polynomial Normalization
        print("\n[STAGE 3: POLYNOMIAL NORMALIZATION]")
        poly = normalize_expression(ast)
        print(f"Normalized form: {poly}")
        
        print("\n" + "=" * 70)
        print("Analysis complete!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def check_equality():
    """Check if two expressions are equivalent."""
    print("\n" + "=" * 70)
    print("  EXPRESSION EQUALITY CHECK")
    print("=" * 70)
    
    expr1 = input("\nEnter first expression: ").strip()
    expr2 = input("Enter second expression: ").strip()
    
    if not expr1 or not expr2:
        print("Error: Both expressions must be non-empty")
        return
    
    print(f"\nComparing:")
    print(f"  Expression 1: {expr1}")
    print(f"  Expression 2: {expr2}")
    print("-" * 70)
    
    try:
        # Parse both expressions
        print("\n[Parsing Expression 1]")
        ast1 = parse(expr1)
        poly1 = normalize_expression(ast1)
        print(f"Normalized: {poly1}")
        
        print("\n[Parsing Expression 2]")
        ast2 = parse(expr2)
        poly2 = normalize_expression(ast2)
        print(f"Normalized: {poly2}")
        
        # Check equivalence
        print("\n[Equivalence Check]")
        is_equiv = are_equivalent(ast1, ast2)
        
        print("-" * 70)
        if is_equiv:
            print("✓ RESULT: The expressions are EQUIVALENT")
        else:
            print("✗ RESULT: The expressions are NOT EQUIVALENT")
        print("-" * 70)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main interactive loop."""
    print("\n" + "=" * 70)
    print("  Welcome to the Mathematical Expression Analyzer!")
    print("=" * 70)
    print("\nSupported features:")
    print("  - Operators: +, -, *, /, ^")
    print("  - Functions: sin, cos, tan, ln, sqrt")
    print("  - Variables: single letters (a-z, A-Z)")
    print("  - Implicit multiplication: 2x, xy, 2(x+1), etc.")
    print("  - Polynomial expansion: (x+1)^2, (x+1)^3")
    print("  - Simple equality checking: 2x + y == y + 2 * x, 0 * x == 0, etc.")
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                analyze_single_expression()
            
            elif choice == '2':
                check_equality()
            
            elif choice == '3':
                print("\n" + "=" * 70)
                print("  Thank you for using the Expression Analyzer!")
                print("=" * 70)
                break
            
            else:
                print("\nInvalid choice. Please enter 1, 2, or 3.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            print("\n" + "=" * 70)
            print("  Thank you for using the Expression Analyzer!")
            print("=" * 70)
            break
        
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
