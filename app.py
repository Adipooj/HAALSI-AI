from __future__ import annotations

import re
import math
import numpy as np
import pandas as pd
import streamlit as st
import joblib

from config.haalsi_config import MODEL_FILE, SCHEMA_FILE
from inference.input_mapper import align_frame_to_schema
from inference.schema import SchemaArtifact
from models.risk_fusion import categorize_risk

st.set_page_config(page_title="HAALSI Clinical Risk Engine", layout="wide")

# =========================
# LOAD MODELS
# =========================
decline_model = joblib.load(MODEL_FILE)
trajectory_model = joblib.load(MODEL_FILE.parent / "trajectory_model.joblib")
schema = SchemaArtifact.load(SCHEMA_FILE)

feature_columns = list(schema.feature_columns)
defaults = schema.feature_defaults

# =========================
# LABEL SYSTEM
# =========================
TOKEN_MAP = {
    "walk": ("Walking Ability", "continuous"),
    "stairs": ("Climbing Stairs", "continuous"),
    "chair": ("Chair Rise", "continuous"),
    "bmi": ("Body Mass Index", "continuous"),
    "weight": ("Weight (kg)", "continuous"),
    "height": ("Height (cm)", "continuous"),
    "diabetes": ("Diabetes", "binary"),
    "stroke": ("Stroke", "binary"),
    "heart": ("Heart Disease", "binary"),
    "memory": ("Memory Function", "continuous"),
    "recall": ("Recall Ability", "continuous"),
    "age": ("Age", "continuous"),
}

def get_label_and_type(col):
    base = col.split("__")[-1].lower()
    for k, v in TOKEN_MAP.items():
        if k in base:
            return v
    return (base.replace("_", " ").title(), "continuous")

def concept_key(col):
    base = col.split("__")[-1].lower()
    for k in TOKEN_MAP:
        if k in base:
            return k
    return base

# =========================
# GROUP FEATURES
# =========================
raw_cols = [c for c in feature_columns if "__" in c]

concept_map = {}
for col in raw_cols:
    key = concept_key(col)
    concept_map.setdefault(key, []).append(col)

# =========================
# UI
# =========================
st.title("🧠 HAALSI Clinical Risk Engine")
st.markdown("Enter patient clinical parameters. System predicts decline, trajectory, and independence risk.")

with st.form("clinical_form"):

    user_inputs = {}

    weight = None
    height = None

    for concept, cols in sorted(concept_map.items()):

        label, dtype = get_label_and_type(cols[0])

        # -------------------
        # BINARY INPUT
        # -------------------
        if dtype == "binary":
            val = st.toggle(label, value=False)
            val = 1 if val else 0

        # -------------------
        # CONTINUOUS INPUT
        # -------------------
        else:
            median = defaults.get(cols[0], 0.0)

            val = st.number_input(
                label,
                value=float(median),
                step=0.1,
            )

        # Capture for BMI calculation
        if "weight" in concept:
            weight = val
        if "height" in concept:
            height = val

        for c in cols:
            user_inputs[c] = val

    # =========================
    # AUTO BMI
    # =========================
    if weight and height:
        bmi = weight / ((height / 100) ** 2)
        st.info(f"Calculated BMI: {bmi:.2f}")

        for c in concept_map.get("bmi", []):
            user_inputs[c] = bmi

    submit = st.form_submit_button("Generate Clinical Risk")

if not submit:
    st.stop()

# =========================
# DATAFRAME
# =========================
df = pd.DataFrame([user_inputs])

for col in feature_columns:
    if col not in df:
        df[col] = np.nan

df = align_frame_to_schema(df, feature_columns, defaults)

for col in df.columns:
    if pd.isna(df.loc[0, col]):
        df.loc[0, col] = defaults.get(col, 0.0)

# =========================
# MODEL
# =========================
decline = decline_model.predict_proba(df)[0, 1]
traj = trajectory_model.predict(df)[0]

traj_scaled = 1 / (1 + np.exp(-traj))
combined = np.clip(0.6 * decline + 0.4 * traj_scaled, 0, 1)

category = categorize_risk(pd.Series([combined])).iloc[0]

# =========================
# TIME ESTIMATE
# =========================
years = int(np.clip((1 - combined) * 10, 1, 10))

# =========================
# CLINICAL OUTPUT
# =========================
st.write("---")
st.subheader("🧾 Clinical Risk Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Decline Risk", f"{decline:.1%}")
col2.metric("Trajectory Risk", f"{traj_scaled:.1%}")
col3.metric("Overall Risk", f"{combined:.1%}")

# Risk Interpretation
if combined < 0.3:
    st.success("🟢 Low Risk: Patient is stable.")
elif combined < 0.6:
    st.warning("🟡 Moderate Risk: Monitor progression.")
else:
    st.error("🔴 High Risk: Early intervention recommended.")

st.metric("Estimated Time to Loss of Independence", f"{years} years")

# =========================
# CLINICAL INSIGHT
# =========================
st.write("### 🧠 Clinical Interpretation")

if combined > 0.6:
    st.write("High likelihood of decline. Consider proactive intervention.")
elif combined > 0.3:
    st.write("Moderate risk. Monitor closely.")
else:
    st.write("Currently stable.")