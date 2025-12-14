"""
Comprehensive Boundary Case Tests for Mathematical Expression Analyzer

This module tests edge cases, boundary conditions, and error handling
with RIGOROUS verification of lexer tokens, AST structures, and outputs.

Run with: python test_boundary_cases.py
"""

import unittest
from lexer import tokenize, TokenType
from parser import parse
from ast_nodes import Number, Variable, BinOp, UnaryOp, FunctionCall
from polynomial import normalize_expression, is_expandable, Polynomial
from equality import are_equivalent


class TestLexerTokenSequence(unittest.TestCase):
    """Verify exact token sequences produced by the lexer."""
    
    def get_token_types(self, expr):
        """Helper to get list of token types (excluding EOF)."""
        return [t.type for t in tokenize(expr) if t.type != TokenType.EOF]
    
    def get_token_values(self, expr):
        """Helper to get list of (type, value) pairs (excluding EOF)."""
        return [(t.type, t.value) for t in tokenize(expr) if t.type != TokenType.EOF]
    
    def test_simple_addition_tokens(self):
        """x + y should produce: VARIABLE, PLUS, VARIABLE."""
        tokens = self.get_token_values('x + y')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.PLUS, '+'),
            (TokenType.VARIABLE, 'y'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_simple_multiplication_tokens(self):
        """x * y should produce: VARIABLE, MULTIPLY, VARIABLE."""
        tokens = self.get_token_values('x * y')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.MULTIPLY, '*'),
            (TokenType.VARIABLE, 'y'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_number_tokens(self):
        """123 should produce NUMBER with value 123."""
        tokens = self.get_token_values('123')
        expected = [(TokenType.NUMBER, 123)]
        self.assertEqual(tokens, expected)
    
    def test_implicit_mult_number_variable(self):
        """2x should produce: NUMBER, IMPLICIT_MULTIPLY, VARIABLE."""
        tokens = self.get_token_values('2x')
        expected = [
            (TokenType.NUMBER, 2),
            (TokenType.IMPLICIT_MULTIPLY, '*'),
            (TokenType.VARIABLE, 'x'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_implicit_mult_variable_variable(self):
        """xy should produce: VARIABLE, IMPLICIT_MULTIPLY, VARIABLE."""
        tokens = self.get_token_values('xy')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.IMPLICIT_MULTIPLY, '*'),
            (TokenType.VARIABLE, 'y'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_implicit_mult_three_variables(self):
        """xyz should produce: x * y * z with implicit multiplies."""
        tokens = self.get_token_values('xyz')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.IMPLICIT_MULTIPLY, '*'),
            (TokenType.VARIABLE, 'y'),
            (TokenType.IMPLICIT_MULTIPLY, '*'),
            (TokenType.VARIABLE, 'z'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_implicit_mult_number_paren(self):
        """2(x+1) should insert implicit multiply before parenthesis."""
        tokens = self.get_token_types('2(x+1)')
        self.assertEqual(tokens[0], TokenType.NUMBER)
        self.assertEqual(tokens[1], TokenType.IMPLICIT_MULTIPLY)
        self.assertEqual(tokens[2], TokenType.LPAREN)
    
    def test_implicit_mult_paren_variable(self):
        """(x)y should insert implicit multiply after closing paren."""
        tokens = self.get_token_types('(x)y')
        # Should be: LPAREN, VARIABLE, RPAREN, IMPLICIT_MULTIPLY, VARIABLE
        self.assertEqual(tokens[2], TokenType.RPAREN)
        self.assertEqual(tokens[3], TokenType.IMPLICIT_MULTIPLY)
        self.assertEqual(tokens[4], TokenType.VARIABLE)
    
    def test_implicit_mult_paren_number(self):
        """(x)2 should insert implicit multiply between ) and 2."""
        tokens = self.get_token_types('(x)2')
        self.assertEqual(tokens[2], TokenType.RPAREN)
        self.assertEqual(tokens[3], TokenType.IMPLICIT_MULTIPLY)
        self.assertEqual(tokens[4], TokenType.NUMBER)
    
    def test_function_token(self):
        """sin(x) should produce: FUNCTION, LPAREN, VARIABLE, RPAREN."""
        tokens = self.get_token_values('sin(x)')
        expected = [
            (TokenType.FUNCTION, 'sin'),
            (TokenType.LPAREN, '('),
            (TokenType.VARIABLE, 'x'),
            (TokenType.RPAREN, ')'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_all_functions(self):
        """All supported functions should be recognized."""
        for func in ['sin', 'cos', 'tan', 'ln', 'sqrt']:
            tokens = tokenize(f'{func}(x)')
            self.assertEqual(tokens[0].type, TokenType.FUNCTION)
            self.assertEqual(tokens[0].value, func)
    
    def test_power_operator(self):
        """x^2 should produce: VARIABLE, POWER, NUMBER."""
        tokens = self.get_token_values('x^2')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.POWER, '^'),
            (TokenType.NUMBER, 2),
        ]
        self.assertEqual(tokens, expected)
    
    def test_division_operator(self):
        """x/y should produce: VARIABLE, DIVIDE, VARIABLE."""
        tokens = self.get_token_values('x/y')
        expected = [
            (TokenType.VARIABLE, 'x'),
            (TokenType.DIVIDE, '/'),
            (TokenType.VARIABLE, 'y'),
        ]
        self.assertEqual(tokens, expected)
    
    def test_complex_expression_tokens(self):
        """2x^2 + 3x - 1 should produce correct token sequence."""
        tokens = self.get_token_types('2x^2 + 3x - 1')
        expected = [
            TokenType.NUMBER,           # 2
            TokenType.IMPLICIT_MULTIPLY, # *
            TokenType.VARIABLE,         # x
            TokenType.POWER,            # ^
            TokenType.NUMBER,           # 2
            TokenType.PLUS,             # +
            TokenType.NUMBER,           # 3
            TokenType.IMPLICIT_MULTIPLY, # *
            TokenType.VARIABLE,         # x
            TokenType.MINUS,            # -
            TokenType.NUMBER,           # 1
        ]
        self.assertEqual(tokens, expected)
    
    def test_sinx_without_paren_is_variables(self):
        """sinx (without parentheses) should be s*i*n*x."""
        tokens = self.get_token_values('sinx')
        # Should be 4 variables with 3 implicit multiplies
        variables = [t for t in tokens if t[0] == TokenType.VARIABLE]
        self.assertEqual(len(variables), 4)
        self.assertEqual([v[1] for v in variables], ['s', 'i', 'n', 'x'])
    
    def test_empty_string(self):
        """Empty input should return only EOF."""
        tokens = tokenize('')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_whitespace_handling(self):
        """Whitespace should be ignored, not create tokens."""
        tokens1 = self.get_token_types('x+y')
        tokens2 = self.get_token_types('x + y')
        tokens3 = self.get_token_types('x  +  y')
        self.assertEqual(tokens1, tokens2)
        self.assertEqual(tokens2, tokens3)
    
    def test_position_tracking(self):
        """Token positions should be accurate."""
        tokens = tokenize('x + y')
        # x at position 0, + at position 2, y at position 4
        self.assertEqual(tokens[0].pos, 0)  # x
        self.assertEqual(tokens[1].pos, 2)  # +
        self.assertEqual(tokens[2].pos, 4)  # y


class TestParserASTStructure(unittest.TestCase):
    """Verify exact AST structure produced by the parser."""
    
    def test_number_ast(self):
        """42 should produce Number(42)."""
        ast = parse('42')
        self.assertIsInstance(ast, Number)
        self.assertEqual(ast.value, 42)
    
    def test_variable_ast(self):
        """x should produce Variable('x')."""
        ast = parse('x')
        self.assertIsInstance(ast, Variable)
        self.assertEqual(ast.name, 'x')
    
    def test_addition_ast(self):
        """x + y should produce BinOp(Variable(x), '+', Variable(y))."""
        ast = parse('x + y')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '+')
        self.assertIsInstance(ast.left, Variable)
        self.assertEqual(ast.left.name, 'x')
        self.assertIsInstance(ast.right, Variable)
        self.assertEqual(ast.right.name, 'y')
    
    def test_subtraction_ast(self):
        """x - y should produce BinOp with '-' operator."""
        ast = parse('x - y')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '-')
    
    def test_multiplication_ast(self):
        """x * y should produce BinOp with '*' operator."""
        ast = parse('x * y')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
    
    def test_division_ast(self):
        """x / y should produce BinOp with '/' operator."""
        ast = parse('x / y')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '/')
    
    def test_power_ast(self):
        """x ^ 2 should produce BinOp with '^' operator."""
        ast = parse('x ^ 2')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '^')
        self.assertIsInstance(ast.left, Variable)
        self.assertIsInstance(ast.right, Number)
        self.assertEqual(ast.right.value, 2)
    
    def test_unary_minus_ast(self):
        """-x should produce UnaryOp('-', Variable(x))."""
        ast = parse('-x')
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.op, '-')
        self.assertIsInstance(ast.operand, Variable)
        self.assertEqual(ast.operand.name, 'x')
    
    def test_function_call_ast(self):
        """sin(x) should produce FunctionCall('sin', Variable(x))."""
        ast = parse('sin(x)')
        self.assertIsInstance(ast, FunctionCall)
        self.assertEqual(ast.func_name, 'sin')
        self.assertIsInstance(ast.arg, Variable)
        self.assertEqual(ast.arg.name, 'x')
    
    def test_nested_function_ast(self):
        """sin(cos(x)) should produce nested FunctionCall."""
        ast = parse('sin(cos(x))')
        self.assertIsInstance(ast, FunctionCall)
        self.assertEqual(ast.func_name, 'sin')
        self.assertIsInstance(ast.arg, FunctionCall)
        self.assertEqual(ast.arg.func_name, 'cos')
        self.assertIsInstance(ast.arg.arg, Variable)
    
    def test_addition_left_associativity(self):
        """x + y + z should be ((x + y) + z) - left associative."""
        ast = parse('x + y + z')
        # Should be BinOp(BinOp(x, +, y), +, z)
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '+')
        self.assertIsInstance(ast.right, Variable)
        self.assertEqual(ast.right.name, 'z')
        # Left should be (x + y)
        self.assertIsInstance(ast.left, BinOp)
        self.assertEqual(ast.left.op, '+')
        self.assertEqual(ast.left.left.name, 'x')
        self.assertEqual(ast.left.right.name, 'y')
    
    def test_multiplication_left_associativity(self):
        """x * y * z should be ((x * y) * z) - left associative."""
        ast = parse('x * y * z')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
        self.assertIsInstance(ast.right, Variable)
        self.assertEqual(ast.right.name, 'z')
        self.assertIsInstance(ast.left, BinOp)
        self.assertEqual(ast.left.op, '*')
    
    def test_power_right_associativity(self):
        """x^2^3 should be x^(2^3) - right associative."""
        ast = parse('x^2^3')
        # Should be BinOp(x, ^, BinOp(2, ^, 3))
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '^')
        self.assertIsInstance(ast.left, Variable)
        self.assertEqual(ast.left.name, 'x')
        # Right should be (2^3)
        self.assertIsInstance(ast.right, BinOp)
        self.assertEqual(ast.right.op, '^')
        self.assertEqual(ast.right.left.value, 2)
        self.assertEqual(ast.right.right.value, 3)
    
    def test_multiplication_precedence_over_addition(self):
        """x + y * z should be x + (y * z)."""
        ast = parse('x + y * z')
        # Top level should be addition
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '+')
        self.assertIsInstance(ast.left, Variable)
        self.assertEqual(ast.left.name, 'x')
        # Right should be multiplication
        self.assertIsInstance(ast.right, BinOp)
        self.assertEqual(ast.right.op, '*')
        self.assertEqual(ast.right.left.name, 'y')
        self.assertEqual(ast.right.right.name, 'z')
    
    def test_power_precedence_over_multiplication(self):
        """2 * x ^ 2 should be 2 * (x ^ 2)."""
        ast = parse('2 * x ^ 2')
        # Top level should be multiplication
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
        self.assertIsInstance(ast.left, Number)
        self.assertEqual(ast.left.value, 2)
        # Right should be power
        self.assertIsInstance(ast.right, BinOp)
        self.assertEqual(ast.right.op, '^')
        self.assertEqual(ast.right.left.name, 'x')
        self.assertEqual(ast.right.right.value, 2)

    def test_power_precedence_over_implicit_multiplication(self):
        """2x ^ 2 should be 2 * (x ^ 2)."""
        ast = parse('2 x ^ 2')
        # Top level should be multiplication
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
        self.assertIsInstance(ast.left, Number)
        self.assertEqual(ast.left.value, 2)
        # Right should be power
        self.assertIsInstance(ast.right, BinOp)
        self.assertEqual(ast.right.op, '^')
        self.assertEqual(ast.right.left.name, 'x')
        self.assertEqual(ast.right.right.value, 2)
    
    def test_unary_minus_precedence(self):
        """-x^2 should be -(x^2), not (-x)^2."""
        ast = parse('-x^2')
        # Top level should be unary minus
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.op, '-')
        # Operand should be x^2
        self.assertIsInstance(ast.operand, BinOp)
        self.assertEqual(ast.operand.op, '^')
        self.assertEqual(ast.operand.left.name, 'x')
        self.assertEqual(ast.operand.right.value, 2)
    
    def test_unary_minus_in_multiplication(self):
        """-x*y should be -(x*y), not (-x)*y."""
        ast = parse('-x*y')
        # Top level should be unary minus
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.op, '-')
        # Operand should be x*y
        self.assertIsInstance(ast.operand, BinOp)
        self.assertEqual(ast.operand.op, '*')
    
    def test_parentheses_override_precedence(self):
        """(x + y) * z should have addition inside."""
        ast = parse('(x + y) * z')
        # Top level should be multiplication
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
        # Left should be addition (from parentheses)
        self.assertIsInstance(ast.left, BinOp)
        self.assertEqual(ast.left.op, '+')
        # Right is z
        self.assertIsInstance(ast.right, Variable)
        self.assertEqual(ast.right.name, 'z')
    
    def test_implicit_multiplication_in_ast(self):
        """2x should produce BinOp with '*' (from implicit multiply)."""
        ast = parse('2x')
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '*')
        self.assertIsInstance(ast.left, Number)
        self.assertEqual(ast.left.value, 2)
        self.assertIsInstance(ast.right, Variable)
        self.assertEqual(ast.right.name, 'x')
    
    def test_function_with_complex_arg(self):
        """sin(x + y) should have BinOp as function argument."""
        ast = parse('sin(x + y)')
        self.assertIsInstance(ast, FunctionCall)
        self.assertEqual(ast.func_name, 'sin')
        self.assertIsInstance(ast.arg, BinOp)
        self.assertEqual(ast.arg.op, '+')
    
    def test_deep_parentheses(self):
        """(((x))) should just be Variable(x)."""
        ast = parse('(((x)))')
        self.assertIsInstance(ast, Variable)
        self.assertEqual(ast.name, 'x')
    
    def test_complex_expression_structure(self):
        """2x^2 + 3x + 1 should have correct nested structure."""
        ast = parse('2x^2 + 3x + 1')
        # Top: (2x^2 + 3x) + 1
        self.assertIsInstance(ast, BinOp)
        self.assertEqual(ast.op, '+')
        self.assertIsInstance(ast.right, Number)
        self.assertEqual(ast.right.value, 1)
        
        # Middle: (2x^2) + (3x)
        middle = ast.left
        self.assertIsInstance(middle, BinOp)
        self.assertEqual(middle.op, '+')
        
        # 3x part
        three_x = middle.right
        self.assertIsInstance(three_x, BinOp)
        self.assertEqual(three_x.op, '*')
        self.assertEqual(three_x.left.value, 3)
        self.assertEqual(three_x.right.name, 'x')
        
        # 2x^2 part: 2 * (x^2)
        two_x_squared = middle.left
        self.assertIsInstance(two_x_squared, BinOp)
        self.assertEqual(two_x_squared.op, '*')
        self.assertEqual(two_x_squared.left.value, 2)
        # x^2
        self.assertIsInstance(two_x_squared.right, BinOp)
        self.assertEqual(two_x_squared.right.op, '^')


