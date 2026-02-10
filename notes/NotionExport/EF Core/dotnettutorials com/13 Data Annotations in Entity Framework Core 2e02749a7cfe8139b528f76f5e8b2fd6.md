# 13. Data Annotations in Entity Framework Core

# Data Annotations in Entity Framework Core

Data Annotations are attributes applied to domain classes and properties to override default conventions. They provide a declarative way to configure database mappings and enforce validation rules directly in your model.

### 1. Attribute Summary

Attributes are primary located in two namespaces:
* `System.ComponentModel.DataAnnotations` (Validation & Metadata)
* `System.ComponentModel.DataAnnotations.Schema` (Database Mapping)

| Attribute | Category | Purpose |
| --- | --- | --- |
| `[Key]` | Metadata | Marks property as Primary Key. |
| `[Required]` | Validation | Forces `NOT NULL` in DB and validates in UI. |
| `[Table]` | Schema | Configures table name and schema. |
| `[Column]` | Schema | Configures column name, type, and order. |
| `[ForeignKey]` | Schema | Explicitly links a navigation property to an FK. |
| `[NotMapped]` | Schema | Excludes property from database storage. |
| `[Timestamp]` | Metadata | Enables Optimistic Concurrency via `rowversion`. |
| `[MaxLength]` | Schema/Val | Sets database length and validates input. |

---

### 2. Schema Mapping Attributes

These attributes reside in `.Schema` and dictate how classes map to database structures.

- **`[Table("Name", Schema="admin")]`**: Customizes the table name and SQL schema.
- **`[Column("Name", TypeName="varchar(50)")]`**: Maps to a specific database column and data type.
- **`[DatabaseGenerated]`**: Specifies how values are created (e.g., `Identity`, `Computed`, or `None`).
- **`[ForeignKey("PropName")]`**: Applied to a navigation property or FK property to clarify relationships.
- **`[InverseProperty]`**: Resolves ambiguity when multiple relationships exist between the same two entities.
- **`[NotMapped]`**: Used for properties required by business logic but not stored in the database.

---

### 3. Validation and Metadata Attributes

These attributes reside in the base namespace and are used for enforcing data integrity.

- **`[Key]`**: Necessary if your PK property doesn’t follow the `Id` or `<Entity>Id` convention.
- **`[Required]`**: Maps to `NOT NULL`. In C# 8.0+, non-nullable reference types (e.g., `string Name`) achieve this automatically in EF Core.
- **`[MaxLength(n)]`**: Sets the database column size (e.g., `NVARCHAR(n)`).
- **`[ConcurrencyCheck]`**: Includes the property in the `WHERE` clause of `UPDATE`/`DELETE` queries to detect conflicts.
- **`[Timestamp]`**: A specialized version of concurrency check that uses the SQL Server `rowversion` type.

---

### 4. Application-Only Validation

Some attributes perform validation during model binding (e.g., in ASP.NET Core) but **do not** affect the database schema:
* `[EmailAddress]`, `[Phone]`, `[Url]`
* `[Range(min, max)]`
* `[MinLength(n)]`
* `[RegularExpression(pattern)]`

---

### 5. Data Annotations vs. Fluent API

| Feature | Data Annotations | Fluent API |
| --- | --- | --- |
| **Simplicity** | High (Inline with code) | Moderate (Separate file) |
| **Separation of Concerns** | Low (Pollutes Domain) | High (Mappings separate) |
| **Capabilities** | Limited | Full (Everything supported) |
| **Precedence** | Lower | Higher (Overrides Annotations) |

**Recommendation**: Use Data Annotations for simple validation and basic mappings. Use **Fluent API** for complex relationships, composite keys, indexing strategies, and global query filters.