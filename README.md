# Simple SQL Engine - Learning Project

A basic SQL database engine built from scratch in Python for educational purposes. This project demonstrates how a SQL database works under the hood.

## Features

- **CREATE TABLE**: Define tables with INT and VARCHAR columns
- **INSERT**: Add data to tables
- **SELECT**: Query data with column selection
- **WHERE**: Filter results with conditions (=, >, <, >=, <=, !=)
- **Compound Conditions**: Use AND/OR in WHERE clauses
- **Data Persistence**: Tables stored as JSON files

## Architecture

- TODO: Add architecture diagram and explanation
- TODO:

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

## 🤝 Contributing

This is a learning project! Feel free to:

- Add new features
- Improve error messages
- Add more comprehensive validation
- Optimize performance
- Add tests

## 📄 License

This project is for educational purposes. Use it freely to learn!
