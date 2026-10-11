from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from config.haalsi_config import CROSSWALK_PATH


def _normalize_col(col: Any) -> str:
    return re.sub(r"\s+", " ", str(col).strip().lower())


def load_crosswalk(path: str | Path = CROSSWALK_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Crosswalk file not found: {path}")

    xls = pd.ExcelFile(path)
    frames = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        if df.empty:
            continue
        df = df.copy()
        df.columns = [_normalize_col(c) for c in df.columns]
        df["source_sheet"] = sheet
        frames.append(df)

    if not frames:
        raise ValueError(f"No readable sheets found in crosswalk: {path}")

    crosswalk = pd.concat(frames, ignore_index=True)
    crosswalk = crosswalk.dropna(how="all")
    return crosswalk


def guess_columns(crosswalk: pd.DataFrame) -> dict[str, str | None]:
    cols = list(crosswalk.columns)

    def find_contains(tokens: list[str]) -> str | None:
        for c in cols:
            cc = c.lower()
            if all(t in cc for t in tokens):
                return c
        return None

    return {
        "w1": find_contains(["wave", "1"]) or find_contains(["w1"]) or find_contains(["wave 1"]),
        "w2": find_contains(["wave", "2"]) or find_contains(["w2"]) or find_contains(["wave 2"]),
        "w3": find_contains(["wave", "3"]) or find_contains(["w3"]) or find_contains(["wave 3"]),
        "question": find_contains(["question", "text"]) or find_contains(["question"]),
        "label": find_contains(["label"]),
        "concept": find_contains(["concept"]) or find_contains(["topic"]),
        "varname": find_contains(["varname"]) or find_contains(["variable", "name"]),
    }


def clean_crosswalk(crosswalk: pd.DataFrame) -> pd.DataFrame:
    out = crosswalk.copy()
    out.columns = [_normalize_col(c) for c in out.columns]
    out = out.dropna(how="all")
    return out


def build_variable_registry(crosswalk: pd.DataFrame) -> pd.DataFrame:
    crosswalk = clean_crosswalk(crosswalk)
    cols = guess_columns(crosswalk)

    if cols["varname"] is None and cols["question"] is None:
        raise ValueError(
            "Could not detect the expected crosswalk columns. "
            "Inspect the workbook and update `guess_columns()`."
        )

    out = crosswalk.copy()

    if cols["question"] is None:
        out["question_text"] = ""
    else:
        out["question_text"] = out[cols["question"]].fillna("").astype(str)

    if cols["label"] is None:
        out["label_text"] = ""
    else:
        out["label_text"] = out[cols["label"]].fillna("").astype(str)

    if cols["concept"] is None:
        out["concept_text"] = ""
    else:
        out["concept_text"] = out[cols["concept"]].fillna("").astype(str)

    if cols["varname"] is None:
        out["varname_text"] = ""
    else:
        out["varname_text"] = out[cols["varname"]].fillna("").astype(str)

    # Keep a single searchable text field
    out["search_text"] = (
        out["question_text"].fillna("") + " " +
        out["label_text"].fillna("") + " " +
        out["concept_text"].fillna("") + " " +
        out["varname_text"].fillna("")
    ).str.lower()

    return out