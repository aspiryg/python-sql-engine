# SQL Engine Architecture Overview

## High-Level Data Flow

```
   User Input (SQL String)
         |
         v
    ┌─────────┐
    │  LEXER  │ ← Breaks SQL text into tokens
    └────┬────┘
         │ [Tokens]
         v
    ┌─────────┐
    │ PARSER  │ ← Organizes tokens into Abstract Syntax Tree (AST)
    └────┬────┘
         │ [AST]
         v
    ┌──────────┐
    │ EXECUTOR │ ← Executes the AST against storage
    └────┬─────┘
         │ [Result]
         v
   ┌──────────────┐
   │ Query Result │ ← Formatted output
   └──────────────┘
```

## Component Breakdown

### 1. LEXER (lexer.py)
```
Input:  "SELECT name FROM users WHERE age > 18"

Process: Character-by-character scanning
         ↓
         Recognizes patterns:
         - Keywords (SELECT, FROM, WHERE)
         - Identifiers (name, users, age)
         - Operators (>)
         - Literals (18)

Output: [
    Token(SELECT, "SELECT", pos=0),
    Token(IDENTIFIER, "name", pos=7),
    Token(FROM, "FROM", pos=12),
    Token(IDENTIFIER, "users", pos=17),
    Token(WHERE, "WHERE", pos=23),
    Token(IDENTIFIER, "age", pos=29),
    Token(GREATER, ">", pos=33),
    Token(NUMBER, 18, pos=35)
]
```

### 2. PARSER (parser.py)
```
Input: Token stream from lexer

Process: Recursive descent parsing
         ↓
         Builds hierarchical structure

Output: SelectStatement(
    columns = ['name'],
    table = 'users',
    where = Condition(
        column = 'age',
        operator = '>',
        value = 18
    )
)

Tree Representation:
        SelectStatement
        /      |       \
   columns   table    where
      |        |        |
   ['name'] 'users' Condition
                     /    |    \
                 column  op  value
                   |     |     |
                 'age'  '>'   18
```

### 3. STORAGE ENGINE (storage.py)
```
In-Memory Structure:
┌─────────────────────────────────┐
│   StorageEngine                 │
│  ┌───────────────────────────┐  │
│  │ tables = {                │  │
│  │   'users': Table(...)     │  │
│  │   'products': Table(...)  │  │
│  │ }                         │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘

Table Structure:
┌──────────────────────────────┐
│ Table: 'users'               │
├──────────────────────────────┤
│ Columns:                     │
│  - id: INT                   │
│  - name: VARCHAR(50)         │
│  - age: INT                  │
├──────────────────────────────┤
│ Rows:                        │
│  [                           │
│    {id: 1, name: 'Alice', age: 25},│
│    {id: 2, name: 'Bob', age: 30},  │
│  ]                           │
└──────────────────────────────┘

Disk Storage (JSON):
database/
├── users.json
│   {
│     "name": "users",
│     "columns": [...],
│     "rows": [...]
│   }
└── products.json
    {
      "name": "products",
      "columns": [...],
      "rows": [...]
    }
```

### 4. EXECUTOR (executor.py)
```
Input: AST from parser

SELECT Execution Flow:
1. Get table from storage
   users_table = storage.get_table('users')

2. Apply WHERE filtering
   filtered_rows = []
   for row in users_table.rows:
       if evaluate_where(row, ast.where):  # age > 18
           filtered_rows.append(row)

3. Project columns
   result_rows = []
   for row in filtered_rows:
       result_rows.append({
           col: row[col] for col in ast.columns  # ['name']
       })

4. Return QueryResult
   QueryResult(
       columns=['name'],
       rows=result_rows
   )

Output: QueryResult
```

## Query Execution Example

Let's trace: `SELECT name FROM users WHERE age > 18 AND age < 65`

### Step 1: Lexing
```
"SELECT name FROM users WHERE age > 18 AND age < 65"
                    ↓
[SELECT] [name] [FROM] [users] [WHERE] [age] [>] [18] [AND] [age] [<] [65] [EOF]
```

### Step 2: Parsing
```
SelectStatement
├── columns: ['name']
├── table: 'users'
└── where: CompoundCondition
           ├── operator: 'AND'
           ├── left: Condition(age > 18)
           └── right: Condition(age < 65)
```

### Step 3: Execution - WHERE Evaluation
```
For each row in users:
  row = {id: 1, name: 'Alice', age: 25}
  
  Evaluate: age > 18 AND age < 65
            25 > 18 AND 25 < 65
            True AND True
            = True  ✓ Include this row
  
  row = {id: 2, name: 'Bob', age: 70}
  
  Evaluate: age > 18 AND age < 65
            70 > 18 AND 70 < 65
            True AND False
            = False  ✗ Exclude this row
```

