# Domain Constarints

To make fields **mandatory** and enforce **Domain Constraints** (valid sets of values) in SQL Server, you rely on three primary tools.

Here is the hierarchy from basic requirements to complex logic.

---

# 🛑 Phase 1: The Foundation (`NOT NULL`)

This is the most basic definition of "Mandatory." It ensures that a field cannot contain the `NULL` marker.

### 1. Creating a New Table

```sql
CREATE TABLE Employees (
    ID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL -- ⛔ Required Field
);

```

### 2. Modifying Existing Table

If you have an existing column that allows NULLs and want to make it mandatory, you must use `ALTER COLUMN`.

> ⚠️ Critical Prerequisite: You must fix (UPDATE) any existing NULL values in that column before running this, or SQL will throw an error.
> 

```sql
-- Step 1: Fix existing bad data
UPDATE Employees SET Email = 'N/A' WHERE Email IS NULL;

-- Step 2: Tighten the rule
ALTER TABLE Employees
ALTER COLUMN Email VARCHAR(100) NOT NULL;

```

---

# 🛡️ Phase 2: Domain Constraints (`CHECK`)

A common mistake is thinking `NOT NULL` is enough.

- **The Trap:** To SQL Server, an Empty String `''` is **NOT** Null. It is a valid value.
- **The Solution:** Use a `CHECK` constraint to ensure the field actually has data.

### 1. Enforcing "Not Empty" (Mandatory Text)

If you want to ensure the User provides at least 1 character:

```sql
ALTER TABLE Employees
ADD CONSTRAINT CK_Employees_Name_NotEmpty
CHECK (LEN(Name) > 0);
-- Validates: Name is NOT NULL *AND* Length > 0

```

### 2. Enforcing "Valid Range" (Domain Rules)

Domain constraints restrict the value to a specific logical set.

```sql
ALTER TABLE Employees
ADD CONSTRAINT CK_Employees_Age
CHECK (Age >= 18 AND Age <= 65);

```

### 3. Enforcing "Specific List" (Enum-like behavior)

Restrict a string column to specific words.

```sql
ALTER TABLE Employees
ADD CONSTRAINT CK_Employees_Status
CHECK (Status IN ('Active', 'Inactive', 'Suspended'));

```

### 4. Enforcing "Pattern" (Regex-lite)

Ensure data follows a format (e.g., Phone Number must be numbers).

```sql
ALTER TABLE Employees
ADD CONSTRAINT CK_Phone_NumbersOnly
CHECK (PhoneNumber NOT LIKE '%[^0-9]%');
-- Reads as: Fail if column contains anything that is NOT 0-9

```

---

# ⚙️ Phase 3: The "Soft" Mandatory (`DEFAULT`)

Sometimes "Mandatory" means: *"The user doesn't have to provide it, but the Database **MUST** have a value."*

Use `DEFAULT` constraints for this. This prevents the field from being NULL if the application logic (C#) forgets to send it.

```sql
ALTER TABLE Employees
ADD CONSTRAINT DF_CreatedDate
DEFAULT GETDATE() FOR CreatedDate;
-- If C# doesn't send CreatedDate, SQL injects the current time.

```

---

# 🧩 Phase 4: Combined Example (Best Practice)

Here is how a professional table definition looks using all these concepts to enforce strict data quality.

```sql
CREATE TABLE UserProfile (
    -- 1. Identity & PK
    UserID INT IDENTITY(1,1) PRIMARY KEY,

    -- 2. Strictly Mandatory (Must send value)
    UserName VARCHAR(50) NOT NULL,

    -- 3. Business Logic (Cannot be blank space)
    DisplayName VARCHAR(50) NOT NULL,
    CONSTRAINT CK_Display_NoBlank CHECK (LEN(DisplayName) > 0),

    -- 4. Specific Domain (Male, Female, Other)
    Gender CHAR(1) NOT NULL,
    CONSTRAINT CK_Gender_Valid CHECK (Gender IN ('M', 'F', 'O')),

    -- 5. Auto-filled (Mandatory in DB, Optional in App)
    IsActive BIT NOT NULL
    CONSTRAINT DF_Active DEFAULT 1
);

```

---

# 🕵️ Expert Tip: `WITH CHECK` vs `WITH NOCHECK`

When adding a constraint to a table that **already has millions of rows**, checking every existing row takes time.

- **`WITH CHECK` (Default):** SQL verifies existing data matches the rule. If it fails, the constraint isn't created.
- **`WITH NOCHECK`:** SQL ignores existing bad data and applies the rule **only to new inserts/updates**.

```sql
-- Allow existing bad phone numbers, but enforce it for new ones
ALTER TABLE Employees
WITH NOCHECK
ADD CONSTRAINT CK_Phone_Valid CHECK (LEN(Phone) = 10);

```

*Note: The constraint will be marked as "Not Trusted" in `sys.check_constraints`, which can affect optimizer performance.*