class TestPolynomialOutput(unittest.TestCase):
    """Verify exact polynomial normalization output."""
    
    def test_constant_zero(self):
        """0 should normalize to '0'."""
        poly = normalize_expression(parse('0'))
        self.assertEqual(str(poly), '0')
    
    def test_constant_nonzero(self):
        """42 should normalize to '42'."""
        poly = normalize_expression(parse('42'))
        self.assertEqual(str(poly), '42')
    
    def test_single_variable(self):
        """x should normalize to 'x'."""
        poly = normalize_expression(parse('x'))
        self.assertEqual(str(poly), 'x')
    
    def test_zero_times_variable(self):
        """0 * x should normalize to '0'."""
        poly = normalize_expression(parse('0 * x'))
        self.assertEqual(str(poly), '0')
    
    def test_variable_times_zero(self):
        """x * 0 should normalize to '0'."""
        poly = normalize_expression(parse('x * 0'))
        self.assertEqual(str(poly), '0')
    
    def test_one_times_variable(self):
        """1 * x should normalize to 'x'."""
        poly = normalize_expression(parse('1 * x'))
        self.assertEqual(str(poly), 'x')
    
    def test_variable_minus_itself(self):
        """x - x should normalize to '0'."""
        poly = normalize_expression(parse('x - x'))
        self.assertEqual(str(poly), '0')
    
    def test_zero_plus_variable(self):
        """0 + x should normalize to 'x'."""
        poly = normalize_expression(parse('0 + x'))
        self.assertEqual(str(poly), 'x')
    
    def test_coefficient_multiplication(self):
        """2 * x should have coefficient 2."""
        poly = normalize_expression(parse('2 * x'))
        self.assertEqual(str(poly), '2*x')
    
    def test_negative_coefficient(self):
        """-2 * x should have coefficient -2."""
        poly = normalize_expression(parse('-2*x'))
        self.assertIn('-2', str(poly))
    
    def test_like_terms_combine(self):
        """x + x should be 2*x."""
        poly = normalize_expression(parse('x + x'))
        self.assertEqual(str(poly), '2*x')
    
    def test_xy_plus_xy(self):
        """xy + xy should be 2*x*y."""
        poly = normalize_expression(parse('x*y + x*y'))
        self.assertIn('2', str(poly))
    
    def test_xy_plus_yx(self):
        """xy + yx should be 2*x*y (commutativity)."""
        poly = normalize_expression(parse('x*y + y*x'))
        self.assertIn('2', str(poly))
    
    def test_power_of_two_expansion(self):
        """(x+1)^2 should expand to x^2 + 2*x + 1."""
        poly = normalize_expression(parse('(x+1)^2'))
        poly_str = str(poly)
        # Should contain x^2 and coefficient 2*x and constant 1
        self.assertIn('x^2', poly_str)
        self.assertIn('2', poly_str)
        self.assertIn('1', poly_str)
    
    def test_power_of_two_xy(self):
        """(x+y)^2 should expand to x^2 + 2*x*y + y^2."""
        poly = normalize_expression(parse('(x+y)^2'))
        poly_str = str(poly)
        self.assertIn('x^2', poly_str)
        self.assertIn('y^2', poly_str)
        self.assertIn('2*(x*y)', poly_str)

    def test_power_of_two_xy_expanded(self):
        """(x+y)^2 should expand to x^2 + 2*x*y + y^2."""
        poly = normalize_expression(parse('x^2 + 2*x*y + y^2'))
        poly_str = str(poly)
        self.assertIn('x^2', poly_str)
        self.assertIn('y^2', poly_str)
        self.assertIn('2*(x*y)', poly_str)
    
    def test_power_of_three_expansion(self):
        """(x+1)^3 should contain x^3 and 3*x^2."""
        poly = normalize_expression(parse('(x+1)^3'))
        poly_str = str(poly)
        self.assertIn('x^3', poly_str)
        self.assertIn('3', poly_str)
    
    def test_power_of_four_not_expanded(self):
        """(x+1)^4 should NOT be expanded (treated as atomic)."""
        poly = normalize_expression(parse('(x+1)^4'))
        poly_str = str(poly)
        # Should contain ^4 as it's not expanded
        self.assertIn('^4', poly_str)
    
    def test_distributive_law(self):
        """x*(y+z) should expand to xy + xz."""
        poly1 = normalize_expression(parse('x*(y+z)'))
        poly2 = normalize_expression(parse('x*y + x*z'))
        self.assertEqual(poly1, poly2)
    
    def test_polynomial_terms_dict(self):
        """x + 2y should have correct internal terms."""
        poly = normalize_expression(parse('x + 2*y'))
        # Check the internal representation
        self.assertEqual(len(poly.terms), 2)
        # Check coefficients
        for monomial, coeff in poly.terms.items():
            vars_dict = dict(monomial)
            if 'x' in vars_dict:
                self.assertEqual(coeff, 1)  # x has coefficient 1
            elif 'y' in vars_dict:
                self.assertEqual(coeff, 2)  # y has coefficient 2


