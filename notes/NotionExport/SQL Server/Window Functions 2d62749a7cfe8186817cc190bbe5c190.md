# Window Functions

Here is the comprehensive **Beginner to Expert** guide to **Window Functions** (`OVER`, `PARTITION BY`).

This feature transformed SQL from a data retrieval language into a data analysis powerhouse.

---

# 📘 Phase 1: The Concept (The "Aha!" Moment)

To understand `OVER()`, you must understand what `GROUP BY` does wrong.

### The Problem with `GROUP BY`

`GROUP BY` collapses rows. If you group 100 sales rows by Month, you get 1 row back. You lose the details of the individual sales.

### The Solution: `OVER()`

`OVER()` allows you to perform "Group By" math (Sum, Count, Avg) **without collapsing the rows**. It adds the aggregate data as an extra column on every row.

**Analogy:**

- **GROUP BY:** Takes 10 receipts, calculates the total, and throws the receipts away. Returns 1 number.
- **OVER():** Takes 10 receipts, calculates the total, and **writes the total at the bottom of every receipt**. Returns 10 receipts.

---

# ⚙️ Phase 2: The Syntax Breakdown

The Clause is composed of three parts:
`Function() OVER ( PARTITION BY ... ORDER BY ... ROWS ... )`

### 1. `OVER()` (The Empty Window)

If you use `OVER()` empty, it treats the **entire result set** as one big window.

```sql
SELECT
    Name,
    Salary,
    -- 🟢 Sum of ALL rows in the table, repeated on every row
    SUM(Salary) OVER() as TotalCompanySalary,

    -- 🟢 Percent of total company salary this person makes
    Salary / SUM(Salary) OVER() * 100 as PctOfTotal
FROM Employees;

```

### 2. `PARTITION BY` (The Reset Button)

This is exactly like `GROUP BY`, but applied inside the window. It means: *"Calculate this aggregate for the specific group this row belongs to."*

```sql
SELECT
    Name,
    Department,
    Salary,
    -- 🟢 Sums only salaries INSIDE this row's Department
    SUM(Salary) OVER(PARTITION BY Department) as DeptTotal
FROM Employees;

```

- *Result:* When the query moves from an 'IT' employee to an 'HR' employee, the `DeptTotal` calculation resets and recalculates for HR.

---

# 📊 Phase 3: Ranking & Ordering

You often need to assign numbers to rows (e.g., "Top 3 Sales"). This requires `ORDER BY` *inside* the `OVER()` clause.

### The Ranking Functions

1. **`ROW_NUMBER()`**: Unique sequential number (1, 2, 3, 4). If there is a tie, it randomly picks who comes first.
2. **`RANK()`**: Ranking with Gaps (1, 1, **3**, 4). If two people tie for 1st, the next person is 3rd.
3. **`DENSE_RANK()`**: Ranking without Gaps (1, 1, **2**, 3). If two people tie for 1st, the next person is 2nd.

**Example: Finding the highest paid person per Dept**

```sql
SELECT
    Name, Department, Salary,
    -- Resets the count for every Department, Ordered by Salary High to Low
    ROW_NUMBER() OVER(PARTITION BY Department ORDER BY Salary DESC) as RankNum
FROM Employees;

```

- *Usage:* To get the top employee, wrap this in a CTE and select `WHERE RankNum = 1`.

---

# 📈 Phase 4: Running Totals (Cumulative Sum)

This is one of the most powerful features. If you add `ORDER BY` to a standard Aggregate (SUM/COUNT), it changes behavior from **"Total of Group"** to **"Running Total"**.

**Scenario:** We want to see how the bank balance changes transaction by transaction.

```sql
SELECT
    TransactionId,
    TransactionDate,
    Amount,
    -- 🟢 Running Total: Sums previous rows + current row based on Date
    SUM(Amount) OVER(ORDER BY TransactionDate) as CumulativeBalance
FROM BankTransactions;

```

**Combined with Partition:**

```sql
-- Running total reset for every Customer
SUM(Amount) OVER(PARTITION BY CustomerId ORDER BY TransactionDate)

```

