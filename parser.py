"""
Parser (Syntax Analyzer) Module
Implements recursive descent parser with operator precedence.
Priority order (highest to lowest):
  1. Primary (numbers, variables, parentheses)
  2. Functions (sin, cos, tan, ln, sqrt)
  3. Power (^) - right associative
  4. Multiply, Divide (*, /)
  5. Unary minus (-)
  6. Add, Subtract (+, -)

Note: Unary minus has lower precedence than multiplication and power:
  - -x^2 is parsed as -(x^2), not (-x)^2
  - -x*y is parsed as -(x*y), not (-x)*y
  - -2*x^2 is parsed as -(2*x^2), not (-2)*x^2
"""

from typing import List, Optional
from lexer import Token, TokenType, tokenize
from ast import ASTNode, Number, Variable, BinOp, UnaryOp, FunctionCall


class Parser:
    """Recursive descent parser for mathematical expressions."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> ASTNode:
        """Parse tokens into an AST."""
        node = self._parse_expression()
        
        if self.current_token().type != TokenType.EOF:
            raise ValueError(f"Unexpected token: {self.current_token()}")
        
        return node
    
    def current_token(self) -> Token:
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek_token(self, offset: int = 1) -> Token:
        """Look ahead at token."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def consume(self, expected_type: Optional[TokenType] = None) -> Token:
        """Consume and return current token."""
        token = self.current_token()
        
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}")
        
        self.pos += 1
        return token
    
    def _parse_expression(self) -> ASTNode:
        """Parse addition/subtraction (lowest precedence)."""
        # Handle leading minus as 0 - expr
        if self.current_token().type == TokenType.MINUS:
            self.consume()
            # Create 0 - expr instead of UnaryOp: -
            zero = Number(0)
            right = self._parse_unary()
            left = BinOp(zero, '-', right)
        else:
            left = self._parse_unary()
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.consume()
            right = self._parse_unary()
            left = BinOp(left, op_token.value, right)
        
        return left
    
    def _parse_term(self) -> ASTNode:
        """Parse multiplication/division (including implicit multiplication)."""
        left = self._parse_power()
        
        while self.current_token().type in (TokenType.MULTIPLY, TokenType.IMPLICIT_MULTIPLY, TokenType.DIVIDE):
            op_token = self.consume()
            right = self._parse_power()
            # Both MULTIPLY and IMPLICIT_MULTIPLY are treated as '*' in the AST
            left = BinOp(left, '*' if op_token.type == TokenType.IMPLICIT_MULTIPLY else op_token.value, right)
        
        return left
    
    def _parse_power(self) -> ASTNode:
        """Parse exponentiation (right-associative)."""
        left = self._parse_function()
        
        if self.current_token().type == TokenType.POWER:
            op_token = self.consume()
            # Right-associative: a^b^c = a^(b^c)
            # Unary minus has lower precedence than power, so we parse power first
            right = self._parse_power()
            return BinOp(left, op_token.value, right)
        
        return left
    
    def _parse_function(self) -> ASTNode:
        """Parse function calls."""
        # Handle functions
        if self.current_token().type == TokenType.FUNCTION:
            func_token = self.consume()
            
            # Function must be followed by primary expression or parenthesized expression
            arg = self._parse_primary()
            return FunctionCall(func_token.value, arg)
        
        return self._parse_primary()
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary minus (lower precedence than multiplication and power)."""
        # Handle unary minus
        if self.current_token().type == TokenType.MINUS:
            self.consume()
            # Unary minus has lower precedence than multiplication and power
            # So -x^2 should be parsed as -(x^2), not (-x)^2
            # And -x*y should be parsed as -(x*y), not (-x)*y
            operand = self._parse_term()
            return UnaryOp('-', operand)
        
        return self._parse_term()
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expressions: numbers, variables, and parenthesized expressions."""
        token = self.current_token()
        
        # Numbers
        if token.type == TokenType.NUMBER:
            self.consume()
            return Number(token.value)
        
        # Variables
        if token.type == TokenType.VARIABLE:
            self.consume()
            return Variable(token.value)
        
        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.consume()
            expr = self._parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        raise ValueError(f"Unexpected token in primary: {token}")


def parse(expression: str) -> ASTNode:
    """Convenience function to parse an expression string."""
    tokens = tokenize(expression)
    parser = Parser(tokens)
    return parser.parse()
