# Simple SQL Engine - Learning Project

A basic SQL database engine built from scratch in Python for educational purposes. This project demonstrates how a SQL database works under the hood.

## 🎯 Features

- **CREATE TABLE**: Define tables with INT and VARCHAR columns
- **INSERT**: Add data to tables
- **SELECT**: Query data with column selection
- **WHERE**: Filter results with conditions (=, >, <, >=, <=, !=)
- **Compound Conditions**: Use AND/OR in WHERE clauses
- **Data Persistence**: Tables stored as JSON files

## 📚 Architecture

The SQL engine consists of five main components:

### 1. **Lexer** (`lexer.py`)
**Purpose**: Converts raw SQL text into tokens

The lexer is the first stage of processing. It reads the SQL statement character by character and groups them into meaningful units called tokens.

**Example**:
```
Input:  "SELECT name FROM users WHERE age > 18"
Output: [SELECT, IDENTIFIER(name), FROM, IDENTIFIER(users), WHERE, IDENTIFIER(age), >, NUMBER(18)]
```

**Key Components**:
- `TokenType`: Enum defining all possible token types (keywords, operators, literals, etc.)
- `Token`: Data class representing a single token with its type, value, and position
- `Lexer`: Main class that scans through the SQL text

**How it works**:
1. Skips whitespace
2. Recognizes numbers (integers and decimals)
3. Recognizes strings (single-quoted)
4. Recognizes identifiers (table/column names) and keywords
5. Recognizes operators (=, >, <, etc.) and punctuation (parentheses, commas)

### 2. **Parser** (`parser.py`)
**Purpose**: Builds an Abstract Syntax Tree (AST) from tokens

The parser takes the flat list of tokens and organizes them into a tree structure that represents the meaning and structure of the SQL statement.

**Example**:
```
Tokens: [SELECT, name, FROM, users]
AST:    SelectStatement(
          columns=['name'],
          table='users',
          where=None
        )
```

**Key Components**:
- AST Node Classes: `SelectStatement`, `InsertStatement`, `CreateTableStatement`, `Condition`, `CompoundCondition`
- `Parser`: Main class that implements recursive descent parsing

**How it works**:
1. Determines statement type (SELECT, INSERT, CREATE TABLE)
2. Calls appropriate parsing method
3. Validates syntax (ensures required keywords are present)
4. Builds hierarchical structure representing the query

**Why AST?**: The tree structure makes it easy to understand and execute complex queries with nested conditions.

### 3. **Storage Engine** (`storage.py`)
**Purpose**: Manages data persistence and table structures

The storage engine handles how data is stored on disk and loaded into memory.

**Key Components**:
- `Column`: Represents a column definition (name, type, size)
- `Table`: Represents a table with its schema and data rows
- `StorageEngine`: Manages multiple tables and disk I/O

**How it works**:
1. Each table is stored as a JSON file in the database directory
2. On startup, all tables are loaded into memory
3. When data changes (INSERT, CREATE TABLE), the corresponding file is updated
4. Schema validation ensures data integrity

**Data Format** (JSON):
```json
{
  "name": "users",
  "columns": [
    {"name": "id", "data_type": "INT", "size": null},
    {"name": "name", "data_type": "VARCHAR", "size": 50}
  ],
  "rows": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

### 4. **Executor** (`executor.py`)
**Purpose**: Executes parsed SQL statements against the storage engine

The executor is where the actual work happens - it takes the AST and performs the requested operations.

**Key Components**:
- `QueryResult`: Holds the result of a query (columns, rows, message)
- `Executor`: Executes different statement types

**How it works**:

**For CREATE TABLE**:
1. Calls storage engine to create a new table
2. Returns success message

**For INSERT**:
1. Builds a row dictionary from columns and values
2. Validates against table schema
3. Calls storage engine to add the row
4. Returns rows affected

**For SELECT**:
1. Retrieves the table from storage
2. Applies WHERE clause filtering (if present)
3. Projects requested columns (or all columns if SELECT *)
4. Returns result set

**WHERE Clause Evaluation**:
- Recursively evaluates compound conditions (AND/OR)
- Compares row values against condition values using appropriate operators
- Returns only rows that match all conditions

### 5. **SQL Engine** (`sql_engine.py`)
**Purpose**: Main interface that ties everything together

This is the user-facing component that provides a simple API for executing SQL.

**Pipeline**:
```
SQL String → Lexer → Tokens → Parser → AST → Executor → Result
```

**Interactive Features**:
- `.tables`: List all tables
- `.describe tablename`: Show table structure
- `.quit`: Exit the REPL

## 🚀 Usage

### Interactive Mode (REPL)

```bash
python sql_engine.py
```

Then type SQL commands:

```sql
sql> CREATE TABLE users (id INT, name VARCHAR(50), age INT)
Table 'users' created successfully

sql> INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25)
1 row inserted into 'users'

sql> INSERT INTO users (id, name, age) VALUES (2, 'Bob', 30)
1 row inserted into 'users'

sql> SELECT * FROM users
id | name  | age
---+-------+----
1  | Alice | 25
2  | Bob   | 30

(2 rows)

sql> SELECT name, age FROM users WHERE age > 26
name | age
-----+----
Bob  | 30

(1 rows)

sql> .tables
Tables:
  - users

