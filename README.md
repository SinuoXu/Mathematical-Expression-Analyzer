# Mathematical Expression Analyzer

A complete Python implementation for analyzing, parsing, and comparing mathematical expressions with support for polynomial normalization and equivalence checking.

## Features

### Supported Expression Elements
- **Numbers**: Integer constants (positive and negative)
- **Variables**: Single-letter variables (x, y, z, etc.)
- **Operators**: 
  - Arithmetic: `+`, `-`, `*`, `/`
  - Exponentiation: `^` (with special handling for powers 2 and 3)
- **Functions**: `sin`, `cos`, `tan`, `ln`, `sqrt`
- **Implicit Multiplication**: `2x`, `x(y+1)`, `xy`, etc.
- **Parentheses**: Full support for grouping

### Core Capabilities

1. **Lexical Analysis (Lexer)**
   - Tokenizes mathematical expressions
   - Automatically detects and inserts implicit multiplication
   - Handles multi-character functions and operators

2. **Syntax Analysis (Parser)**
   - Recursive descent parser with proper operator precedence
   - Precedence order:
     1. Functions (sin, cos, tan, ln, sqrt)
     2. Exponentiation (^)
     3. Multiplication and Division (*, /)
     4. Addition and Subtraction (+, -)

3. **Abstract Syntax Tree (AST)**
   - Comprehensive node types for all expression elements
   - Pretty-printing support for debugging

4. **Polynomial Normalization**
   - Converts expressions into canonical polynomial form
   - Supports expansion of (expr)^2 and (expr)^3
   - Treats non-expandable operations (/, functions, arbitrary powers) as atomic expressions
   - Applies associativity and commutativity rules

5. **Equivalence Checking**
   - Determines if two expressions are mathematically equivalent
   - Based on polynomial normalization
   - Supports recognition of:
     - Additive commutativity: `1 + x` ≡ `x + 1`
     - Multiplicative commutativity: `x * y` ≡ `y * x`
     - Associativity (both addition and multiplication)
     - Distributivity and expansion: `(x + 1)^2` ≡ `x^2 + 2x + 1`

## Project Structure

```
src/
├── __init__.py         # Package initialization
├── ast.py              # AST node definitions
├── lexer.py            # Lexical analyzer
├── parser.py           # Syntax analyzer  
├── polynomial.py       # Polynomial normalization
├── equality.py         # Equivalence checking
└── main.py             # Examples and tests
```

## Usage

### Basic Expression Parsing

```python
from src.parser import parse
from src.ast import print_ast

# Parse an expression
ast = parse("(x + 1)^2")

# Display the AST
print_ast(ast)
```

### Expression Normalization

```python
from src.parser import parse
from src.polynomial import normalize_expression

# Parse and normalize
ast = parse("(x + 1) * (x + 1)")
poly = normalize_expression(ast)

print(poly)  # Output: 1 + 2*x + x^2
```

### Equivalence Checking

```python
from src.parser import parse
from src.equality import are_equivalent

expr1 = parse("(x + 1)^2")
expr2 = parse("x^2 + 2x + 1")

if are_equivalent(expr1, expr2):
    print("Expressions are equivalent!")
```

### Running Tests

```bash
cd /Users/xusinuo/Desktop
python -m src.main
```

This will run comprehensive tests including:
- Single expression analysis
- Equivalence testing (23 test cases)
- Complex expression handling
- Implicit multiplication verification

## Test Results

The test suite validates:

✓ **Commutativity**
- Addition: `1 + x` ≡ `x + 1`
- Multiplication: `x * y` ≡ `y * x`

✓ **Associativity**
- Addition: `(x + y) + z` ≡ `x + (y + z)`
- Multiplication: `(x * y) * z` ≡ `x * (y * z)`

✓ **Distributivity & Expansion**
- `(x + 1)^2` ≡ `x^2 + 2x + 1`
- `(x + 1)^3` ≡ `x^3 + 3x^2 + 3x + 1`
- `x*y + x*z` ≡ `x*(y + z)`

✓ **Edge Cases**
- `0 + x` ≡ `x`
- `x * 1` ≡ `x`
- `x + 0` ≡ `x`

✓ **Non-Equivalence Detection**
- `x + 1` ≢ `x + 2`
- `x * y` ≢ `x + y`
- `x^2` ≢ `x^3`

**Current Pass Rate: 23/23 (100%)**

## Implementation Details

### Polynomial Representation

Polynomials are represented as dictionaries mapping monomials to coefficients:
```python
{
    frozenset(): coefficient,              # Constant term
    frozenset([('x', 1)]): coefficient,   # Linear x
    frozenset([('x', 2)]): coefficient,   # Quadratic x^2
    frozenset([('x', 1), ('y', 1)]): coeff  # Mixed terms xy
}
```

### Atomic Expressions

Non-expandable subexpressions (containing `/`, arbitrary powers, or functions) are treated as atomic variables:
- `sin(x)` → Atom(0:sin(x))
- `x / 2` → Atom(1:(x/2))
- `x^4` → Atom(2:(x^4))

### Implicit Multiplication

Automatically inserted between:
- Number and variable: `2x` → `2 * x`
- Variable and parenthesis: `x(y+1)` → `x * (y + 1)`
- Number and parenthesis: `2(x+1)` → `2 * (x + 1)`
- Closing and opening parenthesis: `(x)(y)` → `(x) * (y)`

## Limitations

The implementation does NOT handle:
- Arbitrary algebraic identities (e.g., `sin²(x) + cos²(x) = 1`)
- Complex simplifications (e.g., `(1/x) * x = 1`)
- Non-constant exponents (powers other than 2 or 3)
- Automatic differentiation or symbolic integration
- Taylor series expansion

## Dependencies

**None!** The entire project uses only Python standard library:
- `abc` - Abstract base classes
- `enum` - Enum types
- `typing` - Type hints

## Author

Created as a comprehensive educational project demonstrating:
- Compiler/interpreter concepts
- Lexical and syntactic analysis
- Abstract syntax trees
- Symbolic mathematics
- Algorithm design

## License

This project is provided as an educational resource.
