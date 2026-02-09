# 1. Overview

# Managing Database Schemas

EF Core provides two primary ways of keeping your EF Core model and database schema in sync. To choose between the two,decide whether your EF Core model or the database schema is the source of truth.

If you want your EF Core model to be the source of truth, use [Migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/). As you make changes to your EF Coremodel, this approach incrementally applies the corresponding schema changes to your database so that it remainscompatible with your EF Core model.

Use [Reverse Engineering](https://learn.microsoft.com/en-us/ef/core/managing-schemas/scaffolding/) if you want your database schema to be the source of truth. This approach allows you toscaffold a DbContext and the entity type classes by reverse engineering your database schema into an EF Core model.

<aside>
ℹ️ **NOTE:** The [create and drop APIs](https://learn.microsoft.com/en-us/ef/core/managing-schemas/ensure-created) can also create the database schema from your EF Core model. However, they are primarilyfor testing, prototyping, and other scenarios where dropping the database is acceptable.

</aside>