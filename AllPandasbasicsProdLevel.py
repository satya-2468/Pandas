#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Production-style pandas pipeline template.

This script demonstrates:
  - Modular ETL pipeline: load → clean → analyze → export
  - Logging instead of prints
  - Data validation before/after cleaning
  - Config-driven parameters
  - Type hints for clarity
  - Functions testable in isolation
"""

import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import numpy as np


# ----------------------------- Config ---------------------------------
CONFIG: Dict[str, Any] = {
    "output_dir": Path("./output"),
    "fill_age_strategy": "median",  # "mean" or "median"
    "fill_salary_strategy": "mean",
    "export_file": "cleaned_data.csv",
}


# ----------------------------- Logging ---------------------------------
def setup_logging() -> None:
    """Configure logging for production-style output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


log = logging.getLogger("pandas-pipeline")


# ----------------------------- Load ---------------------------------
def load_data() -> pd.DataFrame:
    """
    Simulate loading raw data.
    In production, this would load from CSV, DB, or API.
    """
    raw_data = {
        "id": [1, 2, 3, 4, 5, 6],
        "name": [" alice ", "BOB", None, "Charlie", "david", "Eve "],
        "age": ["25", "thirty", "40", None, "35", "29"],
        "salary": [50000, 60000, None, 70000, "80000", "not available"],
        "join_date": [
            "2021-01-10",
            "10/02/2021",
            "March 3, 2021",
            None,
            "2021/05/20",
            "20210615",
        ],
        "dept": ["HR", "IT", "Finance", "Finance", "IT", "HR"],
    }
    df = pd.DataFrame(raw_data)
    log.info("Loaded raw data with %d rows, %d cols", df.shape[0], df.shape[1])
    return df


# ----------------------------- Validation ---------------------------------
def validate_raw(df: pd.DataFrame) -> None:
    """Validate expected schema before cleaning."""
    required_columns = {"id", "name", "age", "salary", "join_date", "dept"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df["id"].duplicated().any():
        raise ValueError("Duplicate IDs found in raw data")
    log.info("Raw data validation passed")


def validate_clean(df: pd.DataFrame) -> None:
    """Validate cleaned data after transformation."""
    if df["age"].isnull().any():
        raise ValueError("Nulls remain in 'age' after cleaning")
    if df["salary"].isnull().any():
        raise ValueError("Nulls remain in 'salary' after cleaning")
    if not pd.api.types.is_datetime64_any_dtype(df["join_date"]):
        raise TypeError("'join_date' not converted to datetime")
    log.info("Clean data validation passed")


# ----------------------------- Cleaning ---------------------------------
def clean_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Clean raw DataFrame according to config rules."""
    df = df.copy()

    # Clean names
    df["name"] = df["name"].str.strip().str.title().fillna("Unknown")

    # Convert age to numeric
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    if config["fill_age_strategy"] == "mean":
        df["age"] = df["age"].fillna(df["age"].mean())
    else:
        df["age"] = df["age"].fillna(df["age"].median())

    # Clean salary
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
    if config["fill_salary_strategy"] == "mean":
        df["salary"] = df["salary"].fillna(df["salary"].mean())
    else:
        df["salary"] = df["salary"].fillna(df["salary"].median())

    # Parse dates
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    df["join_year"] = df["join_date"].dt.year
    df["join_month"] = df["join_date"].dt.month
    df["join_weekday"] = df["join_date"].dt.day_name()

    # Rename dept → department
    df = df.rename(columns={"dept": "department"})

    log.info("Cleaned data: %d rows, %d cols", df.shape[0], df.shape[1])
    return df


# ----------------------------- Analysis ---------------------------------
def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform simple analysis (groupby, aggregations, pivot)."""
    results: Dict[str, Any] = {}

    results["avg_salary_by_dept"] = df.groupby("department")["salary"].mean().to_dict()
    results["salary_stats_by_dept"] = df.groupby("department")["salary"].agg(
        ["mean", "min", "max", "count"]
    )

    pivot = pd.pivot_table(
        df,
        index="department",
        columns="join_year",
        values="id",
        aggfunc="count",
        fill_value=0,
    )
    results["employee_count_pivot"] = pivot

    log.info("Analysis complete: computed groupby and pivot")
    return results


# ----------------------------- Export ---------------------------------
def export_data(df: pd.DataFrame, config: Dict[str, Any]) -> Path:
    """Export cleaned data to CSV."""
    output_dir: Path = config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / config["export_file"]
    df.to_csv(file_path, index=False)
    log.info("Exported cleaned data to %s", file_path)
    return file_path


# ----------------------------- Main ---------------------------------
def main() -> None:
    setup_logging()

    # Step 1: Load
    df_raw = load_data()

    # Step 2: Validate raw
    validate_raw(df_raw)

    # Step 3: Clean
    df_clean = clean_data(df_raw, CONFIG)

    # Step 4: Validate clean
    validate_clean(df_clean)

    # Step 5: Analyze
    results = analyze_data(df_clean)

    log.info("Average salary by department: %s", results["avg_salary_by_dept"])
    log.info("Salary stats by department:\n%s", results["salary_stats_by_dept"])
    log.info("Pivot table (employee count by dept & year):\n%s", results["employee_count_pivot"])

    # Step 6: Export
    export_data(df_clean, CONFIG)


if __name__ == "__main__":
    main()
