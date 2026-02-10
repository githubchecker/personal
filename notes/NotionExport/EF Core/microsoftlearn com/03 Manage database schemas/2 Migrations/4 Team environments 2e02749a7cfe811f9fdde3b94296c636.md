# 4. Team environments

# Migrations in Team Environments

Working on migrations in a team requires careful management of the **Model Snapshot** file to avoid inconsistencies and merge conflicts.

## 1. Merging Independent Changes

If you and a teammate add unrelated changes (e.g., two different properties on the same entity), a merge conflict may occur in the `ModelSnapshot.cs` file.

**Resolution:**Simply accept both changes. Most version control systems (like Git) handle this automatically, but if a manual conflict occurs, ensure both properties are included in the final snapshot code.

```csharp
// Example merged snapshot code:
b.Property<bool>("IsActive");
b.Property<int>("RewardPoints");

```

## 2. Resolving Structural Conflicts

A **True Conflict** happens when both developers modify the same architectural element (e.g., renaming the same property to different names).

**Best Practice Workflow:**If a merge conflict is too complex to resolve manually in the snapshot:

- **Remove your local migration** (but keep your model changes): `dotnet ef migrations remove`.
- **Pull/Merge** your teammate's code and migrations into your branch.
- **Re-add your migration**: `dotnet ef migrations add <Name>`.

This ensures EF Core calculates your migration's delta based on the teammate's already-updated model snapshot, resulting in a clean and serializable migration history.

## 3. Key Rules for Teams

- **Check-in Snapshots:** Always commit both the migration files (`.cs`, `.Designer.cs`) and the `ModelSnapshot.cs`.
- **Don't Edit applied Migrations:** Once a migration has been pushed to a shared branch, do not edit its `Up` or `Down` methods.
- **Communication:** If two people are working on the same entity's structure, communicate to avoid conflicting schema changes.