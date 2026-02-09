"""
Lexer - Tokenizes SQL statements into tokens
This is the first stage of SQL parsing where we break down the raw SQL string
into meaningful pieces (tokens) like keywords, identifiers, operators, etc.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """All possible token types our SQL engine recognizes"""
    # Keywords
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    INSERT = auto()
    INTO = auto()
    VALUES = auto()
    CREATE = auto()
    TABLE = auto()
    INT = auto()
    VARCHAR = auto()
    AND = auto()
    OR = auto()
    
    # Literals and Identifiers
    IDENTIFIER = auto()  # table names, column names
    NUMBER = auto()      # numeric literals
    STRING = auto()      # string literals
    
    # Operators
    EQUALS = auto()      # =
    GREATER = auto()     # >
    LESS = auto()        # <
    GREATER_EQ = auto()  # >=
    LESS_EQ = auto()     # <=
    NOT_EQ = auto()      # !=
    
    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    STAR = auto()        # *
    
    # Special
    EOF = auto()         # End of file/statement


@dataclass
class Token:
    """Represents a single token with its type and value"""
    type: TokenType
    value: any
    position: int  # Position in the original SQL string for error reporting


class Lexer:
    """
    Converts raw SQL text into a stream of tokens.
    
    This class implements a simple lexer that recognizes:
    - SQL keywords (SELECT, FROM, WHERE, etc.)
    - Identifiers (table and column names)
    - String and numeric literals
    - Operators and punctuation
    """
    
    # Map of keyword strings to their token types
    KEYWORDS = {
        'SELECT': TokenType.SELECT,
        'FROM': TokenType.FROM,
        'WHERE': TokenType.WHERE,
        'INSERT': TokenType.INSERT,
        'INTO': TokenType.INTO,
        'VALUES': TokenType.VALUES,
        'CREATE': TokenType.CREATE,
        'TABLE': TokenType.TABLE,
        'INT': TokenType.INT,
        'VARCHAR': TokenType.VARCHAR,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
    }
    
    def __init__(self, sql: str):
        """
        Initialize the lexer with SQL text.
        
        Args:
            sql: The SQL statement to tokenize
        """
        self.sql = sql
        self.position = 0
        self.current_char = self.sql[0] if sql else None
    
    def advance(self):
        """Move to the next character in the SQL string"""
        self.position += 1
        if self.position >= len(self.sql):
            self.current_char = None
        else:
            self.current_char = self.sql[self.position]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Look ahead at the next character without consuming it"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.sql):
            return None
        return self.sql[peek_pos]
    
    def skip_whitespace(self):
        """Skip over whitespace characters"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_number(self) -> Token:
        """
        Read a numeric literal from the input.
        Supports integers and decimals.
        """
        start_pos = self.position
        num_str = ''
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        
        # Convert to appropriate numeric type
        value = float(num_str) if '.' in num_str else int(num_str)
        return Token(TokenType.NUMBER, value, start_pos)
    
    def read_string(self) -> Token:
        """
        Read a string literal enclosed in single quotes.
        Example: 'Hello World'
        """
        start_pos = self.position
        self.advance()  # Skip opening quote
        
        string_value = ''
        while self.current_char and self.current_char != "'":
            string_value += self.current_char
            self.advance()
        
        if self.current_char == "'":
            self.advance()  # Skip closing quote
        else:
            raise ValueError(f"Unterminated string at position {start_pos}")
        
        return Token(TokenType.STRING, string_value, start_pos)
    
    def read_identifier(self) -> Token:
        """
        Read an identifier (table name, column name) or keyword.
        Identifiers start with a letter or underscore and can contain letters, digits, and underscores.
        """
        start_pos = self.position
        identifier = ''
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            identifier += self.current_char
            self.advance()
        
        # Check if this identifier is actually a keyword
        identifier_upper = identifier.upper()
        token_type = self.KEYWORDS.get(identifier_upper, TokenType.IDENTIFIER)
        
        # For keywords, store the uppercase version; for identifiers, keep original case
        value = identifier_upper if token_type != TokenType.IDENTIFIER else identifier
        
        return Token(token_type, value, start_pos)
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire SQL statement.
        
        Returns:
            List of tokens representing the SQL statement
        """
        tokens = []
        
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Numbers
            if self.current_char.isdigit():
                tokens.append(self.read_number())
                continue
            
            # Strings (single-quoted)
            if self.current_char == "'":
                tokens.append(self.read_string())
                continue
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.read_identifier())
                continue
            
            # Operators and punctuation
            pos = self.position
            
            # Two-character operators
            if self.current_char == '>' and self.peek() == '=':
                tokens.append(Token(TokenType.GREATER_EQ, '>=', pos))
                self.advance()
                self.advance()
                continue
            
            if self.current_char == '<' and self.peek() == '=':
                tokens.append(Token(TokenType.LESS_EQ, '<=', pos))
                self.advance()
                self.advance()
                continue
            
            if self.current_char == '!' and self.peek() == '=':
                tokens.append(Token(TokenType.NOT_EQ, '!=', pos))
                self.advance()
                self.advance()
                continue
            
            # Single-character operators and delimiters
            char_map = {
                '=': TokenType.EQUALS,
                '>': TokenType.GREATER,
                '<': TokenType.LESS,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '*': TokenType.STAR,
            }
            
            if self.current_char in char_map:
                tokens.append(Token(char_map[self.current_char], self.current_char, pos))
                self.advance()
                continue
            
            # Unknown character
            raise ValueError(f"Unexpected character '{self.current_char}' at position {pos}")
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, None, self.position))
        return tokens
