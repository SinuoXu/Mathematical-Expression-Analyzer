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
   - **Important**: Function calls must include parentheses (e.g., `sin(x)`). Writing `sinx` will be parsed as `s*i*n*x`

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
   - Determines if two expressions are mathematically equivalent (functional equivalence)
   - **Equivalence criterion**: Two expressions are equivalent if they produce the same result for all variable values
   - **Implementation strategy**:
     1. Polynomial normalization for expandable expressions
     2. Structural equality checking (considering commutativity)
     3. Rational form simplification: converts to numerator/denominator form and uses cross-multiplication
   - Supports recognition of:
     - Additive commutativity: `1 + x` ≡ `x + 1`
     - Multiplicative commutativity: `x * y` ≡ `y * x`
     - Associativity (both addition and multiplication)
     - Distributivity and expansion: `(x + 1)^2` ≡ `x^2 + 2x + 1`
     - Rational equivalence: `1 - 1/x` ≡ `(x-1)/x`


## Running Tests

```bash
# Run from the project root directory
python main.py
```

This will run comprehensive tests including:
- Single expression analysis (tokens → AST → normalized form)
- Equivalence testing with multiple test cases
- Complex expression handling
- Implicit multiplication verification
- Interactive mode for manual testing

```bash
# Run from the project root directory
python test.py
```

This will only run:
- Interactive mode for manual testing

## Project Structure

```
Mathematical-Expression-Analyzer/
├── ast_nodes.py        # AST node definitions
├── lexer.py            # Lexical analyzer
├── parser.py           # Syntax analyzer  
├── polynomial.py       # Polynomial normalization
├── equality.py         # Equivalence checking
├── main.py             # Main program and tests
├── test.py             # Additional tests
└── README.md           # This file
```

## Usage

### Basic Expression Parsing

```python
from parser import parse
from ast_nodes import print_ast

# Parse an expression
ast = parse("(x + 1)^2")

# Display the AST
print_ast(ast)
```

### Expression Normalization

```python
from parser import parse
from polynomial import normalize_expression

# Parse and normalize
ast = parse("(x + 1) * (x + 1)")
poly = normalize_expression(ast)

print(poly)  # Output: 1 + 2*x + x^2
```

### Equivalence Checking

```python
from parser import parse
from equality import are_equivalent

expr1 = parse("(x + 1)^2")
expr2 = parse("x^2 + 2x + 1")

if are_equivalent(expr1, expr2):
    print("Expressions are equivalent!")
```

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