class TestParserErrors(unittest.TestCase):
    """Test that parser correctly raises errors for invalid input."""
    
    def test_empty_parentheses_error(self):
        """() should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('()')
    
    def test_unbalanced_open_paren_error(self):
        """((x+1) should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('((x+1)')
    
    def test_unbalanced_close_paren_error(self):
        """(x+1)) should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('(x+1))')
    
    def test_double_operator_error(self):
        """x ++ y should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('x ++ y')
    
    def test_double_multiply_error(self):
        """x ** y should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('x ** y')
    
    def test_leading_multiply_error(self):
        """* x should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('* x')
    
    def test_leading_divide_error(self):
        """/ x should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('/ x')
    
    def test_leading_power_error(self):
        """^ x should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('^ x')
    
    def test_trailing_plus_error(self):
        """x + should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('x +')
    
    def test_trailing_multiply_error(self):
        """x * should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('x *')
    
    def test_unary_plus_error(self):
        """+x should raise ValueError (unary plus not supported)."""
        with self.assertRaises(ValueError):
            parse('+x')
    
    def test_double_unary_minus_error(self):
        """--x should raise ValueError (known limitation)."""
        with self.assertRaises(ValueError):
            parse('--x')
    
    def test_empty_function_arg_error(self):
        """sin() should raise ValueError."""
        with self.assertRaises(ValueError):
            parse('sin()')
    
    def test_negative_power_error(self):
        """x^-2 should raise ValueError (not supported)."""
        with self.assertRaises(ValueError):
            parse('x^-2')


class TestLexerErrors(unittest.TestCase):
    """Test that lexer correctly raises errors for invalid input."""
    
    def test_decimal_number_error(self):
        """3.14 should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            tokenize('3.14')
        self.assertIn('.', str(ctx.exception))
    
    def test_at_symbol_error(self):
        """x @ y should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            tokenize('x @ y')
        self.assertIn('@', str(ctx.exception))
    
    def test_hash_symbol_error(self):
        """x # y should raise ValueError."""
        with self.assertRaises(ValueError):
            tokenize('x # y')
    
    def test_dollar_symbol_error(self):
        """$x should raise ValueError."""
        with self.assertRaises(ValueError):
            tokenize('$x')
    
    def test_ampersand_error(self):
        """x & y should raise ValueError."""
        with self.assertRaises(ValueError):
            tokenize('x & y')
    
    def test_exclamation_error(self):
        """x! should raise ValueError."""
        with self.assertRaises(ValueError):
            tokenize('x!')


class TestEquivalenceChecking(unittest.TestCase):
    """Test equivalence checking with specific expected results."""
    
    def test_self_equivalence(self):
        """x ≡ x should be True."""
        self.assertTrue(are_equivalent(parse('x'), parse('x')))
    
    def test_addition_commutativity(self):
        """x + y ≡ y + x should be True."""
        self.assertTrue(are_equivalent(parse('x+y'), parse('y+x')))
    
    def test_multiplication_commutativity(self):
        """x * y ≡ y * x should be True."""
        self.assertTrue(are_equivalent(parse('x*y'), parse('y*x')))
    
    def test_subtraction_not_commutative(self):
        """x - y ≢ y - x should be False."""
        self.assertFalse(are_equivalent(parse('x-y'), parse('y-x')))
    
    def test_division_not_commutative(self):
        """x / y ≢ y / x should be False."""
        self.assertFalse(are_equivalent(parse('x/y'), parse('y/x')))
    
    def test_associativity_addition(self):
        """(x+y)+z ≡ x+(y+z) should be True."""
        self.assertTrue(are_equivalent(parse('(x+y)+z'), parse('x+(y+z)')))
    
    def test_associativity_multiplication(self):
        """(x*y)*z ≡ x*(y*z) should be True."""
        self.assertTrue(are_equivalent(parse('(x*y)*z'), parse('x*(y*z)')))
    
    def test_distributive_law(self):
        """x*(y+z) ≡ x*y+x*z should be True."""
        self.assertTrue(are_equivalent(parse('x*(y+z)'), parse('x*y+x*z')))
    
    def test_zero_identity(self):
        """x + 0 ≡ x should be True."""
        self.assertTrue(are_equivalent(parse('x+0'), parse('x')))
    
    def test_one_identity(self):
        """x * 1 ≡ x should be True."""
        self.assertTrue(are_equivalent(parse('x*1'), parse('x')))
    
    def test_zero_multiplication(self):
        """x * 0 ≡ 0 should be True."""
        self.assertTrue(are_equivalent(parse('x*0'), parse('0')))
    
    def test_self_subtraction(self):
        """x - x ≡ 0 should be True."""
        self.assertTrue(are_equivalent(parse('x-x'), parse('0')))
    
    def test_polynomial_expansion(self):
        """(x+1)^2 ≡ x^2+2x+1 should be True."""
        self.assertTrue(are_equivalent(parse('(x+1)^2'), parse('x^2+2*x+1')))
    
    def test_factorization(self):
        """x*y+x*z ≡ x*(y+z) should be True."""
        self.assertTrue(are_equivalent(parse('x*y+x*z'), parse('x*(y+z)')))
    
    def test_different_constants_not_equivalent(self):
        """1 ≢ 2 should be False."""
        self.assertFalse(are_equivalent(parse('1'), parse('2')))
    
    def test_different_variables_not_equivalent(self):
        """x ≢ y should be False."""
        self.assertFalse(are_equivalent(parse('x'), parse('y')))
    
    def test_different_functions_not_equivalent(self):
        """sin(x) ≢ cos(x) should be False."""
        self.assertFalse(are_equivalent(parse('sin(x)'), parse('cos(x)')))
    
    def test_function_arg_commutativity(self):
        """sin(x+y) ≡ sin(y+x) should be True."""
        self.assertTrue(are_equivalent(parse('sin(x+y)'), parse('sin(y+x)')))
    
    def test_rational_equivalence(self):
        """1-1/x ≡ (x-1)/x should be True."""
        self.assertTrue(are_equivalent(parse('1-1/x'), parse('(x-1)/x')))
    
    def test_x_over_x(self):
        """x/x ≡ 1 should be True."""
        self.assertTrue(are_equivalent(parse('x/x'), parse('1')))
    
    def test_implicit_vs_explicit_mult(self):
        """2x ≡ 2*x should be True."""
        self.assertTrue(are_equivalent(parse('2x'), parse('2*x')))


class TestExpandableCheck(unittest.TestCase):
    """Test is_expandable function."""
    
    def test_number_expandable(self):
        """Numbers are expandable."""
        self.assertTrue(is_expandable(parse('42')))
    
    def test_variable_expandable(self):
        """Variables are expandable."""
        self.assertTrue(is_expandable(parse('x')))
    
    def test_addition_expandable(self):
        """Addition is expandable."""
        self.assertTrue(is_expandable(parse('x + y')))
    
    def test_subtraction_expandable(self):
        """Subtraction is expandable."""
        self.assertTrue(is_expandable(parse('x - y')))
    
    def test_multiplication_expandable(self):
        """Multiplication is expandable."""
        self.assertTrue(is_expandable(parse('x * y')))
    
    def test_unary_minus_expandable(self):
        """Unary minus is expandable."""
        self.assertTrue(is_expandable(parse('-x')))
    
    def test_division_not_expandable(self):
        """Division is NOT expandable."""
        self.assertFalse(is_expandable(parse('x / y')))
    
    def test_power_not_expandable(self):
        """Power is NOT expandable."""
        self.assertFalse(is_expandable(parse('x ^ 2')))
    
    def test_function_not_expandable(self):
        """Functions are NOT expandable."""
        self.assertFalse(is_expandable(parse('sin(x)')))
    
    def test_nested_with_division(self):
        """x + y/z is NOT expandable (contains division)."""
        self.assertFalse(is_expandable(parse('x + y/z')))


class TestStressTests(unittest.TestCase):
    """Stress tests for large/complex expressions."""
    
    def test_long_addition_chain(self):
        """Long chain of additions."""
        expr = '+'.join(['x'] * 100)
        ast = parse(expr)
        self.assertIsInstance(ast, BinOp)
        # Normalize and check it's 100*x
        poly = normalize_expression(ast)
        self.assertIn('100', str(poly))
    
    def test_long_multiplication_chain(self):
        """Long chain of multiplications."""
        expr = '*'.join(['x'] * 10)
        ast = parse(expr)
        self.assertIsInstance(ast, BinOp)
        poly = normalize_expression(ast)
        # Should be x^10
        self.assertIn('x^10', str(poly))
    
    def test_many_nested_parentheses(self):
        """50 levels of nested parentheses."""
        depth = 50
        expr = '(' * depth + 'x' + ')' * depth
        ast = parse(expr)
        # Should just be Variable(x)
        self.assertIsInstance(ast, Variable)
        self.assertEqual(ast.name, 'x')
    
    def test_many_variables_polynomial(self):
        """Polynomial with many variables."""
        expr = '+'.join('abcdefghij')
        poly = normalize_expression(parse(expr))
        # Should have 10 terms
        self.assertEqual(len(poly.terms), 10)


def run_tests():
    """Run all tests and display summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLexerTokenSequence))
    suite.addTests(loader.loadTestsFromTestCase(TestParserASTStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestPolynomialOutput))
    suite.addTests(loader.loadTestsFromTestCase(TestParserErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestLexerErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestEquivalenceChecking))
    suite.addTests(loader.loadTestsFromTestCase(TestExpandableCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestStressTests))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("BOUNDARY CASE TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nTests with errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


if __name__ == "__main__":
    run_tests()
