"""
Storage Engine - Manages data persistence and table structures
This module handles how data is stored and retrieved from disk.
For simplicity, we use JSON files to store tables.
"""

import json
import os
from typing import Dict, List, Any, Optional
from parser import Column


class Table:
    """
    Represents a database table with its schema and data.
    
    Each table has:
    - A name
    - A schema (column definitions)
    - Rows of data
    """
    
    def __init__(self, name: str, columns: List[Column]):
        """
        Create a new table.
        
        Args:
            name: Table name
            columns: List of column definitions
        """
        self.name = name
        self.columns = columns
        self.rows: List[Dict[str, Any]] = []
    
    def get_column_names(self) -> List[str]:
        """Get a list of all column names in this table"""
        return [col.name for col in self.columns]
    
    def validate_row(self, row: Dict[str, Any]) -> bool:
        """
        Validate that a row conforms to the table schema.
        
        Checks:
        - All columns in the row exist in the schema
        - Data types match (basic type checking)
        
        Args:
            row: Dictionary mapping column names to values
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        column_names = self.get_column_names()
        
        # Check that all keys in the row exist as columns
        for key in row.keys():
            if key not in column_names:
                raise ValueError(f"Column '{key}' does not exist in table '{self.name}'")
        
        # Basic type validation
        for col in self.columns:
            if col.name in row:
                value = row[col.name]
                if col.data_type == 'INT':
                    if not isinstance(value, int):
                        raise ValueError(
                            f"Column '{col.name}' expects INT, got {type(value).__name__}"
                        )
                elif col.data_type == 'VARCHAR':
                    if not isinstance(value, str):
                        raise ValueError(
                            f"Column '{col.name}' expects VARCHAR, got {type(value).__name__}"
                        )
                    if col.size and len(value) > col.size:
                        raise ValueError(
                            f"Value for '{col.name}' exceeds maximum length of {col.size}"
                        )
        
        return True
    
    def insert(self, row: Dict[str, Any]):
        """
        Insert a new row into the table.
        
        Args:
            row: Dictionary mapping column names to values
        """
        self.validate_row(row)
        self.rows.append(row)
    
    def to_dict(self) -> Dict:
        """
        Serialize table to a dictionary for JSON storage.
        
        Returns:
            Dictionary representation of the table
        """
        return {
            'name': self.name,
            'columns': [
                {
                    'name': col.name,
                    'data_type': col.data_type,
                    'size': col.size
                }
                for col in self.columns
            ],
            'rows': self.rows
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Table':
        """
        Deserialize table from a dictionary.
        
        Args:
            data: Dictionary representation of a table
            
        Returns:
            Table instance
        """
        columns = [
            Column(
                name=col_data['name'],
                data_type=col_data['data_type'],
                size=col_data.get('size')
            )
            for col_data in data['columns']
        ]
        
        table = cls(name=data['name'], columns=columns)
        table.rows = data['rows']
        return table


class StorageEngine:
    """
    Manages database storage using JSON files.
    
    Each database is stored in a directory, with each table as a separate JSON file.
    This is a simple approach suitable for learning. Production databases use
    much more sophisticated storage formats for performance.
    """
    
    def __init__(self, db_path: str = './database'):
        """
        Initialize the storage engine.
        
        Args:
            db_path: Path to the directory where database files are stored
        """
        self.db_path = db_path
        self.tables: Dict[str, Table] = {}
        
        # Create database directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Load existing tables from disk
        self.load_database()
    
    def load_database(self):
        """
        Load all tables from disk into memory.
        
        Reads all .json files in the database directory and loads them as tables.
        """
        if not os.path.exists(self.db_path):
            return
        
        for filename in os.listdir(self.db_path):
            if filename.endswith('.json'):
                table_name = filename[:-5]  # Remove .json extension
                table_path = os.path.join(self.db_path, filename)
                
                with open(table_path, 'r') as f:
                    table_data = json.load(f)
                    self.tables[table_name] = Table.from_dict(table_data)
    
    def save_table(self, table: Table):
        """
        Save a table to disk.
        
        Args:
            table: The table to save
        """
        table_path = os.path.join(self.db_path, f"{table.name}.json")
        with open(table_path, 'w') as f:
            json.dump(table.to_dict(), f, indent=2)
    
    def create_table(self, name: str, columns: List[Column]):
        """
        Create a new table.
        
        Args:
            name: Table name
            columns: List of column definitions
        """
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        table = Table(name, columns)
        self.tables[name] = table
        self.save_table(table)
    
    def get_table(self, name: str) -> Optional[Table]:
        """
        Retrieve a table by name.
        
        Args:
            name: Table name
            
        Returns:
            Table instance or None if not found
        """
        return self.tables.get(name)
    
    def insert_row(self, table_name: str, row: Dict[str, Any]):
        """
        Insert a row into a table.
        
        Args:
            table_name: Name of the table
            row: Dictionary mapping column names to values
        """
        table = self.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table.insert(row)
        self.save_table(table)
    
    def table_exists(self, name: str) -> bool:
        """Check if a table exists"""
        return name in self.tables
    
    def list_tables(self) -> List[str]:
        """Get a list of all table names"""
        return list(self.tables.keys())
