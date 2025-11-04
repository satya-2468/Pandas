#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pandas essentials: A single-file tutorial with explanations and best practices.

What this file demonstrates:
  - Creating DataFrames from messy sample data (dicts, lists, CSV-like strings)
  - Inspecting data: .head(), .info(), .describe()
  - Handling null values: detecting, filling, dropping
  - Working with data types: converting columns to numeric, datetime
  - Indexing & selection: loc, iloc, boolean masks, query
  - Common transformations: rename, sort, groupby, apply, map, lambda
  - Filtering and cleaning text data
  - Date handling: parsing multiple date formats, extracting year/month/day
  - Joining & merging DataFrames
  - Aggregations and pivot tables
  - Exporting cleaned data
"""
# ---- Testing new branch

import pandas as pd
import numpy as np

# ----------------------------- 1. Create Messy Sample Data -----------------------------


raw_data = {
    "id": [1, 2, 3, 4, 5, 6],
    "name": [" alice ", "BOB", None, "Charlie", "david", "Eve "],
    "age": ["25", "thirty", "40", None, "35", "29"],  # mixed numeric/text/null
    "salary": [50000, 60000, None, 70000, "80000", "not available"],  # messy salaries
    "join_date": ["2021-01-10", "10/02/2021", "March 3, 2021", None, "2021/05/20", "20210615"],
    "dept": ["HR", "IT", "Finance", "Finance", "IT", "HR"],
}

df = pd.DataFrame(raw_data)

print("\n--- Raw DataFrame ---")
print(df)

# ----------------------------- 2. Inspect Data -----------------------------
print("\n--- Basic Inspection ---")
print(df.head())         # first 5 rows
print(df.info())         # column types, null counts
print(df.describe(include="all"))  # stats summary, include non-numeric

# ----------------------------- 3. Cleaning Names -----------------------------
# Strip spaces, title-case names, and fill missing with 'Unknown'
df["name"] = df["name"].str.strip().str.title().fillna("Unknown")
print("\n--- Cleaned Names ---")
print(df["name"])

# ----------------------------- 4. Converting Age -----------------------------
# Convert age to numeric, invalid parsing -> NaN
df["age"] = pd.to_numeric(df["age"], errors="coerce")
print("\n--- Cleaned Age (numeric) ---")
print(df["age"])

# ----------------------------- 5. Cleaning Salary -----------------------------
# Convert salary to numeric, replacing invalid with NaN
df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
print("\n--- Cleaned Salary (numeric) ---")
print(df["salary"])

# Fill missing salaries with mean salary
df["salary"] = df["salary"].fillna(df["salary"].mean())

# ----------------------------- 6. Handling Dates -----------------------------
# Convert messy date strings to datetime
df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce", dayfirst=False)
print("\n--- Parsed Join Dates ---")
print(df["join_date"])

# Extract year, month, weekday
df["join_year"] = df["join_date"].dt.year
df["join_month"] = df["join_date"].dt.month
df["join_weekday"] = df["join_date"].dt.day_name()

# ----------------------------- 7. Handling Nulls -----------------------------
print("\n--- Null Value Counts ---")
print(df.isnull().sum())

# Fill missing ages with median
df["age"] = df["age"].fillna(df["age"].median())

# ----------------------------- 8. Indexing & Selection -----------------------------
print("\n--- Selection Examples ---")
print(df.loc[0, "name"])        # single cell
print(df.loc[df["dept"] == "IT"])  # filter by dept
print(df.iloc[0:2, 0:3])        # row/col by position

# Boolean mask: employees with salary > 60000
print(df[df["salary"] > 60000])

# Query syntax (alternative filtering)
print(df.query("dept == 'Finance' and age > 30"))

# ----------------------------- 9. Sorting & Renaming -----------------------------
df = df.rename(columns={"dept": "department"})
df = df.sort_values(by="salary", ascending=False)
print("\n--- Sorted by Salary ---")
print(df[["name", "salary", "department"]])

# ----------------------------- 10. GroupBy & Aggregation -----------------------------
print("\n--- Average Salary by Department ---")
print(df.groupby("department")["salary"].mean())

# Multiple aggregations
print("\n--- Salary Aggregations by Department ---")
print(df.groupby("department")["salary"].agg(["mean", "min", "max", "count"]))

# ----------------------------- 11. Apply & Lambda -----------------------------
# Add a column with salary category using apply + lambda
df["salary_category"] = df["salary"].apply(lambda x: "High" if x > 65000 else "Low/Medium")
print("\n--- Salary Categories ---")
print(df[["name", "salary", "salary_category"]])

# ----------------------------- 12. Joining / Merging -----------------------------
# Create a second DataFrame with dept info
dept_info = pd.DataFrame({
    "department": ["HR", "IT", "Finance"],
    "location": ["New York", "San Francisco", "Chicago"],
})

merged = df.merge(dept_info, on="department", how="left")
print("\n--- Merged DataFrame with Dept Info ---")
print(merged[["name", "department", "location"]])

# ----------------------------- 13. Pivot Tables -----------------------------
pivot = pd.pivot_table(
    df,
    index="department",
    columns="salary_category",
    values="id",
    aggfunc="count",
    fill_value=0,
)
print("\n--- Pivot Table (Employee Count by Dept & Salary Category) ---")
print(pivot)

# ----------------------------- 14. Exporting -----------------------------
# Export cleaned data to CSV (in real projects, to file; here just to string)
csv_data = df.to_csv(index=False)
print("\n--- Cleaned Data (CSV Preview) ---")
print(csv_data)

# ----------------------------- 15. Wrap Up -----------------------------
"""
Key pandas essentials demonstrated:
- DataFrame creation from messy input
- Data inspection and summary stats
- Cleaning text, numeric, date columns
- Handling nulls (detect, fill, drop)
- Selection/indexing: loc, iloc, masks, query
- Sorting, renaming
- GroupBy and aggregations
- Apply/lambda transformations
- Merging DataFrames
- Pivot tables
- Exporting to CSV

This covers ~80% of real-world pandas use cases in data cleaning & analysis.
"""
