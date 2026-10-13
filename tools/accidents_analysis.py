# accidents_analysis.py
# Core requirement: given a CSV master file + data dictionary (xlsx),
# compute distributions (counts + percents) for any chosen column.

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd


# ----------------------------
# Data Dictionary structures
# ----------------------------

@dataclass
class ColumnMeta:
    name: str
    description: Optional[str] = None
    allowed_values: Optional[List[Union[int, str]]] = None


def _extract_allowed_values(text: object) -> Optional[List[Union[int, str]]]:
    """Parse 'allowed values' from a dictionary cell (ranges or lists) as ints or strings."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return None
    s = str(text).strip()
    if not s:
        return None

    # Normalize some common separators
    s_norm = s.replace("–", "-").replace("—", "-").replace("..", "-")

    # Find ranges like 1-12
    ranges = re.findall(r"(-?\d+)\s*-\s*(-?\d+)", s_norm)
    values: List[int] = []
    for a, b in ranges:
        a_i, b_i = int(a), int(b)
        step = 1 if a_i <= b_i else -1
        values.extend(list(range(a_i, b_i + step, step)))

    # Find standalone ints
    ints = re.findall(r"(?<![A-Za-z])(-?\d+)(?![A-Za-z])", s_norm)
    for x in ints:
        values.append(int(x))

    if values:
        return sorted(set(values))

    # Fallback: try comma-separated tokens (strings)
    if "," in s:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return parts or None

    return None


def load_data_dictionary(xlsx_path: str) -> Dict[str, ColumnMeta]:
    """Load an Excel data dictionary into {column_name: ColumnMeta}, scanning all sheets."""
    xl = pd.ExcelFile(xlsx_path)
    meta: Dict[str, ColumnMeta] = {}

    name_keys = {"column", "field", "name", "עמודה", "שם עמודה", "שם_עמודה", "קוד", "code"}
    desc_keys = {"description", "desc", "תיאור", "הסבר"}
    allowed_keys = {"values", "allowed", "range", "ערכים", "ערכים אפשריים", "טווח"}

    def normalize_col(c: object) -> str:
        """Normalize a column name for keyword matching."""
        return str(c).strip().lower()

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if df.empty:
            continue

        cols_norm = {c: normalize_col(c) for c in df.columns}

        name_col = None
        desc_col = None
        allowed_col = None

        for c, c_norm in cols_norm.items():
            if any(k in c_norm for k in name_keys):
                name_col = c
            if any(k in c_norm for k in desc_keys):
                desc_col = c
            if any(k in c_norm for k in allowed_keys):
                allowed_col = c

        if name_col is None:
            continue

        for _, row in df.iterrows():
            raw_name = row.get(name_col, None)
            if raw_name is None or (isinstance(raw_name, float) and pd.isna(raw_name)):
                continue

            col_name = str(raw_name).strip()
            if not col_name:
                continue

            description = None
            if desc_col is not None:
                raw_desc = row.get(desc_col, None)
                if raw_desc is not None and not (isinstance(raw_desc, float) and pd.isna(raw_desc)):
                    description = str(raw_desc).strip() or None

            allowed_values = None
            if allowed_col is not None:
                allowed_values = _extract_allowed_values(row.get(allowed_col, None))

            if col_name not in meta:
                meta[col_name] = ColumnMeta(name=col_name, description=description, allowed_values=allowed_values)
            else:
                if meta[col_name].description is None and description:
                    meta[col_name].description = description
                if meta[col_name].allowed_values is None and allowed_values:
                    meta[col_name].allowed_values = allowed_values

    return meta


# ----------------------------
# Analysis logic
# ----------------------------

class AccidentsAnalyzer:
    def __init__(self, csv_path: str, dictionary_xlsx_path: Optional[str] = None) -> None:
        """Load the CSV and, if provided, the data dictionary."""
        self.csv_path = csv_path
        self.dictionary_xlsx_path = dictionary_xlsx_path

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        self.df = pd.read_csv(csv_path, low_memory=False)

        self.meta: Dict[str, ColumnMeta] = {}
        if dictionary_xlsx_path:
            if not os.path.exists(dictionary_xlsx_path):
                raise FileNotFoundError(f"Dictionary XLSX file not found: {dictionary_xlsx_path}")
            self.meta = load_data_dictionary(dictionary_xlsx_path)

    def analyze_column(
        self,
        column_name: str,
        percent_of: str = "all",          # "all" or "non_null"
        include_nulls: bool = True,
        show_all_allowed: bool = False,   # if dictionary has allowed values, show missing with 0 count
        report_unknowns: bool = False     # show values not in allowed list
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        """Return a distribution DataFrame (Value, Count, Percent), optionally with unknowns."""
        if column_name not in self.df.columns:
            raise ValueError(f"Column '{column_name}' not found in CSV.")

        s = self.df[column_name]

        if percent_of not in {"all", "non_null"}:
            raise ValueError("percent_of must be 'all' or 'non_null'.")

        denom = len(self.df) if percent_of == "all" else int(s.notna().sum())

        counts = s.value_counts(dropna=not include_nulls is False) if include_nulls else s.value_counts(dropna=True)

        dist = (
            counts.rename_axis("Value")
            .reset_index(name="Count")
        )
        dist["Percent"] = (dist["Count"] / denom * 100.0) if denom else 0.0

        # Always create unknowns_df with columns, even if empty
        unknowns_df = pd.DataFrame(columns=["Value", "Count"])
        meta = self.meta.get(column_name)

        if show_all_allowed and meta and meta.allowed_values:
            allowed = meta.allowed_values

            dist_values_set = set(dist["Value"].astype(str).tolist())
            allowed_str = [str(x) for x in allowed]

            full = pd.DataFrame({"Value": allowed_str})
            merged = full.merge(
                dist.assign(Value=dist["Value"].astype(str)),
                on="Value",
                how="left"
            )
            merged["Count"] = merged["Count"].fillna(0).astype(int)
            merged["Percent"] = (merged["Count"] / denom * 100.0) if denom else 0.0
            dist = merged

            if report_unknowns:
                unknown_values = sorted(list(dist_values_set - set(allowed_str)))
                unknowns_df = pd.DataFrame({"Value": unknown_values})
                if not unknowns_df.empty:
                    unknown_counts = (
                        s.astype(str)
                        .value_counts(dropna=not include_nulls)
                        .rename_axis("Value")
                        .reset_index(name="Count")
                    )
                    unknowns_df = unknowns_df.merge(unknown_counts, on="Value", how="left").fillna({"Count": 0})
                    unknowns_df["Count"] = unknowns_df["Count"].astype(int)
                else:
                    unknowns_df = pd.DataFrame(columns=["Value", "Count"])

        else:
            if report_unknowns and meta and meta.allowed_values:
                allowed_str_set = set(str(x) for x in meta.allowed_values)
                found_str_set = set(dist["Value"].astype(str).tolist())
                unknown_values = sorted(list(found_str_set - allowed_str_set))

                unknowns_df = pd.DataFrame({"Value": unknown_values})
                if not unknowns_df.empty:
                    unknown_counts = (
                        s.astype(str)
                        .value_counts(dropna=not include_nulls)
                        .rename_axis("Value")
                        .reset_index(name="Count")
                    )
                    unknowns_df = unknowns_df.merge(unknown_counts, on="Value", how="left").fillna({"Count": 0})
                    unknowns_df["Count"] = unknowns_df["Count"].astype(int)
                else:
                    unknowns_df = pd.DataFrame(columns=["Value", "Count"])

        if meta:
            dist.attrs["description"] = meta.description
            dist.attrs["allowed_values"] = meta.allowed_values

        return (dist, unknowns_df) if report_unknowns else dist


# ----------------------------
# Standalone analysis example
# ----------------------------

if __name__ == "__main__":
    # Make paths relative to THIS file (avoids FileNotFound issues when running from other folders)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    CSV_PATH = os.path.join(BASE_DIR, "accidents_raw_master.csv")
    DICT_XLSX = os.path.join(BASE_DIR, "data-dictionary-document-accidents.xlsx")

    analyzer = AccidentsAnalyzer(csv_path=CSV_PATH, dictionary_xlsx_path=DICT_XLSX)

    # Select the column used by this standalone example.
    COLUMN_TO_ANALYZE = "MEZEG_AVIR"

    dist = analyzer.analyze_column(
        COLUMN_TO_ANALYZE,
        percent_of="all",
        include_nulls=True,
        show_all_allowed=True,
        report_unknowns=True
    )

    if isinstance(dist, tuple):
        dist_df, unknowns_df = dist
        print("=== Distribution ===")
        print(dist_df.head(30))
        print("\n=== Unknown values (not in dictionary allowed list) ===")
        print(unknowns_df.head(30))
    else:
        print(dist.head(30))
