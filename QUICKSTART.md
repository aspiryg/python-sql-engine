# Quick Start Guide

## Installation

No installation required! Just Python 3.6+.

## Running the Interactive Shell

```bash
python sql_engine.py
```

## Your First Commands

Once in the shell, try these commands:

### 1. Create a table
```sql
CREATE TABLE students (id INT, name VARCHAR(50), grade INT)
```

### 2. Insert some data
```sql
INSERT INTO students (id, name, grade) VALUES (1, 'Alice', 95)
INSERT INTO students (id, name, grade) VALUES (2, 'Bob', 87)
INSERT INTO students (id, name, grade) VALUES (3, 'Charlie', 92)
```

### 3. Query the data
```sql
SELECT * FROM students
```

### 4. Filter with WHERE
```sql
SELECT name, grade FROM students WHERE grade > 90
```

### 5. Use special commands
```
.tables              -- List all tables
.describe students   -- Show table structure
.quit                -- Exit
```

## Using in Your Code

```python
from sql_engine import SQLEngine

# Create engine
engine = SQLEngine()

# Execute SQL
result = engine.execute("CREATE TABLE test (id INT, value VARCHAR(20))")
print(result)

result = engine.execute("INSERT INTO test (id, value) VALUES (1, 'hello')")
print(result)

result = engine.execute("SELECT * FROM test")
print(result)
```

## What You Can Do

✅ CREATE TABLE with INT and VARCHAR columns
✅ INSERT rows into tables
✅ SELECT with column selection
✅ WHERE clauses with =, >, <, >=, <=, !=
✅ AND/OR conditions
✅ Data validation (types and sizes)
✅ Persistent storage (tables saved as JSON)

## What's Not Implemented

❌ UPDATE and DELETE
❌ JOINs
❌ GROUP BY, ORDER BY
❌ Aggregations (COUNT, SUM, AVG)
❌ Indexes
❌ Transactions

## Example Queries

```sql
-- Create a table
CREATE TABLE books (id INT, title VARCHAR(100), year INT, rating INT)

-- Insert data
INSERT INTO books (id, title, year, rating) VALUES (1, 'The Great Gatsby', 1925, 5)
INSERT INTO books (id, title, year, rating) VALUES (2, '1984', 1949, 5)
INSERT INTO books (id, title, year, rating) VALUES (3, 'To Kill a Mockingbird', 1960, 4)

-- Query all books
SELECT * FROM books

-- Find books with 5-star rating
SELECT title, year FROM books WHERE rating = 5

-- Find books published after 1940
SELECT title, year FROM books WHERE year > 1940

-- Find 5-star books published after 1940
SELECT title, year, rating FROM books WHERE rating = 5 AND year > 1940
```

## File Structure

After running, you'll see:
```
sql_engine/
├── lexer.py              # Tokenization
├── parser.py             # AST construction  
├── storage.py            # Data storage
├── executor.py           # Query execution
├── sql_engine.py         # Main interface
├── examples.py           # Usage examples
├── test.py               # Tests
├── README.md             # Full documentation
├── QUICKSTART.md         # This file
└── database/             # Your data (created automatically)
    ├── students.json
    ├── books.json
    └── ...
```

## Troubleshooting

**Problem**: "Table already exists"
**Solution**: Tables persist between runs. Delete the `database/` folder to start fresh.

**Problem**: "Column does not exist"
**Solution**: Check spelling and case. Column names are case-sensitive.

**Problem**: "Expected INT, got str"
**Solution**: Make sure values match the column types. Numbers should not be in quotes.

## Next Steps

1. Read the full [README.md](README.md) for detailed architecture explanation
2. Run `python examples.py` to see all features in action
3. Try modifying the code to add new features!
4. Look at `test.py` for examples of programmatic usage

## Learning Resources

To understand how this works:
1. Start with `lexer.py` - see how SQL text becomes tokens
2. Then `parser.py` - see how tokens become a tree structure
3. Then `storage.py` - see how data is stored
4. Then `executor.py` - see how queries are executed
5. Finally `sql_engine.py` - see how it all connects

Have fun learning! 🚀
