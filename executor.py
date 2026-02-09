"""
Executor - Executes parsed SQL statements
This module takes the AST from the parser and executes it against the storage engine.
It handles the actual data manipulation and retrieval.
"""

from typing import List, Dict, Any, Union
from parser import (
    SelectStatement, InsertStatement, CreateTableStatement,
    WhereClause, Condition, CompoundCondition
)
from storage import StorageEngine


class QueryResult:
    """
    Represents the result of a SQL query.
    
    Contains:
    - columns: List of column names
    - rows: List of row data (each row is a dictionary)
    - rows_affected: Number of rows affected (for INSERT, UPDATE, DELETE)
    """
    
    def __init__(self, columns: List[str] = None, rows: List[Dict[str, Any]] = None, 
                 rows_affected: int = 0, message: str = None):
        self.columns = columns or []
        self.rows = rows or []
        self.rows_affected = rows_affected
        self.message = message
    
    def __str__(self) -> str:
        """Format the result as a readable string"""
        if self.message:
            return self.message
        
        if not self.rows:
            return f"({self.rows_affected} rows affected)"
        
        # Calculate column widths for pretty printing
        col_widths = {}
        for col in self.columns:
            col_widths[col] = len(col)
        
        for row in self.rows:
            for col in self.columns:
                value_str = str(row.get(col, ''))
                col_widths[col] = max(col_widths[col], len(value_str))
        
        # Build header
        header = ' | '.join(col.ljust(col_widths[col]) for col in self.columns)
        separator = '-+-'.join('-' * col_widths[col] for col in self.columns)
        
        # Build rows
        result_lines = [header, separator]
        for row in self.rows:
            row_str = ' | '.join(
                str(row.get(col, '')).ljust(col_widths[col]) 
                for col in self.columns
            )
            result_lines.append(row_str)
        
        result_lines.append(f"\n({len(self.rows)} rows)")
        return '\n'.join(result_lines)


class Executor:
    """
    Executes SQL statements against the storage engine.
    
    This class is responsible for:
    - Creating tables
    - Inserting data
    - Querying data with filtering and projection
    """
    
    def __init__(self, storage: StorageEngine):
        """
        Initialize the executor with a storage engine.
        
        Args:
            storage: The storage engine to execute queries against
        """
        self.storage = storage
    
    def execute(self, statement: Union[SelectStatement, InsertStatement, CreateTableStatement]) -> QueryResult:
        """
        Execute a SQL statement.
        
        Args:
            statement: The parsed AST node representing the SQL statement
            
        Returns:
            QueryResult containing the result of the execution
        """
        if isinstance(statement, SelectStatement):
            return self.execute_select(statement)
        elif isinstance(statement, InsertStatement):
            return self.execute_insert(statement)
        elif isinstance(statement, CreateTableStatement):
            return self.execute_create_table(statement)
        else:
            raise ValueError(f"Unknown statement type: {type(statement)}")
    
    def execute_create_table(self, statement: CreateTableStatement) -> QueryResult:
        """
        Execute a CREATE TABLE statement.
        
        Args:
            statement: The CREATE TABLE AST node
            
        Returns:
            QueryResult with a success message
        """
        self.storage.create_table(statement.table, statement.columns)
        return QueryResult(message=f"Table '{statement.table}' created successfully")
    
    def execute_insert(self, statement: InsertStatement) -> QueryResult:
        """
        Execute an INSERT statement.
        
        Args:
            statement: The INSERT AST node
            
        Returns:
            QueryResult with the number of rows affected
        """
        # Build a row dictionary from columns and values
        row = dict(zip(statement.columns, statement.values))
        
        self.storage.insert_row(statement.table, row)
        return QueryResult(rows_affected=1, message=f"1 row inserted into '{statement.table}'")
    
    def execute_select(self, statement: SelectStatement) -> QueryResult:
        """
        Execute a SELECT statement.
        
        This involves:
        1. Retrieving the table
        2. Filtering rows based on WHERE clause (if present)
        3. Projecting only the requested columns
        
        Args:
            statement: The SELECT AST node
            
        Returns:
            QueryResult with the selected rows
        """
        # Get the table
        table = self.storage.get_table(statement.table)
        if not table:
            raise ValueError(f"Table '{statement.table}' does not exist")
        
        # Start with all rows
        rows = table.rows.copy()
        
        # Apply WHERE clause filtering if present
        if statement.where:
            rows = [row for row in rows if self.evaluate_where(row, statement.where)]
        
        # Determine which columns to return
        if statement.columns == ['*']:
            columns = table.get_column_names()
        else:
            columns = statement.columns
            # Validate that requested columns exist
            table_columns = table.get_column_names()
            for col in columns:
                if col not in table_columns:
                    raise ValueError(f"Column '{col}' does not exist in table '{statement.table}'")
        
        # Project only the requested columns
        projected_rows = []
        for row in rows:
            projected_row = {col: row.get(col) for col in columns}
            projected_rows.append(projected_row)
        
        return QueryResult(columns=columns, rows=projected_rows)
    
    def evaluate_where(self, row: Dict[str, Any], where: WhereClause) -> bool:
        """
        Evaluate a WHERE clause against a row.
        
        This recursively evaluates compound conditions (AND/OR) and
        simple conditions (comparisons).
        
        Args:
            row: The row to evaluate
            where: The WHERE clause AST node
            
        Returns:
            True if the row matches the condition, False otherwise
        """
        if isinstance(where, Condition):
            return self.evaluate_condition(row, where)
        elif isinstance(where, CompoundCondition):
            left_result = self.evaluate_where(row, where.left)
            right_result = self.evaluate_where(row, where.right)
            
            if where.operator == 'AND':
                return left_result and right_result
            elif where.operator == 'OR':
                return left_result or right_result
            else:
                raise ValueError(f"Unknown logical operator: {where.operator}")
        else:
            raise ValueError(f"Unknown WHERE clause type: {type(where)}")
    
    def evaluate_condition(self, row: Dict[str, Any], condition: Condition) -> bool:
        """
        Evaluate a single comparison condition.
        
        Args:
            row: The row to evaluate
            condition: The condition to check
            
        Returns:
            True if the condition is met, False otherwise
        """
        # Get the column value from the row
        if condition.column not in row:
            raise ValueError(f"Column '{condition.column}' not found in row")
        
        row_value = row[condition.column]
        compare_value = condition.value
        
        # Perform the comparison based on the operator
        operator_map = {
            '=': lambda a, b: a == b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
        }
        
        if condition.operator not in operator_map:
            raise ValueError(f"Unknown operator: {condition.operator}")
        
        return operator_map[condition.operator](row_value, compare_value)
