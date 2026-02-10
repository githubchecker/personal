# Skip Trigger

This is a classic requirement when doing **Bulk Loads**, **Data Migration**, or **Emergency Fixes** where you don't want audit logs or cascading updates to fire.

Here are the **4 Ways** to achieve this, ranked from "Brute Force" to "Architecturally Elegant."

---

# 🛑 Method 1: Brute Force (DISABLE TRIGGER)

You physically turn off the trigger for the entire table.

- **Behavior:** The trigger is dead. No one can trigger it.
- **⚠️ The Risk:** This disables the trigger for **EVERYONE**, not just you. If a user inserts data while you are running your script, their business logic will **fail to run**. This is dangerous on a live production system.

**Syntax:**

```sql
BEGIN TRANSACTION;

-- 1. Turn it OFF
DISABLE TRIGGER trg_User_Audit ON Users;

-- 2. Do your Work
INSERT INTO Users (Name) VALUES ('Silent Bob');

-- 3. Turn it ON
ENABLE TRIGGER trg_User_Audit ON Users;

COMMIT TRANSACTION;

```

---

# 🛡️ Method 2: The "Session Context" Hook (Safe & Professional)

This is the **Best Practice** for enterprise systems. You modify the Trigger code *once* to check for a "Secret Passcode" (Context info). If the passcode is present, the trigger voluntarily exits.

**How it works:**

1. **Modify Trigger:** Add a check at the top.
2. **Usage:** In your script, set a session variable before inserting.
3. **Safety:** This **only** affects YOUR connection. Other users remain protected by the trigger.

### Step 1: Modify the Trigger (One time setup)

```sql
ALTER TRIGGER trg_User_Audit
ON Users
AFTER INSERT
AS
BEGIN
    -- 🛑 Hook: Check if "SilentMode" is active for this session
    DECLARE @SilentMode BIT;
    SET @SilentMode = CAST(SESSION_CONTEXT(N'DisableAudit') AS BIT);

    IF @SilentMode = 1
    BEGIN
        RETURN; -- 🚪 Exit immediately, do nothing
    END

    -- Normal Logic below...
    INSERT INTO AuditLog...
END

```

### Step 2: Running your Insert

```sql
-- 1. Set the flag (Only exists for this connection)
EXEC sp_set_session_context 'DisableAudit', 1;

-- 2. Trigger sees flag and exits immediately
INSERT INTO Users (Name) VALUES ('Ninja Insert');

-- 3. Reset (Optional, as closing connection resets it anyway)
EXEC sp_set_session_context 'DisableAudit', 0;

```

---

# 📦 Method 3: Bulk Operations (`BULK INSERT`)

By default, **Bulk Operations** in SQL Server (like `bcp` or `BULK INSERT`) do **NOT** fire triggers for performance reasons.

- **Behavior:** If you use the standard bulk insert command, triggers are bypassed automatically.
- **To Enable them:** You actually have to force them on using `FIRE_TRIGGERS`.

**SQL Script:**

```sql
BULK INSERT Users
FROM 'C:\\Data\\NewUsers.txt'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\\n'
    -- Note: I did NOT specify 'FIRE_TRIGGERS', so Triggers are OFF.
);

```

**C# (SqlBulkCopy):**
If using [ADO.NET](http://ado.net/) `SqlBulkCopy`, standard triggers are ignored unless you set the option.

```csharp
using (SqlBulkCopy bulk = new SqlBulkCopy(connString))
{
    // 🛑 Standard: Triggers won't fire.
    // To FORCE them to fire, you would use:
    // new SqlBulkCopy(connString, SqlBulkCopyOptions.FireTriggers);

    bulk.DestinationTableName = "Users";
    bulk.WriteToServer(myDataTable);
}

```

---

# 🤖 Method 4: `NOT FOR REPLICATION`

You can mark a trigger with `NOT FOR REPLICATION`. This tells SQL Server: *"If the Insert comes from a Replication Agent (synchronizing data), don't fire."*

You can exploit this by temporarily pretending to be a replication agent, but this is extremely risky (hacking internal roles) and **not recommended** for standard development.

---

# 🏆 Summary Recommendation

| Scenario | Recommended Method | Why? |
| --- | --- | --- |
| **Emergency Fix (Middle of night)** | **Disable Trigger** | Quickest, but block other users access first. |
| **Regular Maintenance Script** | **Session Context** | Safe, Thread-safe (doesn't affect others). |
| **Importing 1 Million Rows** | **Bulk Insert** | Native performance feature; triggers are off by default. |