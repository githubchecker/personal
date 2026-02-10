# 3. Entity Properties

# Entity Properties

Entity properties represent the data stored in the database. When using a relational provider, each property maps to a table column.

## 1. Property Inclusion and Exclusion

By default, all public properties with a getter and setter are included in the model.

- **Exclude Properties:**
- **Fluent API:** `modelBuilder.Entity<Blog>().Ignore(b => b.LoadedTimestamp);`

## 2. Column Names and Data Types

### Column Naming

- **Fluent API:** `builder.Property(b => b.BlogId).HasColumnName("blog_id");`
- **Data Annotations:** `[Column("blog_id")]`

### Data Types

Explicitly define the database provider type (e.g., `varchar`, `decimal`).

- **Fluent API:** `builder.Property(b => b.Rating).HasColumnType("decimal(5, 2)");`
- **Data Annotations:** `[Column(TypeName = "decimal(5, 2)")]`

## 3. Length, Precision, and Scale

### Maximum Length (Strings and Bytes)

- **Fluent API:** `.HasMaxLength(500)`
- **Data Annotations:** `[MaxLength(500)]`

### Precision and Scale (Decimals and Dates)

`Precision` is the total number of digits; `Scale` is the digits after the decimal point.

- **Fluent API:** `.HasPrecision(14, 2)`
- **Data Annotations:** `[Precision(14, 2)]`

## 4. Required vs. Optional Properties

| Status | .NET Type | Database Column |
| --- | --- | --- |
| **Optional** | `string?`, `int?` | `NULL` |
| **Required** | `string` (with NRT), `int` | `NOT NULL` |

### Explicit Configuration:

To force an optional property to be required:

- **Fluent API:** `builder.Property(b => b.Url).IsRequired();`
- **Data Annotations:** `[Required]`

## 5. Advanced Column Configuration

### Unicode Support

Configure text columns to be Unicode (UTF-16/`nvarchar`) or non-Unicode (ASCII/`varchar`).

- **Fluent API:** `.IsUnicode(false)`
- **Data Annotations:** `[Unicode(false)]`

### Collations

Define how text is compared and sorted (e.g., case-insensitive).

```csharp
builder.Property(c => c.Name).UseCollation("SQL_Latin1_General_CP1_CI_AS");

```

### Column Order

Specifies the position of the column in the generated table.

- **Fluent API:** `.HasColumnOrder(0)`
- **Data Annotations:** `[Column(Order = 0)]`

### Column Comments

Add documentation directly to the database schema.

- **Fluent API:** `.HasComment("Primary key for the blog table")`
- **Data Annotations:** `[Comment("Primary key for the blog table")]`