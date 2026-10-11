from __future__ import annotations

import pandas as pd
import numpy as np


# ---------------------------
# DOMAIN DETECTION (KEY FIX)
# ---------------------------

def detect_domain(col: str) -> str | None:
    c = col.lower()

    if "walk" in c or "stairs" in c or "chair" in c:
        return "mobility"
    elif "grip" in c:
        return "grip"
    elif "bp" in c or "pressure" in c or "systolic" in c:
        return "blood_pressure"
    elif "bmi" in c or "weight" in c or "height" in c:
        return "bmi"
    elif "diabetes" in c or "stroke" in c or "heart" in c:
        return "disease"
    elif "hiv" in c or "cd4" in c:
        return "hiv"
    elif "memory" in c or "recall" in c or "cog" in c:
        return "cognition"
    elif "depress" in c or "sad" in c:
        return "mental_health"
    elif "social" in c or "friend" in c:
        return "social"
    else:
        return None


# ---------------------------
# BUILD DOMAIN VARIABLE LISTS
# ---------------------------

def build_domain_variable_lists(df: pd.DataFrame) -> dict[str, dict[str, list[str]]]:
    """
    Robust mapping using actual dataset columns (NOT crosswalk)
    """

    domain_varlists = {}

    for col in df.columns:

        # -----------------------
        # Detect wave
        # -----------------------
        if col.startswith("W1"):
            wave = "W1"
        elif col.startswith("W2"):
            wave = "W2"
        elif col.startswith("W3"):
            wave = "W3"
        else:
            continue

        # -----------------------
        # Detect domain
        # -----------------------
        domain = detect_domain(col)

        if domain is None:
            continue

        # -----------------------
        # Initialize
        # -----------------------
        if domain not in domain_varlists:
            domain_varlists[domain] = {
                "W1": [],
                "W2": [],
                "W3": []
            }

        domain_varlists[domain][wave].append(col)

    return domain_varlists


# ---------------------------
# BUILD FEATURE TABLE
# ---------------------------

def build_feature_table(
    df: pd.DataFrame,
    domain_varlists: dict[str, dict[str, list[str]]],
    wave: str = "W1"
) -> pd.DataFrame:

    frames = []

    for domain, waves in domain_varlists.items():

        vars_ = waves.get(wave, [])

        if not vars_:
            continue

        cols = [v for v in vars_ if v in df.columns]

        if not cols:
            continue

        subset = df[cols].copy()

        # Prefix with domain for clarity
        subset = subset.add_prefix(f"{domain}__")

        frames.append(subset)

    if not frames:
        return pd.DataFrame(index=df.index)

    return pd.concat(frames, axis=1)


# ---------------------------
# PAIRWISE WAVE FRAMES (DECLINE)
# ---------------------------

def pairwise_domain_frames(
    df: pd.DataFrame,
    domain_varlists: dict[str, dict[str, list[str]]],
    wave_base: str = "W1",
    wave_follow: str = "W2"
):

    base_frames = []
    follow_frames = []

    for domain, waves in domain_varlists.items():

        base_vars = waves.get(wave_base, [])
        follow_vars = waves.get(wave_follow, [])

        for base_var in base_vars:
            follow_var = base_var.replace(wave_base, wave_follow, 1)

            if base_var in df.columns and follow_var in df.columns:
                base_frames.append(
                    df[[base_var]].rename(
                        columns={base_var: f"{domain}__{base_var}"}
                    )
                )

                follow_frames.append(
                    df[[follow_var]].rename(
                        columns={follow_var: f"{domain}__{follow_var}"}
                    )
                )

    base = pd.concat(base_frames, axis=1) if base_frames else pd.DataFrame(index=df.index)
    follow = pd.concat(follow_frames, axis=1) if follow_frames else pd.DataFrame(index=df.index)

    return base, follow


# ---------------------------
# NUMERIC COERCION
# ---------------------------

def coalesce_numeric_frame(frame: pd.DataFrame) -> pd.DataFrame:

    out = frame.copy()

    for c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    return out