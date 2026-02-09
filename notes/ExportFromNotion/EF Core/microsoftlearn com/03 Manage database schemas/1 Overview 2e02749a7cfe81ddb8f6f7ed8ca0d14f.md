# 1. Overview

# Managing Database Schemas

EF Core provides two primary strategies for keeping your .NET model and the database schema in sync. The choice depends on which one is considered the "Source of Truth."

## 1. Migrations (Code-First)

Use **Migrations** if your **EF Core model** is the source of truth.

- As you modify your C# entities, EF Core generates incremental code files (migrations) that describe the changes needed to the database.
- Keeps the database schema evolving alongside your application code.
- Recommended for most new projects.

## 2. Reverse Engineering (Database-First)

Use **Reverse Engineering (Scaffolding)** if your **database schema** is the source of truth.

- You create/modify the database schema manually or using other tools.
- You then run a command to generate (scaffold) `DbContext` and entity classes that match the existing schema.
- Common for legacy databases or when DBA teams manage the schema.

## 3. Create and Drop APIs

For prototyping, local testing, or in-memory databases, you can use the `EnsureCreated` and `EnsureDeleted` APIs.

- `EnsureCreated`: Creates the database and schema based on the model if they don't exist.
- `EnsureDeleted`: Drops the database if it exists.
- **Warning:** These APIs bypass Migrations; they are not suitable for production scenarios where schema evolution is required.