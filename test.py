"""
Simple test script for the SQL Engine
Demonstrates basic programmatic usage
"""

from sql_engine import SQLEngine


def test_basic_operations():
    """Test basic SQL operations"""
    
    # Create engine instance
    engine = SQLEngine(db_path='./demo_database')
    
    print("Testing Basic SQL Operations\n")
    
    # 1. Create a table
    print("1. Creating 'employees' table...")
    result = engine.execute("""
        CREATE TABLE employees (
            id INT,
            name VARCHAR(100),
            department VARCHAR(50),
            salary INT
        )
    """)
    print(result)
    print()
    
    # 2. Insert some data
    print("2. Inserting employee records...")
    employees = [
        (1, 'John Smith', 'Engineering', 75000),
        (2, 'Jane Doe', 'Marketing', 65000),
        (3, 'Bob Johnson', 'Engineering', 80000),
        (4, 'Alice Williams', 'Sales', 70000),
        (5, 'Charlie Brown', 'Engineering', 72000),
    ]
    
    for emp_id, name, dept, salary in employees:
        sql = f"INSERT INTO employees (id, name, department, salary) VALUES ({emp_id}, '{name}', '{dept}', {salary})"
        result = engine.execute(sql)
        print(f"  {result.message}")
    print()
    
    # 3. Query all employees
    print("3. Querying all employees:")
    result = engine.execute("SELECT * FROM employees")
    print(result)
    print()
    
    # 4. Query with filtering
    print("4. Finding employees in Engineering:")
    result = engine.execute("SELECT name, salary FROM employees WHERE department = 'Engineering'")
    print(result)
    print()
    
    # 5. Query with salary filter
    print("5. Finding employees earning more than $70,000:")
    result = engine.execute("SELECT name, department, salary FROM employees WHERE salary > 70000")
    print(result)
    print()
    
    # 6. Query with compound condition
    print("6. Finding Engineering employees earning more than $70,000:")
    result = engine.execute(
        "SELECT name, salary FROM employees WHERE department = 'Engineering' AND salary > 70000"
    )
    print(result)
    print()
    
    # 7. Show table structure
    print("7. Table structure:")
    print(engine.describe_table('employees'))
    print()


def test_data_validation():
    """Test that data validation works correctly"""
    
    engine = SQLEngine(db_path='./validation_test')
    
    print("\nTesting Data Validation\n")
    
    # Create a table with size constraints
    print("Creating table with VARCHAR(10) constraint...")
    engine.execute("CREATE TABLE test (id INT, code VARCHAR(10))")
    
    # Test valid data
    print("\nInserting valid data (code = 'ABC')...")
    result = engine.execute("INSERT INTO test (id, code) VALUES (1, 'ABC')")
    print(result)
    
    # Test invalid data (string too long)
    print("\nAttempting to insert invalid data (code = 'VERYLONGCODE123')...")
    result = engine.execute("INSERT INTO test (id, code) VALUES (2, 'VERYLONGCODE123')")
    print(result)
    
    # Test type mismatch
    print("\nAttempting to insert wrong type (id = 'not_a_number')...")
    result = engine.execute("INSERT INTO test (id, code) VALUES ('not_a_number', 'XYZ')")
    print(result)
    print()


if __name__ == '__main__':
    test_basic_operations()
    test_data_validation()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
