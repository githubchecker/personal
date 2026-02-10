# 47. Table Per Type Inheritance in Entity Framework Core

# Table Per Type (TPT) Inheritance

**Table Per Type (TPT)** is an inheritance mapping strategy where **each class in the hierarchy maps to its own separate database table**. It represents a normalized approach to storing object hierarchies.

---

### How TPT Works

In TPT, data for a single object is split across two or more tables:
* **Base Table:** Stores columns for properties shared by all types (the base class properties).
* **Derived Tables:** Store columns for properties unique to that specific type.
* **Linkage:** The Primary Key of each derived table is also a Foreign Key that points to the Primary Key of the base table.

---

### Implementation Example: CMS Content

### 1. Define the Entities

Unlike TPH, derived types do not need to be nullable unless the business logic specifically requires it, because they have their own dedicated storage.

```csharp
public abstract class Content
{
    public int Id { get; set; }
    public string Title { get; set; }
    public string Author { get; set; }
}

public class Article : Content
{
    public string Body { get; set; } // Can be NOT NULL in DB
}

public class Video : Content
{
    public string Url { get; set; }
    public int Duration { get; set; }
}
```

### 2. Configure TPT Mapping

To enable TPT, you must explicitly assign a table name to each class in the hierarchy using the `ToTable()` method in the Fluent API.

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Content>().ToTable("Contents");
    modelBuilder.Entity<Article>().ToTable("Articles");
    modelBuilder.Entity<Video>().ToTable("Videos");
}
```

---

### Database Schema Result

This configuration creates a normalized structure with one-to-one relationships between the base and derived tables.

**Contents (Base)**
| Id (PK) | Title | Author |
| :— | :— | :— |
| 1 | EF Core TPT Guide | Pranaya |
| 2 | Intro Video | Rakesh |

**Articles (Derived)**
| Id (PK, FK) | Body |
| :— | :— |
| 1 | “Full article text here…” |

**Videos (Derived)**
| Id (PK, FK) | Url | Duration |
| :— | :— | :— |
| 2 | “http://video.link” | 120 |

---

### Query Behavior: The Join Penalty

When you query for a derived type, EF Core must automatically perform a `JOIN` to reconstruct the full object.

```csharp
// Behind the scenes: SELECT ... FROM Articles JOIN Contents ON Articles.Id = Contents.Id
var articles = await context.Articles.ToListAsync();
```

If you perform a polymorphic query (e.g., `context.Contents.ToList()`), EF Core will perform a `LEFT JOIN` across **every** derived table in the hierarchy to find the data.

---

### Pros and Cons of TPT

| Advantages | Disadvantages |
| --- | --- |
| **Normalized Schema:** Follows standard database normalization rules. | **Performance Overheads:** Every query involves one or more JOINs, which can be slow on large datasets. |
| **Strict Constraints:** You can enforce `NOT NULL` on specialized properties at the database level. | **Write Complexity:** Inserting or deleting a record requires multiple `INSERT` or `DELETE` statements. |
| **Clean Schema:** No “sparse” tables with hundreds of nullable columns. | **Scalability:** As hierarchies get deeper, the JOINs become increasingly complex and difficult to optimize. |

### Summary Recommendation

Use TPT when your database requires a **strictly normalized schema** or when you must guarantee data integrity with DB-level constraints on specialized fields. Avoid TPT if you expect to perform frequent large-scale polymorphic queries, as the performance penalty for the joins can become a bottleneck.