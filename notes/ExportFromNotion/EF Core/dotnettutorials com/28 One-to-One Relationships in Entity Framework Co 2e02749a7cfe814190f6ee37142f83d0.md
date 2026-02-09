# 28. One-to-One Relationships in Entity Framework Core

# One-to-One Relationships in Entity Framework Core

A **One-to-One (1:1)** relationship exists when a single record in one table is associated with exactly one record in another table. In EF Core, this is typically represented by a principal entity and a dependent entity linked via a unique foreign key.

---

### Principal vs. Dependent Entities

In a 1:1 relationship, EF Core must know which side holds the foreign key:
* **Principal Entity (Parent)**: The entity that contains the primary key. It can exist independently (e.g., `User`).
* **Dependent Entity (Child)**: The entity that contains the foreign key referencing the principal. It depends on the principal (e.g., `Passport`).

---

### 1. Configuration by Convention

EF Core can discover a 1:1 relationship if both entities have reference navigation properties pointing to each other and follow standard naming for the foreign key.

```csharp
public class User
{
    public int Id { get; set; }
    public string Username { get; set; }

    // Reference Navigation Property
    public Passport Passport { get; set; }
}

public class Passport
{
    public int Id { get; set; }
    public string PassportNumber { get; set; }

    // Foreign Key (Detected by convention: <PrincipalClassName>Id)
    public int UserId { get; set; }
    public User User { get; set; }
}
```

**Note**: EF Core automatically creates a **Unique Index** on the `UserId` column in the `Passport` table to enforce that no two passports can point to the same user.

---

### 2. Configuration with Data Annotations

You can use the `[ForeignKey]` attribute to explicitly define the foreign key property.

```csharp
public class Passport
{
    public int Id { get; set; }
    public string PassportNumber { get; set; }

    public int UserId { get; set; }

    [ForeignKey("UserId")]
    public User User { get; set; }
}
```

---

### 3. Configuration with Fluent API (Recommended)

The Fluent API is the most robust way to configure 1:1 relationships. You must specify which entity is the dependent by passing the generic type to `HasForeignKey`.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<User>()
        .HasOne(u => u.Passport)      // Principal has one Passport
        .WithOne(p => p.User)         // Dependent has one User
        .HasForeignKey<Passport>(p => p.UserId); // FK is in the Passport entity
}
```

---

### Shared Primary Key Pattern

A “Strict” One-to-One relationship can be implemented using a shared primary key. Here, the Primary Key of the dependent table is also its Foreign Key. This ensures that a row in the child table can only ever correspond to exactly one row in the parent table.

```csharp
public class Passport
{
    // Both Primary Key and Foreign Key
    public int UserId { get; set; }
    public string PassportNumber { get; set; }
    public User User { get; set; }
}

// In DbContext OnModelCreating:
modelBuilder.Entity<Passport>()
    .HasKey(p => p.UserId); // Define UserId as PK

modelBuilder.Entity<User>()
    .HasOne(u => u.Passport)
    .WithOne(p => p.User)
    .HasForeignKey<Passport>(p => p.UserId);
```

---

### Required vs. Optional Relationships

The nullability of the Foreign Key property determines if the relationship is mandatory:

- **Required Relationship**: The Foreign Key is **non-nullable** (`int UserId`). A `Passport` cannot exist without a `User`. EF Core uses `Cascade` delete by default.
- **Optional Relationship**: The Foreign Key is **nullable** (`int? UserId`). A `Passport` can exist without a `User`. EF Core uses `ClientSetNull` or `SetNull` by default.

---

### Key Takeaways

| Feature | Implementation / Behavior |
| --- | --- |
| **Principal Entity** | The “Parent” (referenced by the FK). |
| **Dependent Entity** | The “Child” (contains the FK). |
| **Unique Constraint** | Required on the FK column to maintain the 1:1 nature. |
| **Fluent API Mapping** | `modelBuilder.Entity<Principal>().HasOne(p => p.Child).WithOne(c => c.Parent).HasForeignKey<Child>(c => c.FkId);` |
| **Shared Primary Key** | The most storage-efficient way to implement a strict 1:1 relationship. |