---

# ⏩ Phase 5: LEAD & LAG (Time Travel)

These allows you to look at a **Different Row** from the **Current Row** without self-joining the table.

- **`LAG(Col, 1)`**: Look at the *Previous* row.
- **`LEAD(Col, 1)`**: Look at the *Next* row.

**Scenario:** Calculate Year-Over-Year (YoY) Growth.

```sql
SELECT
    Year,
    TotalSales,
    -- 1. Grab sales from the previous row
    LAG(TotalSales, 1) OVER(ORDER BY Year) as LastYearSales,

    -- 2. Calculate Difference
    TotalSales - LAG(TotalSales, 1) OVER(ORDER BY Year) as Growth
FROM YearlySales;

```

---

# 🧠 Phase 6: Expert Tuning (Framing)

When you calculate Running Totals using `ORDER BY`, SQL Server applies a **Default Frame**. This matters for performance.

### 1. The Default (`RANGE`)

If you write `SUM(x) OVER(ORDER BY y)`, SQL interprets it as:
`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`

- **Issue:** `RANGE` is slower because it has to handle logical duplicates (ties) mathematically. It often causes a "Window Spool" on disk in execution plans.

### 2. The Fix (`ROWS`)

Explicitly tell SQL to look at **Physical Rows**.
`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`

- **Performance:** Significantly faster than `RANGE`.

**Expert Code Style:**

```sql
-- 🚀 Fast Running Total
SUM(Amount) OVER(
    PARTITION BY CustId
    ORDER BY Date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW -- Explicit Frame
)

```

---

# 📝 Summary Cheat Sheet

| Keyword | Definition | Effect on Aggregation |
| --- | --- | --- |
| **`OVER()`** | The Window | Defines the set of rows to calculate over. |
| **`PARTITION BY`** | The Scope | "Reset" calculation when this column changes. (Like GROUP BY). |
| **`ORDER BY`** | The Sort | Required for Ranking. Turns `SUM` into "Running Total". |
| **`ROW_NUMBER()`** | Function | 1, 2, 3, 4 (Always Unique). |
| **`RANK()`** | Function | 1, 1, 3, 4 (Skips on ties). |
| **`DENSE_RANK()`** | Function | 1, 1, 2, 3 (No skips). |
| **`LAG()`** | Function | Value from previous row. |
| **`ROWS BETWEEN`** | The Frame | Physical restriction (e.g., "Only look at last 3 rows"). |

### 🚀 Performance Tip

To optimize `OVER(PARTITION BY A ORDER BY B)`, ensure you have an **Index** on `(A, B)`.

- SQL will read the index, see the data is already partitioned (Grouped) and sorted, and calculate the window function instantly without a Sort operator.

## Examples

Here is a clear, step-by-step example using a **Sales Scenario**.

We will look at two main concepts:

1. **Aggregates** (Totals) without collapsing rows.
2. **Ranking** (Handling ties and sorting).

---

### 🛠️ Step 1: The Setup (Copy & Paste this)

First, let's create a temporary dataset of Salespeople in two different Regions (North and South). Note that **Alice and Bob represent a "Tie"** in sales.

```sql
DECLARE @SalesTable TABLE (
    SalesPerson VARCHAR(50),
    Region VARCHAR(50),
    SalesAmount INT
);

INSERT INTO @SalesTable VALUES
('Alice',   'North', 500), -- Tie for 1st in North
('Bob',     'North', 500), -- Tie for 1st in North
('Charlie', 'North', 300),
('Dave',    'North', 200),
('Eve',     'South', 900),
('Frank',   'South', 600);

```

---

### 📊 Example 1: `OVER()` and `PARTITION BY`

**Goal:** Show the Individual Sales, The Region's Total, and the Grand Total on *every* row.

```sql
SELECT
    SalesPerson,
    Region,
    SalesAmount,

    -- 1. Grand Total: Empty OVER() means "Look at the whole table"
    SUM(SalesAmount) OVER() as GrandTotal,

    -- 2. Region Total: PARTITION BY means "Reset sum for each Region"
    SUM(SalesAmount) OVER(PARTITION BY Region) as RegionTotal,

    -- 3. Calculate % of Region (Easy math using the window function)
    CAST(SalesAmount * 100.0 / SUM(SalesAmount) OVER(PARTITION BY Region) AS DECIMAL(5,2)) as PctOfRegion
FROM @SalesTable;

```

