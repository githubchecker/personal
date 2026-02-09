# 9. Glossary

# Relationship Glossary

This glossary defines key terms used in Entity Framework Core relationship documentation.

| Term | Definition |
| --- | --- |
| **Dependent Entity** | The "child" entity that contains the Foreign Key (FK). |
| **Principal Entity** | The "parent" entity that contains the Primary or Alternate Key being referenced. |
| **Principal Key** | The property (Primary or Alternate Key) that uniquely identifies the principal entity. |
| **Foreign Key (FK)** | The property in the dependent entity that stores the value matching the principal key. |
| **Navigation** | A property on an entity that references related entities (Reference or Collection). |
| **Reference Navigation** | A navigation holding a single entity reference (the "one" side). |
| **Collection Navigation** | A navigation holding multiple entity references (the "many" side). |
| **Inverse Navigation** | The navigation property at the opposite end of a relationship. |
| **Bidirectional** | A relationship with navigations defined on both entities. |
| **Unidirectional** | A relationship with a navigation defined on only one entity. |
| **Required Relationship** | A relationship where the dependent *must* be linked to a principal (Non-nullable FK). |
| **Optional Relationship** | A relationship where the dependent can exist independently (Nullable FK). |
| **Self-Referencing** | A relationship where the principal and dependent are the same entity type (e.g., Manager/Employee). |
| **Skip Navigation** | A navigation in a many-to-many relationship that "skips" the join entity to reach the other end. |