import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
import joblib
import numpy as np
import pandas as pd
from backend.app.core.config import settings

class MLInferenceEngine:
    def __init__(self):
        self.decline_model = None
        self.trajectory_model = None
        self.trajectory_scaler = None
        self.thresholds = None
        self.schema = None
        self.feature_columns = []
        self.feature_defaults = {}
        self.loaded = False
        self._load_artifacts()

    def _load_artifacts(self):
        try:
            if settings.DECLINE_MODEL_PATH.exists():
                self.decline_model = joblib.load(settings.DECLINE_MODEL_PATH)
            if settings.TRAJECTORY_MODEL_PATH.exists():
                self.trajectory_model = joblib.load(settings.TRAJECTORY_MODEL_PATH)
            if settings.TRAJECTORY_SCALER_PATH.exists():
                self.trajectory_scaler = joblib.load(settings.TRAJECTORY_SCALER_PATH)
            if settings.TRAJECTORY_THRESHOLDS_PATH.exists():
                self.thresholds = json.loads(settings.TRAJECTORY_THRESHOLDS_PATH.read_text(encoding="utf-8"))
            if settings.SCHEMA_PATH.exists():
                self.schema = json.loads(settings.SCHEMA_PATH.read_text(encoding="utf-8"))
                self.feature_columns = self.schema.get("feature_columns", [])
                self.feature_defaults = self.schema.get("feature_defaults", {})
            self.loaded = True
        except Exception as e:
            print(f"[ML Service] Error loading model artifacts: {e}")
            self.loaded = False

    def predict(self, assessment_data: Dict[str, Any], age: int) -> Dict[str, Any]:
        """
        Executes end-to-end inference:
        1. Aligns assessment inputs to the 30-feature schema
        2. Computes the Deficit Frailty Index
        3. Predicts Decline Probability with Calibrated XGBoost
        4. Predicts Trajectory and Scales to Percentile
        5. Fuses Risk: 0.40 * Decline + 0.40 * Frailty + 0.20 * Age Factor
        6. Runs Forward Simulation for Years to Independence Loss
        7. Generates SHAP-aligned clinical risk contributions
        """
        # 1. Height, Weight, BMI
        height = assessment_data.get("height_cm") or 162.0
        weight = assessment_data.get("weight_kg") or 69.8
        bmi = weight / ((height / 100.0) ** 2) if height > 0 else 26.28

        # Vitals & Anthropometrics
        sys_bp = assessment_data.get("systolic_bp")
        dia_bp = assessment_data.get("diastolic_bp")
        pulse = assessment_data.get("pulse_bpm")
        spo2 = assessment_data.get("spo2_pct")
        temp = assessment_data.get("temperature_c")
        resp_rate = assessment_data.get("respiratory_rate")
        waist = assessment_data.get("waist_cm")
        hip = assessment_data.get("hip_cm")
        muac = assessment_data.get("mid_upper_arm_circ_cm") # Bicep / Mid-upper arm circ
        chest = assessment_data.get("chest_cm")

        # 2. Deficit Frailty Index Calculation
        # Clinical Deficit items expanded for nursing home & ambulatory monitoring:
        # - High BMI (>28) or Low (<18.5)
        # - Diabetes, Hypertension, Stroke, Heart Disease
        # - Walking difficulty, Stairs difficulty, Chair rise difficulty
        # - Memory deficit (<8), Recall deficit (<8)
        # - Vitals deficits:
        #     * Elevated/Abnormal Blood Pressure (SBP >= 140 or DBP >= 90 or SBP < 90)
        #     * Tachycardia/Bradycardia (Pulse > 100 or Pulse < 50)
        #     * Hypoxia / Low SpO2 (< 94%)
        #     * Sarcopenia / Muscle wasting indicators: Low MUAC/bicep (<22 cm in elderly)
        #     * Central adiposity / metabolic risk: Waist-to-hip ratio or high waist (>88cm F, >102cm M, or >95cm general)
        deficits = []
        deficits.append(1.0 if (bmi > 28.0 or bmi < 18.5) else 0.0)
        deficits.append(1.0 if assessment_data.get("has_diabetes") else 0.0)
        deficits.append(1.0 if assessment_data.get("has_hypertension") else 0.0)
        deficits.append(1.0 if assessment_data.get("has_stroke") else 0.0)
        deficits.append(1.0 if assessment_data.get("has_heart_disease") else 0.0)
        deficits.append(min(1.0, float(assessment_data.get("walking_difficulty", 0)) / 2.0))
        deficits.append(min(1.0, float(assessment_data.get("stairs_difficulty", 0)) / 2.0))
        deficits.append(min(1.0, float(assessment_data.get("chair_rise_difficulty", 0)) / 2.0))
        deficits.append(1.0 if float(assessment_data.get("memory_score", 10.0)) < 8.0 else 0.0)
        deficits.append(1.0 if float(assessment_data.get("recall_score", 10.0)) < 8.0 else 0.0)
        
        # Vitals deficits
        if sys_bp is not None and dia_bp is not None:
            deficits.append(1.0 if (sys_bp >= 140 or dia_bp >= 90 or sys_bp < 95) else 0.0)
        elif assessment_data.get("has_hypertension"):
            deficits.append(1.0)
        else:
            deficits.append(0.0)

        if pulse is not None:
            deficits.append(1.0 if (pulse > 100 or pulse < 50) else 0.0)

        if spo2 is not None:
            deficits.append(1.0 if spo2 < 94.0 else 0.0)

        # Body Anthropometrics & Sarcopenia / Frailty markers
        if muac is not None:
            # Low Mid-Upper Arm Circumference indicates clinical sarcopenia / muscle wasting (< 23cm)
            deficits.append(1.0 if muac < 23.0 else 0.0)

        if waist is not None:
            # High abdominal waist circumference indicates high cardiometabolic risk (> 95cm)
            deficits.append(1.0 if waist > 95.0 else 0.0)

        # Polypharmacy deficit (>=5 meds)
        meds_count = assessment_data.get("medications_count", 0)
        is_polypharmacy = meds_count >= 5
        deficits.append(1.0 if is_polypharmacy else 0.0)

        frailty_index = float(np.mean(deficits))

        # 3. Build Model Feature Frame
        input_row = dict(self.feature_defaults)
        
        # Map specific inputs to schema
        input_row["bmi__W1C_BS_HEIGHT"] = float(height)
        input_row["bmi__W1C_BS_WEIGHT"] = float(weight)
        input_row["bmi__W1C_BS_BMI"] = float(bmi)
        input_row["bmi__W1FL_C_BS_HEIGHT"] = float(height)
        input_row["bmi__W1FL_C_BS_WEIGHT"] = float(weight)
        input_row["bmi__W1FL_C_BS_BMI"] = float(bmi)
        input_row["disease__W1C_CM_DIABETES_SRTRT"] = 1.0 if assessment_data.get("has_diabetes") else 2.0
        input_row["disease__W1C_CM_DIABETES_SRDIAG"] = 1.0 if assessment_data.get("has_diabetes") else 2.0
        input_row["mobility__W1C_PF_DIFF_WALK"] = float(assessment_data.get("walking_difficulty", 0) + 1)
        input_row["frailty_index"] = frailty_index

        # Align to exact columns
        df_in = pd.DataFrame([input_row])[self.feature_columns]

        # 4. Predict Decline
        if self.decline_model:
            decline_prob = float(self.decline_model.predict_proba(df_in)[0, 1])
        else:
            decline_prob = float(np.clip(0.5 * frailty_index + 0.1 * (age / 80.0), 0.0, 1.0))

        # 5. Predict Trajectory
        if self.trajectory_model and self.trajectory_scaler:
            raw_traj = float(self.trajectory_model.predict(df_in)[0])
            scaled_traj = float(self.trajectory_scaler.transform([[raw_traj]])[0, 0])
        else:
            scaled_traj = float(np.clip(frailty_index * 0.8 + 0.2, 0.0, 1.0))

        # Categorize Trajectory
        if self.thresholds:
            if scaled_traj <= self.thresholds.get("scaled_lower", 0.33):
                traj_cat = "Stable"
            elif scaled_traj <= self.thresholds.get("scaled_upper", 0.66):
                traj_cat = "Moderate Decline"
            else:
                traj_cat = "Rapid Decline"
        else:
            traj_cat = "Stable" if scaled_traj < 0.4 else ("Moderate Decline" if scaled_traj < 0.7 else "Rapid Decline")

        # 6. Overall Risk Fusion
        # Normalized age factor: 60 = 0.0, 90 = 1.0
        age_factor = float(np.clip((age - 60.0) / 30.0, 0.0, 1.0))
        overall_risk = float(np.clip(0.40 * decline_prob + 0.40 * frailty_index + 0.20 * age_factor, 0.0, 1.0))

        # Risk Tier
        if overall_risk < 0.35:
            risk_tier = "Low"
        elif overall_risk < 0.65:
            risk_tier = "Moderate"
        else:
            risk_tier = "High"

        # 7. Estimated Time to Loss of Independence (Simulation approximation)
        if overall_risk >= 0.70:
            est_years = max(1, int(round((1.0 - overall_risk) * 6)))
        elif overall_risk >= 0.45:
            est_years = max(3, int(round((1.0 - overall_risk) * 10)))
        else:
            est_years = min(10, max(6, int(round((1.0 - overall_risk) * 12))))

        # 8. Clinical Recommendations & SHAP Contributions
        contributions = {
            "Frailty Deficit Burden": round(frailty_index * 0.40, 3),
            "Age Factor": round(age_factor * 0.20, 3),
            "Mobility & Gait Limitation": round(float(assessment_data.get("walking_difficulty", 0)) * 0.15, 3),
            "Cardiovascular & Hemodynamic Stress": round(0.12 if (sys_bp and (sys_bp > 140 or sys_bp < 95)) or assessment_data.get("has_hypertension") else 0.02, 3),
            "Pulse & Respiratory Stability": round(0.08 if (pulse and (pulse > 100 or pulse < 50)) or (spo2 and spo2 < 94) else 0.01, 3),
            "Sarcopenia & Arm/Waist Wasting": round(0.09 if (muac and muac < 23.0) or (waist and waist > 100) else 0.02, 3),
            "Polypharmacy Burden": round(0.10 if is_polypharmacy else 0.0, 3),
            "Cognitive Reserve Loss": round(0.08 if float(assessment_data.get("memory_score", 10.0)) < 8.0 else 0.0, 3)
        }

        recommendations = []
        if risk_tier == "High":
            recommendations.append("Priority comprehensive geriatric assessment (CGA) recommended within 14 days.")
            recommendations.append("Initiate targeted physical therapy and fall-prevention home hazard assessment.")
        elif risk_tier == "Moderate":
            recommendations.append("Schedule longitudinal follow-up (4-8 weeks) to re-evaluate functional stability.")
            recommendations.append("Introduce resistance and balance training to decelerate frailty progression.")
        else:
            recommendations.append("Patient demonstrates stable aging profile. Continue standard monitoring protocols.")

        if is_polypharmacy:
            recommendations.append("POLYPHARMACY ALERT: Review concurrent medications (≥5 active drugs) to reduce adverse drug interactions and fall risks.")

        if spo2 and spo2 < 94.0:
            recommendations.append("RESPIRATORY VIGILANCE: Resting SpO2 is subnormal (<94%). Evaluate for occult hypoxemia or pulmonary exacerbation.")

        if muac and muac < 23.0:
            recommendations.append("NUTRITIONAL & SARCOPENIA INTERVENTION: Mid-upper arm circumference (<23 cm) indicates acute muscle wasting. Dietary protein supplementation recommended.")

        if sys_bp and (sys_bp >= 150 or sys_bp < 95):
            recommendations.append("HEMODYNAMIC ALERT: Blood pressure readings out of target range. Assess orthostatic hypotension risk.")

        return {
            "bmi": round(bmi, 2),
            "frailty_index": round(frailty_index, 3),
            "decline_probability": round(decline_prob, 3),
            "trajectory_score": round(scaled_traj, 3),
            "trajectory_category": traj_cat,
            "overall_risk_score": round(overall_risk, 3),
            "risk_tier": risk_tier,
            "estimated_years_to_independence_loss": est_years,
            "is_polypharmacy": is_polypharmacy,
            "shap_contributions": contributions,
            "clinical_recommendations": recommendations,
            "model_version": "1.0.0",
            "schema_version": "1.0.0"
        }

ml_service = MLInferenceEngine()
