# RAISERROR vs THROW

## The following table lists differences between the [RAISERROR](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/raiserror-transact-sql?view=sql-server-ver17) and `THROW` statements.

| RAISERROR statement | THROW statement |
| --- | --- |
| If a *msg_id* is passed to `RAISERROR`, the ID must be defined in `sys.messages`. | The *error_number* parameter doesn't have to be defined in `sys.messages`. |
| The *msg_str* parameter can contain `printf` formatting styles. | The *message* parameter doesn't accept `printf` style formatting. |
| The *severity* parameter specifies the severity of the exception. | There's no *severity* parameter. When `THROW` is used to initiate the exception, the severity is always set to `16`. However, when `THROW` is used to rethrow an existing exception, the severity is set to that exception's severity level. |
| Doesn't honor [SET XACT_ABORT](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql?view=sql-server-ver17). | Transactions are *rolled back* if [SET XACT_ABORT](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-xact-abort-transact-sql?view=sql-server-ver17) is `ON`. |

**Examples**

**A. Use THROW to raise an exception**

The following example shows how to use the `THROW` statement to raise an exception.

SQL

```sql
THROW 51000, 'The record does not exist.', 1;
```

Here's the result set.

Output

```sql
Msg 51000, Level 16, State 1, Line 1
The record does not exist.
```

**B. Use THROW to raise an exception again**

The following example shows how to use the `THROW` statement to raise the last thrown exception again.

SQL

```sql
USE tempdb;
GO
CREATE TABLE dbo.TestRethrow
(    ID INT PRIMARY KEY
);
BEGIN TR
    INSERT dbo.TestRethrow(ID) VALUES(1);

--  Force error 2627, Violation of PRIMARY KEY constraint to be raised.
    INSERT dbo.TestRethrow(ID) VALUES(1);
END TRY
BEGIN CATCH

    PRINT 'In catch block.';
    THROW;
END CATCH;
```

Here's the result set.

Output

```sql
In catch block.
Msg 2627, Level 14, State 1, Line 1
Violation of PRIMARY KEY constraint 'PK__TestReth__3214EC272E3BD7D3'. Cannot insert duplicate key in object 'dbo.TestRethrow'.
The statement has been terminated.
```