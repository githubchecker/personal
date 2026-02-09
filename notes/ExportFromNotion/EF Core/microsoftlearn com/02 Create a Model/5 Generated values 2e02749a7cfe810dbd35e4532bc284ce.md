# 5. Generated values

# Generated Values

EF Core supports various patterns for generating property values, ranging from simple database defaults to complex computed columns and identity fields.

## 1. Default Values

Relational databases use a default value if no value is provided during an `INSERT`.

- **Static Value:** `builder.Property(b => b.Rating).HasDefaultValue(3);`
- **SQL Fragment:** `builder.Property(b => b.Created).HasDefaultValueSql("getutcdate()");`

### Named Constraints (SQL Server)

You can specify a custom name for the default value constraint:

```csharp
builder.Property(b => b.Rating).HasDefaultValue(3, "DF_Blog_Rating");

```

## 2. Computed Columns

Value is calculated by the database based on other columns.

- **Virtual (Computed on Fetch):**
- **Stored (Persisted on Disk):**

## 3. Explicit Value Generation Configuration

You can force specific behaviors for non-key properties using `ValueGenerated*` methods.

| Strategy | Description | Fluent API | Data Annotation |
| --- | --- | --- | --- |
| **On Add** | Generated for new records only. | `.ValueGeneratedOnAdd()` | `[DatabaseGenerated(Identity)]` |
| **On Add or Update** | Generated on every save/update. | `.ValueGeneratedOnAddOrUpdate()` | `[DatabaseGenerated(Computed)]` |
| **Never** | Disables all generation. | `.ValueGeneratedNever()` | `[DatabaseGenerated(None)]` |

## 4. Date and Time Timestamps

### Creation Timestamp

Typically handled by a default SQL value.

```csharp
builder.Property(b => b.CreatedAt).HasDefaultValueSql("getutcdate()");

```

### Update Timestamp

Most databases don't allow volatile functions like `GETDATE()` in computed columns. Instead, use a **database trigger**:

```sql
CREATE TRIGGER [Blogs_UPDATE] ON [Blogs] AFTER UPDATE AS
BEGIN
    UPDATE Blogs SET LastUpdated = GETUTCDATE() FROM Blogs 
    INNER JOIN INSERTED ON Blogs.Id = INSERTED.Id
END

```

## 5. Overriding Value Generation

If a property has value generation configured, EF Core will ignore any values you set in C# unless you provide a **non-default** value (e.g., non-zero for `int`).

<aside>
ℹ️ Inserting explicit values into a SQL Server `IDENTITY` column requires a specific `SET IDENTITY_INSERT` flag in raw SQL or specialized configuration.

</aside>