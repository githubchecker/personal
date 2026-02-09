# 4. Team environments

# Migrations in Team Environments

When working with Migrations in team environments, pay extra attention to the model snapshot file. This file can tell you if your teammate's migration merges cleanly with yours or if you need to resolve a conflict by re-creating yourmigration before sharing it.

## Merging

When you merge migrations from your teammates, you may get conflicts in your model snapshot file. If both changes are unrelated, the merge is trivial and the two migrations can coexist. For example, you may get a merge conflict in the customer entity type configuration that looks like this:

```bash
<<<<<<< Mine
b.Property<bool>("Deactivated");
=======
b.Property<int>("LoyaltyPoints");
>>>>>>> Theirs

```

Since both of these properties need to exist in the final model, complete the merge by adding both properties. In manycases, your version control system may automatically merge such changes for you.

```csharp
b.Property<bool>("Deactivated");
b.Property<int>("LoyaltyPoints");

```

In these cases, your migration and your teammate's migration are independent of each other. Since either of them could be applied first, you don't need to make any additional changes to your migration before sharing it with your team.

## Resolving conflicts

Sometimes you encounter a true conflict when merging the model snapshot model. For example, you and your teammate may each have renamed the same property.

```bash
<<<<<<< Mine
b.Property<string>("Username");
=======
b.Property<string>("Alias");
>>>>>>> Theirs

```

If you encounter this kind of conflict, resolve it by re-creating your migration. Follow these steps:

- Abort the merge and rollback to your working directory before the merge
- Remove your migration (but keep your model changes)
- Merge your teammate's changes into your working directory
- Re-add your migration

After doing this, the two migrations can be applied in the correct order. Their migration is applied first, renamingthe column to Alias, thereafter your migration renames it to Username.

Your migration can safely be shared with the rest of the team.