### 🟢 Output 1 (Aggregates)

Notice how `RegionTotal` changes when we switch from North to South, but the rows are not collapsed.

| SalesPerson | Region | SalesAmount | GrandTotal | RegionTotal | PctOfRegion |
| --- | --- | --- | --- | --- | --- |
| Alice | **North** | 500 | 3000 | **1500** | 33.33 |
| Bob | **North** | 500 | 3000 | **1500** | 33.33 |
| Charlie | **North** | 300 | 3000 | **1500** | 20.00 |
| Dave | **North** | 200 | 3000 | **1500** | 13.33 |
| Eve | **South** | 900 | 3000 | **1500** | 60.00 |
| Frank | **South** | 600 | 3000 | **1500** | 40.00 |

---

### 🏆 Example 2: The Ranking Functions (The Tie Breakers)

**Goal:** Rank employees by Sales from High to Low within their Region. Watch exactly how **Alice and Bob (both 500)** are treated differently.

```sql
SELECT
    Region,
    SalesPerson,
    SalesAmount,

    -- 1. ROW_NUMBER: Unique ID. Tries are broken randomly or by chance.
    ROW_NUMBER() OVER(PARTITION BY Region ORDER BY SalesAmount DESC) as RN,

    -- 2. RANK: Skips numbers. (1, 1, 3). Like Olympic Medals.
    RANK() OVER(PARTITION BY Region ORDER BY SalesAmount DESC) as Rnk,

    -- 3. DENSE_RANK: No Skips. (1, 1, 2).
    DENSE_RANK() OVER(PARTITION BY Region ORDER BY SalesAmount DESC) as DenseRnk,

    -- 4. NTILE: Divide the group into 2 buckets (High performers vs Low)
    NTILE(2) OVER(PARTITION BY Region ORDER BY SalesAmount DESC) as Quartile
FROM @SalesTable;

```

### 🟢 Output 2 (Rankings)

Look at the **North** region logic:

| Region | Name | Sales | **RN** | **Rnk** | **Dense** | **Ntile(2)** | Meaning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **North** | Alice | 500 | **1** | **1** | **1** | 1 | Tied for first. |
| **North** | Bob | 500 | **2** | **1** | **1** | 1 | Tied for first. `ROW_NUMBER` forced a 2. `RANK` gave 1. |
| **North** | Charlie | 300 | **3** | **3** | **2** | 2 | **RANK:** Since 2 people were #1, Charlie is #3.<br>**DENSE:** Alice/Bob are rank 1, so Charlie is next (Rank 2). |
| **North** | Dave | 200 | 4 | 4 | 3 | 2 | Bottom of list. |
| South | Eve | 900 | 1 | 1 | 1 | 1 | Best in South. |
| South | Frank | 600 | 2 | 2 | 2 | 2 | Second in South. |

### 🧠 Cheat Sheet for Understanding

1. **`OVER()`**: Defines the "Window". If empty, it looks at everything.
2. **`PARTITION BY [Col]`**: The "Reset Button". Restarts the counter/sum whenever `[Col]` changes (e.g., reset rank for South region).
3. **`ROW_NUMBER()`**: **"The Turnstyle"**. 1, 2, 3, 4. No duplicates. If there is a tie, SQL randomly picks who is 1 and who is 2.
4. **`RANK()`**: **"The Olympic Medal"**. 1, 1, **3**. (Gold, Gold, Bronze). There is no "Silver" (Rank 2) because two people got Gold.
5. **`DENSE_RANK()`**: **"The Optimist"**. 1, 1, **2**. Everyone gets a number. Ties don't cause gaps in the sequence.
6. **`NTILE(X)`**: **"The Buckets"**. Splits the data into X groups. `NTILE(2)` splits the top half (1) and bottom half (2).