"""
Parser - Builds an Abstract Syntax Tree (AST) from tokens
The parser takes the tokens from the lexer and organizes them into a tree structure
that represents the meaning of the SQL statement.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from lexer import Token, TokenType


# AST Node classes - each represents a different part of a SQL statement

@dataclass
class Column:
    """Represents a column in a table definition or selection"""
    name: str
    data_type: Optional[str] = None  # For CREATE TABLE (e.g., 'INT', 'VARCHAR')
    size: Optional[int] = None        # For VARCHAR(50), size would be 50


@dataclass
class SelectStatement:
    """
    Represents a SELECT query.
    Example: SELECT name, age FROM users WHERE age > 18
    """
    columns: List[str]  # Column names to select, or ['*'] for all columns
    table: str          # Table name to select from
    where: Optional['WhereClause'] = None  # Optional WHERE clause for filtering


@dataclass
class InsertStatement:
    """
    Represents an INSERT query.
    Example: INSERT INTO users (name, age) VALUES ('Alice', 25)
    """
    table: str           # Table name to insert into
    columns: List[str]   # Column names
    values: List[any]    # Values to insert


@dataclass
class CreateTableStatement:
    """
    Represents a CREATE TABLE statement.
    Example: CREATE TABLE users (id INT, name VARCHAR(50))
    """
    table: str          # Table name
    columns: List[Column]  # Column definitions


@dataclass
class WhereClause:
    """
    Represents a WHERE clause with conditions.
    Can be a simple condition (column = value) or compound (condition AND/OR condition)
    """
    pass


@dataclass
class Condition(WhereClause):
    """
    A single comparison condition.
    Example: age > 18, name = 'Alice'
    """
    column: str      # Column name
    operator: str    # Comparison operator (=, >, <, >=, <=, !=)
    value: any       # Value to compare against


@dataclass
class CompoundCondition(WhereClause):
    """
    Multiple conditions joined by AND/OR.
    Example: age > 18 AND name = 'Alice'
    """
    left: WhereClause    # Left condition
    operator: str        # 'AND' or 'OR'
    right: WhereClause   # Right condition


class Parser:
    """
    Parses tokens into an Abstract Syntax Tree (AST).
    
    The parser implements a recursive descent parser, which means it processes
    tokens from left to right and builds the tree structure by calling methods
    that correspond to grammar rules.
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize the parser with a list of tokens.
        
        Args:
            tokens: List of tokens from the lexer
        """
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to the next token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def expect(self, token_type: TokenType) -> Token:
        """
        Verify that the current token is of the expected type, then consume it.
        
        Args:
            token_type: The expected token type
            
        Returns:
            The consumed token
            
        Raises:
            ValueError: If the current token doesn't match the expected type
        """
        if self.current_token.type != token_type:
            raise ValueError(
                f"Expected {token_type}, got {self.current_token.type} "
                f"at position {self.current_token.position}"
            )
        token = self.current_token
        self.advance()
        return token
    
    def parse(self) -> Union[SelectStatement, InsertStatement, CreateTableStatement]:
        """
        Parse the tokens into an AST.
        
        This is the entry point for parsing. It determines what type of statement
        we're dealing with and delegates to the appropriate parsing method.
        
        Returns:
            An AST node representing the SQL statement
        """
        if self.current_token.type == TokenType.SELECT:
            return self.parse_select()
        elif self.current_token.type == TokenType.INSERT:
            return self.parse_insert()
        elif self.current_token.type == TokenType.CREATE:
            return self.parse_create_table()
        else:
            raise ValueError(f"Unexpected statement starting with {self.current_token.type}")
    
    def parse_select(self) -> SelectStatement:
        """
        Parse a SELECT statement.
        Grammar: SELECT columns FROM table [WHERE conditions]
        """
        self.expect(TokenType.SELECT)
        
        # Parse column list
        columns = []
        if self.current_token.type == TokenType.STAR:
            columns.append('*')
            self.advance()
        else:
            # Read comma-separated column names
            columns.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token.type == TokenType.COMMA:
                self.advance()  # Skip comma
                columns.append(self.expect(TokenType.IDENTIFIER).value)
        
        # Parse FROM clause
        self.expect(TokenType.FROM)
        table = self.expect(TokenType.IDENTIFIER).value
        
        # Parse optional WHERE clause
        where = None
        if self.current_token.type == TokenType.WHERE:
            self.advance()
            where = self.parse_where()
        
        return SelectStatement(columns=columns, table=table, where=where)
    
    def parse_insert(self) -> InsertStatement:
        """
        Parse an INSERT statement.
        Grammar: INSERT INTO table (columns) VALUES (values)
        """
        self.expect(TokenType.INSERT)
        self.expect(TokenType.INTO)
        
        # Get table name
        table = self.expect(TokenType.IDENTIFIER).value
        
        # Parse column list in parentheses
        self.expect(TokenType.LPAREN)
        columns = []
        columns.append(self.expect(TokenType.IDENTIFIER).value)
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            columns.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.RPAREN)
        
        # Parse VALUES keyword and value list
        self.expect(TokenType.VALUES)
        self.expect(TokenType.LPAREN)
        values = []
        values.append(self.parse_value())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            values.append(self.parse_value())
        self.expect(TokenType.RPAREN)
        
        return InsertStatement(table=table, columns=columns, values=values)
    
    def parse_create_table(self) -> CreateTableStatement:
        """
        Parse a CREATE TABLE statement.
        Grammar: CREATE TABLE table_name (column_definitions)
        """
        self.expect(TokenType.CREATE)
        self.expect(TokenType.TABLE)
        
        # Get table name
        table = self.expect(TokenType.IDENTIFIER).value
        
        # Parse column definitions
        self.expect(TokenType.LPAREN)
        columns = []
        columns.append(self.parse_column_definition())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            columns.append(self.parse_column_definition())
        self.expect(TokenType.RPAREN)
        
        return CreateTableStatement(table=table, columns=columns)
    
    def parse_column_definition(self) -> Column:
        """
        Parse a column definition in a CREATE TABLE statement.
        Examples: 
            id INT
            name VARCHAR(50)
        """
        column_name = self.expect(TokenType.IDENTIFIER).value
        
        # Get data type
        if self.current_token.type == TokenType.INT:
            data_type = 'INT'
            self.advance()
            return Column(name=column_name, data_type=data_type)
        elif self.current_token.type == TokenType.VARCHAR:
            data_type = 'VARCHAR'
            self.advance()
            
            # Check for size specification VARCHAR(50)
            size = None
            if self.current_token.type == TokenType.LPAREN:
                self.advance()
                size = self.expect(TokenType.NUMBER).value
                self.expect(TokenType.RPAREN)
            
            return Column(name=column_name, data_type=data_type, size=size)
        else:
            raise ValueError(f"Expected data type, got {self.current_token.type}")
    
    def parse_where(self) -> WhereClause:
        """
        Parse a WHERE clause with conditions.
        Supports AND/OR operators for compound conditions.
        """
        # Parse the first condition
        left = self.parse_condition()
        
        # Check for AND/OR to create compound conditions
        while self.current_token.type in (TokenType.AND, TokenType.OR):
            operator = self.current_token.value
            self.advance()
            right = self.parse_condition()
            left = CompoundCondition(left=left, operator=operator, right=right)
        
        return left
    
    def parse_condition(self) -> Condition:
        """
        Parse a single comparison condition.
        Example: age > 18, name = 'Alice'
        """
        column = self.expect(TokenType.IDENTIFIER).value
        
        # Get comparison operator
        operator_map = {
            TokenType.EQUALS: '=',
            TokenType.GREATER: '>',
            TokenType.LESS: '<',
            TokenType.GREATER_EQ: '>=',
            TokenType.LESS_EQ: '<=',
            TokenType.NOT_EQ: '!=',
        }
        
        if self.current_token.type not in operator_map:
            raise ValueError(f"Expected comparison operator, got {self.current_token.type}")
        
        operator = operator_map[self.current_token.type]
        self.advance()
        
        # Get the value to compare against
        value = self.parse_value()
        
        return Condition(column=column, operator=operator, value=value)
    
    def parse_value(self) -> any:
        """
        Parse a literal value (number or string).
        """
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return value
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return value
        else:
            raise ValueError(f"Expected value, got {self.current_token.type}")
