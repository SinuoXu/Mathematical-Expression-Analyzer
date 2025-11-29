"""
Lexer (Lexical Analyzer) Module
Tokenizes mathematical expressions, handling implicit multiplication.
"""

from typing import List, Optional, NamedTuple
from enum import Enum, auto


class TokenType(Enum):
    """Token type enumeration."""
    NUMBER = auto()
    VARIABLE = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    IMPLICIT_MULTIPLY = auto()  # Implicit multiplication (e.g., 2x, xy)
    DIVIDE = auto()
    POWER = auto()
    LPAREN = auto()
    RPAREN = auto()
    FUNCTION = auto()  # sin, cos, tan, ln, sqrt
    EOF = auto()


class Token(NamedTuple):
    """Represents a single token."""
    type: TokenType
    value: any
    pos: int


class Lexer:
    """Tokenizes mathematical expressions."""
    
    FUNCTIONS = {'sin', 'cos', 'tan', 'ln', 'sqrt'}
    
    def __init__(self, expression: str):
        self.expression = expression
        self.pos = 0
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Convert expression string into list of tokens."""
        while self.pos < len(self.expression):
            self._skip_whitespace()
            
            if self.pos >= len(self.expression):
                break
            
            ch = self.expression[self.pos]
            
            # Numbers
            if ch.isdigit():
                self._read_number()
            # Variables or functions
            elif ch.isalpha():
                self._read_identifier()
            # Operators and delimiters
            elif ch == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.pos))
                self.pos += 1
            elif ch == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', self.pos))
                self.pos += 1
            elif ch == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', self.pos))
                self.pos += 1
            elif ch == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', self.pos))
                self.pos += 1
            elif ch == '^':
                self.tokens.append(Token(TokenType.POWER, '^', self.pos))
                self.pos += 1
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.pos))
                self.pos += 1
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.pos))
                self.pos += 1
            else:
                raise ValueError(f"Unexpected character '{ch}' at position {self.pos}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.pos))
        return self._handle_implicit_multiplication()
    
    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < len(self.expression) and self.expression[self.pos].isspace():
            self.pos += 1
    
    def _read_number(self):
        """Read a numeric token."""
        start = self.pos
        while self.pos < len(self.expression) and self.expression[self.pos].isdigit():
            self.pos += 1
        value = int(self.expression[start:self.pos])
        self.tokens.append(Token(TokenType.NUMBER, value, start))
    
    def _read_identifier(self):
        """Read a variable or function token."""
        start = self.pos
        while self.pos < len(self.expression) and self.expression[self.pos].isalpha():
            self.pos += 1
        identifier = self.expression[start:self.pos]
        
        if identifier in self.FUNCTIONS:
            self.tokens.append(Token(TokenType.FUNCTION, identifier, start))
        else:
            # Single-letter variable
            if len(identifier) == 1:
                self.tokens.append(Token(TokenType.VARIABLE, identifier, start))
            else:
                raise ValueError(f"Invalid identifier '{identifier}' at position {start}")
    
    def _handle_implicit_multiplication(self) -> List[Token]:
        """
        Insert IMPLICIT_MULTIPLY tokens for implicit multiplication.
        The position is set to be between the two adjacent tokens.
        Cases:
        - number followed by variable/function/lparen: 2x, 2sin(x), 2(x+1)
        - variable/rparen followed by variable/function/lparen: x(y+1), xy, x sin(x)
        """
        result = []
        
        for i, token in enumerate(self.tokens):
            result.append(token)
            
            if i < len(self.tokens) - 1:
                next_token = self.tokens[i + 1]
                
                # Check if we need to insert implicit multiplication
                should_insert_mult = False
                
                # Current token is NUMBER
                if token.type == TokenType.NUMBER:
                    if next_token.type in (TokenType.VARIABLE, TokenType.FUNCTION, TokenType.LPAREN):
                        should_insert_mult = True
                
                # Current token is VARIABLE
                elif token.type == TokenType.VARIABLE:
                    if next_token.type in (TokenType.VARIABLE, TokenType.FUNCTION, TokenType.LPAREN, TokenType.NUMBER):
                        should_insert_mult = True
                
                # Current token is RPAREN
                elif token.type == TokenType.RPAREN:
                    if next_token.type in (TokenType.VARIABLE, TokenType.FUNCTION, TokenType.LPAREN, TokenType.NUMBER):
                        should_insert_mult = True
                
                if should_insert_mult:
                    # Position is between current token end and next token start
                    implicit_pos = token.pos + len(str(token.value)) if token.value else token.pos + 1
                    result.append(Token(TokenType.IMPLICIT_MULTIPLY, '*', implicit_pos))
        
        return result


def tokenize(expression: str) -> List[Token]:
    """Convenience function to tokenize an expression."""
    lexer = Lexer(expression)
    return lexer.tokenize()