### Step 4: Projection
```
Filtered rows: [{id: 1, name: 'Alice', age: 25}, ...]
Project columns: ['name']

Result: [{name: 'Alice'}, ...]
```

## Token Types Reference

```
┌─────────────────────────────────────────────┐
│ KEYWORDS                                    │
├─────────────────────────────────────────────┤
│ SELECT, FROM, WHERE, INSERT, INTO, VALUES   │
│ CREATE, TABLE, INT, VARCHAR, AND, OR        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ LITERALS & IDENTIFIERS                      │
├─────────────────────────────────────────────┤
│ IDENTIFIER - table/column names             │
│ NUMBER - 42, 3.14                          │
│ STRING - 'hello world'                     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ OPERATORS                                   │
├─────────────────────────────────────────────┤
│ =, >, <, >=, <=, !=                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ DELIMITERS                                  │
├─────────────────────────────────────────────┤
│ ( ) , ; *                                   │
└─────────────────────────────────────────────┘
```

## AST Node Types

```
Statement Nodes:
├── SelectStatement
│   ├── columns: List[str]
│   ├── table: str
│   └── where: Optional[WhereClause]
│
├── InsertStatement
│   ├── table: str
│   ├── columns: List[str]
│   └── values: List[any]
│
└── CreateTableStatement
    ├── table: str
    └── columns: List[Column]

Where Clause Nodes:
├── Condition
│   ├── column: str
│   ├── operator: str
│   └── value: any
│
└── CompoundCondition
    ├── left: WhereClause
    ├── operator: str ('AND'|'OR')
    └── right: WhereClause
```

## Error Handling Flow

```
Try:
    SQL Text → Lexer → Tokens
                        ↓
    Tokens → Parser → AST
                        ↓
    AST → Executor → Result
                        ↓
    Success! Return Result
    
Catch:
    Lexer Error    → "Unexpected character 'X' at position N"
    Parser Error   → "Expected IDENTIFIER, got NUMBER at position N"
    Executor Error → "Table 'X' does not exist"
                  → "Column 'X' does not exist"
                  → "Column 'X' expects INT, got str"
```

## Complete Example Trace

```
User Input: "INSERT INTO users (name, age) VALUES ('Alice', 25)"

┌────────────────────────────────────────────────────────────┐
│ 1. LEXER                                                   │
├────────────────────────────────────────────────────────────┤
│ Scans character by character:                             │
│ "INSERT" → Keyword INSERT                                 │
│ " " → Skip whitespace                                     │
│ "INTO" → Keyword INTO                                     │
│ ... continue ...                                          │
│                                                           │
│ Tokens: [INSERT, INTO, IDENTIFIER(users),                │
│          LPAREN, IDENTIFIER(name), COMMA,                │
│          IDENTIFIER(age), RPAREN, VALUES,                │
│          LPAREN, STRING('Alice'), COMMA,                 │
│          NUMBER(25), RPAREN]                             │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ 2. PARSER                                                  │
├────────────────────────────────────────────────────────────┤
│ Recognize INSERT statement                                │
│ Parse table name: 'users'                                │
│ Parse column list: ['name', 'age']                       │
│ Parse VALUES                                              │
│ Parse value list: ['Alice', 25]                          │
│                                                           │
│ AST: InsertStatement(                                     │
│   table='users',                                         │
│   columns=['name', 'age'],                               │
│   values=['Alice', 25]                                   │
│ )                                                         │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ 3. EXECUTOR                                                │
├────────────────────────────────────────────────────────────┤
│ Get 'users' table from storage                           │
│                                                           │
│ Build row: {name: 'Alice', age: 25}                      │
│                                                           │
│ Validate:                                                 │
│   - 'name' is VARCHAR ✓                                  │
│   - 'age' is INT ✓                                       │
│   - No size violations ✓                                 │
│                                                           │
│ Insert row into table                                     │
│ Save table to disk (users.json)                          │
│                                                           │
│ Return: QueryResult(message="1 row inserted")            │
└────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Recursive Descent Parsing
Each grammar rule becomes a method:
- `parse_select()` handles SELECT statements
- `parse_where()` handles WHERE clauses
- `parse_condition()` handles individual conditions

### 2. Visitor Pattern (Implicit)
The executor "visits" different AST node types and handles each appropriately.

### 3. Data Validation Layer
Storage validates all data before insertion:
- Type checking (INT vs VARCHAR)
- Size constraints (VARCHAR(50))
- Schema conformance

### 4. Separation of Concerns
- Lexer: Only knows about characters and tokens
- Parser: Only knows about tokens and AST
- Storage: Only knows about data persistence
- Executor: Only knows about query execution

This makes the code maintainable and testable!
