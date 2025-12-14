    def test_multiple_unary_minus_error(self):
        """Multiple unary minus (---x) is not currently supported."""
        # This is a known limitation - double minus should ideally work
        with self.assertRaises(ValueError):
            parse('--x')

    def test_negative_power_error(self):
        """Negative exponent (x^-2) is not currently supported."""
        with self.assertRaises(ValueError):
            parse('x^-2')

    def test_unary_minus_in_multiplication(self):
        """-x*y should be -(x*y), not (-x)*y."""
        ast = parse('-x*y')
        # Top level should be unary minus
        self.assertIsInstance(ast, UnaryOp)
        self.assertEqual(ast.op, '-')
        # Operand should be x*y
        self.assertIsInstance(ast.operand, BinOp)
        self.assertEqual(ast.operand.op, '*')

    def test_deep_parentheses(self):
        """(((x))) should just be Variable(x)."""
        ast = parse('(((x)))')
        self.assertIsInstance(ast, Variable)
        self.assertEqual(ast.name, 'x')