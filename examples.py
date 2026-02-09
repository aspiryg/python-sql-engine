"""
Example usage of the SQL Engine
This script demonstrates all the basic features of our SQL engine.
"""

from sql_engine import SQLEngine


def print_section(title):
    """Helper to print section headers"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    # Initialize the SQL engine with a test database
    print("Initializing SQL Engine...")
    engine = SQLEngine(db_path='./test_database')
    
    # ========================================================================
    # Example 1: CREATE TABLE
    # ========================================================================
    print_section("Example 1: CREATE TABLE")
    
    # Create a users table
    sql = "CREATE TABLE users (id INT, name VARCHAR(50), age INT)"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Create a products table
    sql = "CREATE TABLE products (id INT, name VARCHAR(100), price INT, stock INT)"
    print(f"\nSQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # ========================================================================
    # Example 2: INSERT DATA
    # ========================================================================
    print_section("Example 2: INSERT DATA")
    
    # Insert users
    users_data = [
        "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)",
        "INSERT INTO users (id, name, age) VALUES (2, 'Bob', 30)",
        "INSERT INTO users (id, name, age) VALUES (3, 'Charlie', 35)",
        "INSERT INTO users (id, name, age) VALUES (4, 'Diana', 28)",
        "INSERT INTO users (id, name, age) VALUES (5, 'Eve', 22)",
    ]
    
    for sql in users_data:
        print(f"SQL: {sql}")
        result = engine.execute(sql)
        print(result)
    
    # Insert products
    print()
    products_data = [
        "INSERT INTO products (id, name, price, stock) VALUES (1, 'Laptop', 999, 10)",
        "INSERT INTO products (id, name, price, stock) VALUES (2, 'Mouse', 25, 50)",
        "INSERT INTO products (id, name, price, stock) VALUES (3, 'Keyboard', 75, 30)",
        "INSERT INTO products (id, name, price, stock) VALUES (4, 'Monitor', 300, 15)",
        "INSERT INTO products (id, name, price, stock) VALUES (5, 'Headphones', 150, 20)",
    ]
    
    for sql in products_data:
        print(f"SQL: {sql}")
        result = engine.execute(sql)
        print(result)
    
    # ========================================================================
    # Example 3: SELECT * (All columns)
    # ========================================================================
    print_section("Example 3: SELECT * (All columns)")
    
    sql = "SELECT * FROM users"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # ========================================================================
    # Example 4: SELECT specific columns
    # ========================================================================
    print_section("Example 4: SELECT specific columns")
    
    sql = "SELECT name, age FROM users"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # ========================================================================
    # Example 5: SELECT with WHERE clause (single condition)
    # ========================================================================
    print_section("Example 5: SELECT with WHERE (single condition)")
    
    # Greater than
    sql = "SELECT name, age FROM users WHERE age > 26"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Equal
    print()
    sql = "SELECT * FROM products WHERE price = 150"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Less than
    print()
    sql = "SELECT name, price FROM products WHERE price < 100"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # ========================================================================
    # Example 6: SELECT with WHERE clause (compound conditions)
    # ========================================================================
    print_section("Example 6: SELECT with WHERE (compound conditions)")
    
    # AND condition
    sql = "SELECT name, age FROM users WHERE age > 23 AND age < 32"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # OR condition
    print()
    sql = "SELECT name, price FROM products WHERE price < 50 OR price > 500"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Complex compound condition
    print()
    sql = "SELECT name, price, stock FROM products WHERE price > 50 AND stock > 15"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # ========================================================================
    # Example 7: All comparison operators
    # ========================================================================
    print_section("Example 7: All comparison operators")
    
    operators = [
        (">=", "SELECT name, age FROM users WHERE age >= 28"),
        ("<=", "SELECT name, age FROM users WHERE age <= 28"),
        ("!=", "SELECT name, price FROM products WHERE price != 25"),
    ]
    
    for op, sql in operators:
        print(f"\nOperator '{op}':")
        print(f"SQL: {sql}")
        result = engine.execute(sql)
        print(result)
    
    # ========================================================================
    # Example 8: Utility functions
    # ========================================================================
    print_section("Example 8: Utility functions")
    
    # List all tables
    print("List all tables:")
    tables = engine.list_tables()
    for table in tables:
        print(f"  - {table}")
    
    # Describe table structure
    print("\nDescribe 'users' table:")
    description = engine.describe_table('users')
    print(description)
    
    print("\nDescribe 'products' table:")
    description = engine.describe_table('products')
    print(description)
    
    # ========================================================================
    # Example 9: Error handling
    # ========================================================================
    print_section("Example 9: Error handling")
    
    # Non-existent table
    sql = "SELECT * FROM nonexistent"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Non-existent column
    print()
    sql = "SELECT invalid_column FROM users"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Invalid syntax
    print()
    sql = "SELECT name FROM"  # Missing table name
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    # Type mismatch
    print()
    sql = "INSERT INTO users (id, name, age) VALUES ('not a number', 'Test', 25)"
    print(f"SQL: {sql}")
    result = engine.execute(sql)
    print(result)
    
    print("\n" + "=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
