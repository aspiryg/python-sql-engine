"""
SQL Engine - Main interface for executing SQL queries
This module provides the high-level API that users interact with.
It coordinates the lexer, parser, storage, and executor.
"""

from lexer import Lexer
from parser import Parser
from storage import StorageEngine
from executor import Executor, QueryResult


class SQLEngine:
    """
    The main SQL engine that processes SQL queries.
    
    This class provides a simple interface:
    - Initialize the engine with a database path
    - Execute SQL statements
    
    The engine handles the entire pipeline:
    SQL text → Lexer → Tokens → Parser → AST → Executor → Result
    """
    
    def __init__(self, db_path: str = './database'):
        """
        Initialize the SQL engine.
        
        Args:
            db_path: Path to the database directory
        """
        self.storage = StorageEngine(db_path)
        self.executor = Executor(self.storage)
    
    def execute(self, sql: str) -> QueryResult:
        """
        Execute a SQL statement.
        
        This method orchestrates the entire query processing pipeline:
        1. Tokenization (Lexer): Convert SQL text into tokens
        2. Parsing (Parser): Build an Abstract Syntax Tree from tokens
        3. Execution (Executor): Execute the AST against the storage engine
        
        Args:
            sql: The SQL statement to execute
            
        Returns:
            QueryResult containing the result of the query
        """
        try:
            # Step 1: Tokenize the SQL statement
            lexer = Lexer(sql)
            tokens = lexer.tokenize()
            
            # Step 2: Parse tokens into an AST
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Step 3: Execute the AST
            result = self.executor.execute(ast)
            
            return result
            
        except Exception as e:
            # Return error information in a QueryResult
            return QueryResult(message=f"Error: {str(e)}")
    
    def list_tables(self) -> list:
        """
        Get a list of all tables in the database.
        
        Returns:
            List of table names
        """
        return self.storage.list_tables()
    
    def describe_table(self, table_name: str) -> str:
        """
        Get information about a table's structure.
        
        Args:
            table_name: Name of the table
            
        Returns:
            String describing the table structure
        """
        table = self.storage.get_table(table_name)
        if not table:
            return f"Table '{table_name}' does not exist"
        
        result = [f"Table: {table_name}", "Columns:"]
        for col in table.columns:
            col_info = f"  - {col.name}: {col.data_type}"
            if col.size:
                col_info += f"({col.size})"
            result.append(col_info)
        
        result.append(f"\nTotal rows: {len(table.rows)}")
        return '\n'.join(result)


def main():
    """
    Main function demonstrating the SQL engine usage.
    This provides an interactive REPL (Read-Eval-Print Loop) for testing.
    """
    print("=" * 60)
    print("Simple SQL Engine - Learning Project")
    print("=" * 60)
    print("Supported commands:")
    print("  CREATE TABLE tablename (col1 INT, col2 VARCHAR(50))")
    print("  INSERT INTO tablename (col1, col2) VALUES (1, 'text')")
    print("  SELECT * FROM tablename")
    print("  SELECT col1, col2 FROM tablename WHERE col1 > 5")
    print("  .tables - List all tables")
    print("  .describe tablename - Show table structure")
    print("  .quit - Exit")
    print("=" * 60)
    print()
    
    # Initialize the SQL engine
    engine = SQLEngine()
    
    # Interactive loop
    while True:
        try:
            # Get SQL input from user
            sql = input("sql> ").strip()
            
            if not sql:
                continue
            
            # Handle special commands
            if sql == '.quit':
                print("Goodbye!")
                break
            elif sql == '.tables':
                tables = engine.list_tables()
                if tables:
                    print("Tables:")
                    for table in tables:
                        print(f"  - {table}")
                else:
                    print("No tables found")
                continue
            elif sql.startswith('.describe '):
                table_name = sql.split()[1]
                print(engine.describe_table(table_name))
                continue
            
            # Execute SQL statement
            result = engine.execute(sql)
            print(result)
            print()
            
        except KeyboardInterrupt:
            print("\nUse .quit to exit")
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
