export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  organization_id: string;
}

export interface Participant {
  id: string;
  organization_id: string;
  participant_code: string;
  age: number;
  gender: string;
  contact_phone?: string;
  caregiver_name?: string;
  caregiver_phone?: string;
  is_demo: boolean;
  created_at: string;
}

export interface Assessment {
  id: string;
  participant_id: string;
  assessor_id: string;
  assessment_date: string;
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
  systolic_bp?: number;
  diastolic_bp?: number;
  pulse_bpm?: number;
  spo2_pct?: number;
  temperature_c?: number;
  respiratory_rate?: number;
  waist_cm?: number;
  hip_cm?: number;
  mid_upper_arm_circ_cm?: number;
  chest_cm?: number;
  has_diabetes: boolean;
  has_hypertension: boolean;
  has_stroke: boolean;
  has_heart_disease: boolean;
  walking_difficulty: number;
  stairs_difficulty: number;
  chair_rise_difficulty: number;
  memory_score: number;
  recall_score: number;
  medications_count: number;
  medications_list?: string[];
  is_polypharmacy: boolean;
  frailty_index: number;
  decline_probability: number;
  trajectory_score: number;
  trajectory_category: string;
  overall_risk_score: number;
  risk_tier: 'Low' | 'Moderate' | 'High';
  estimated_years_to_independence_loss?: number;
  model_version: string;
  schema_version: string;
  shap_contributions?: Record<string, number>;
  clinical_recommendations?: string[];
  created_at: string;
}

export interface DashboardMetrics {
  total_participants: number;
  total_assessments: number;
  high_risk_count: number;
  moderate_risk_count: number;
  low_risk_count: number;
  polypharmacy_alert_count: number;
  average_frailty_index: number;
  recent_assessments: Assessment[];
}