sql> .describe users
Table: users
Columns:
  - id: INT
  - name: VARCHAR(50)
  - age: INT

Total rows: 2
```

### Programmatic Usage

```python
from sql_engine import SQLEngine

# Initialize engine
engine = SQLEngine(db_path='./my_database')

# Create a table
result = engine.execute("CREATE TABLE products (id INT, name VARCHAR(100), price INT)")
print(result)

# Insert data
engine.execute("INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 999)")
engine.execute("INSERT INTO products (id, name, price) VALUES (2, 'Mouse', 25)")

# Query data
result = engine.execute("SELECT * FROM products WHERE price < 500")
print(result)

# List tables
tables = engine.list_tables()
print(tables)
```

## 📖 Detailed Component Breakdown

### Token Types
- **Keywords**: SELECT, FROM, WHERE, INSERT, INTO, VALUES, CREATE, TABLE, INT, VARCHAR, AND, OR
- **Literals**: Numbers (42, 3.14), Strings ('hello')
- **Identifiers**: Table and column names
- **Operators**: =, >, <, >=, <=, !=
- **Delimiters**: (, ), ,, ;, *

### Supported SQL Syntax

**CREATE TABLE**:
```sql
CREATE TABLE table_name (
  column1 INT,
  column2 VARCHAR(size),
  ...
)
```

**INSERT**:
```sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...)
```

**SELECT**:
```sql
SELECT column1, column2 FROM table_name
SELECT * FROM table_name
SELECT columns FROM table_name WHERE condition
SELECT columns FROM table_name WHERE condition1 AND condition2
SELECT columns FROM table_name WHERE condition1 OR condition2
```

### WHERE Clause Operators
- `=`: Equal
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal
- `<=`: Less than or equal
- `!=`: Not equal

### Logical Operators
- `AND`: Both conditions must be true
- `OR`: At least one condition must be true

## 🔍 How Query Execution Works

Let's trace a query through the entire pipeline:

**Query**: `SELECT name FROM users WHERE age > 18 AND age < 65`

### Step 1: Lexing
```
Input: "SELECT name FROM users WHERE age > 18 AND age < 65"
Output Tokens:
[
  Token(SELECT, "SELECT", 0),
  Token(IDENTIFIER, "name", 7),
  Token(FROM, "FROM", 12),
  Token(IDENTIFIER, "users", 17),
  Token(WHERE, "WHERE", 23),
  Token(IDENTIFIER, "age", 29),
  Token(GREATER, ">", 33),
  Token(NUMBER, 18, 35),
  Token(AND, "AND", 38),
  Token(IDENTIFIER, "age", 42),
  Token(LESS, "<", 46),
  Token(NUMBER, 65, 48),
  Token(EOF, None, 50)
]
```

### Step 2: Parsing
```
AST:
SelectStatement(
  columns=['name'],
  table='users',
  where=CompoundCondition(
    left=Condition(column='age', operator='>', value=18),
    operator='AND',
    right=Condition(column='age', operator='<', value=65)
  )
)
```

### Step 3: Execution
1. Load 'users' table from storage
2. For each row:
   - Evaluate: age > 18
   - Evaluate: age < 65
   - If both true (AND), include row
3. Project only 'name' column
4. Return result set

## 🎓 Learning Objectives

This project demonstrates:

1. **Lexical Analysis**: How to tokenize text input
2. **Parsing**: Building tree structures from linear token streams
3. **Abstract Syntax Trees**: Representing program structure
4. **Data Structures**: Tables, rows, columns
5. **Query Execution**: Filtering, projection, logical operations
6. **Data Persistence**: Serialization and deserialization
7. **Software Architecture**: Separation of concerns, modular design

## 🔧 Limitations (By Design)

This is a learning project, so many features of production databases are intentionally omitted:

- No transactions or ACID guarantees
- No indexes (all queries are table scans)
- No UPDATE or DELETE statements
- No JOINs between tables
- No aggregations (COUNT, SUM, AVG, etc.)
- No GROUP BY or ORDER BY
- No subqueries
- Limited data types (only INT and VARCHAR)
- No NULL values
- No primary keys or foreign keys
- No concurrent access handling
- Simple JSON storage (not optimized for performance)

## 🚀 Possible Extensions

Ideas for learning more:

1. **Add UPDATE and DELETE**: Modify or remove existing rows
2. **Add Indexes**: B-tree indexes for faster lookups
3. **Add JOIN**: Combine data from multiple tables
4. **Add Aggregations**: COUNT, SUM, AVG, MIN, MAX
5. **Add ORDER BY**: Sort results
6. **Add GROUP BY**: Group and aggregate data
7. **Better Storage**: Use a binary format instead of JSON
8. **Add Transactions**: Implement BEGIN, COMMIT, ROLLBACK
9. **Query Optimization**: Plan and optimize query execution
10. **Add More Data Types**: BOOLEAN, DATE, FLOAT, etc.

## 📝 File Structure

```
sql_engine/
├── lexer.py          # Tokenization
├── parser.py         # AST construction
├── storage.py        # Data persistence
├── executor.py       # Query execution
├── sql_engine.py     # Main interface
└── database/         # Storage directory (created automatically)
    └── *.json        # Table files
```

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new features
- Improve error messages
- Add more comprehensive validation
- Optimize performance
- Add tests

## 📄 License

This project is for educational purposes. Use it freely to learn!
