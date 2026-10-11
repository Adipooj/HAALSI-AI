import React, { useState } from 'react';
import { ArrowLeft, Activity, Pill, Heart, Brain, User, AlertCircle, Thermometer, Gauge, Ruler } from 'lucide-react';
import { api } from '../lib/api';
import { Participant } from '../types';
import { translations } from '../lib/i18n';

interface AssessmentFormProps {
  participant: Participant;
  onBack: () => void;
  onComplete: (assessment: any) => void;
  lang: 'en' | 'hi';
}

export const AssessmentFormView: React.FC<AssessmentFormProps> = ({ participant, onBack, onComplete, lang }) => {
  const t = translations[lang];

  // Assessment Date
  const [assessmentDate, setAssessmentDate] = useState(new Date().toISOString().split('T')[0]);

  // Vitals & Hemodynamics
  const [heightCm, setHeightCm] = useState(160);
  const [weightKg, setWeightKg] = useState(65);
  const [systolicBp, setSystolicBp] = useState(130);
  const [diastolicBp, setDiastolicBp] = useState(80);
  const [pulseBpm, setPulseBpm] = useState(72);
  const [spo2Pct, setSpo2Pct] = useState(98);
  const [temperatureC, setTemperatureC] = useState(36.6);
  const [respRate, setRespRate] = useState(16);

  // Body Anthropometrics & Sarcopenia Markers
  const [waistCm, setWaistCm] = useState(85);
  const [hipCm, setHipCm] = useState(96);
  const [muacCm, setMuacCm] = useState(26.5); // Mid-upper arm / bicep
  const [chestCm, setChestCm] = useState(92);

  // Chronic Conditions
  const [hasDiabetes, setHasDiabetes] = useState(false);
  const [hasHypertension, setHasHypertension] = useState(false);
  const [hasStroke, setHasStroke] = useState(false);
  const [hasHeartDisease, setHasHeartDisease] = useState(false);

  // Functional & Mobility
  const [walkingDiff, setWalkingDiff] = useState(0);
  const [stairsDiff, setStairsDiff] = useState(0);
  const [chairDiff, setChairDiff] = useState(0);

  // Cognition
  const [memoryScore, setMemoryScore] = useState(10);
  const [recallScore, setRecallScore] = useState(10);

  // Medications & Polypharmacy
  const [medCount, setMedCount] = useState(2);
  const [medList, setMedList] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Auto calculate BMI
  const bmi = weightKg && heightCm ? (weightKg / ((heightCm / 100) ** 2)).toFixed(1) : '25.0';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        participant_id: participant.id,
        assessment_date: assessmentDate ? new Date(assessmentDate).toISOString() : new Date().toISOString(),
        height_cm: Number(heightCm),
        weight_kg: Number(weightKg),
        systolic_bp: Number(systolicBp),
        diastolic_bp: Number(diastolicBp),
        pulse_bpm: Number(pulseBpm),
        spo2_pct: Number(spo2Pct),
        temperature_c: Number(temperatureC),
        respiratory_rate: Number(respRate),
        waist_cm: Number(waistCm),
        hip_cm: Number(hipCm),
        mid_upper_arm_circ_cm: Number(muacCm),
        chest_cm: Number(chestCm),
        has_diabetes: hasDiabetes,
        has_hypertension: hasHypertension,
        has_stroke: hasStroke,
        has_heart_disease: hasHeartDisease,
        walking_difficulty: Number(walkingDiff),
        stairs_difficulty: Number(stairsDiff),
        chair_rise_difficulty: Number(chairDiff),
        memory_score: Number(memoryScore),
        recall_score: Number(recallScore),
        medications_count: Number(medCount),
        medications_list: medList ? medList.split(',').map((s) => s.trim()) : [],
      };
      const res = await api.createAssessment(payload);
      onComplete(res);
    } catch (err: any) {
      alert(err.message || 'Error generating assessment');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50">
          <ArrowLeft className="w-4 h-4 text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t.newAssessment}</h1>
          <p className="text-sm text-slate-500">
            Participant: <span className="font-semibold text-slate-800">{participant.participant_code}</span> ({participant.gender}, {participant.age} yrs)
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Assessment Date Field */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <label className="text-sm font-semibold text-slate-800">{t.assessmentDateLabel}</label>
          <input
            type="date"
            value={assessmentDate}
            onChange={(e) => setAssessmentDate(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm text-slate-700 font-medium"
          />
        </div>

        {/* Step 1: Nursing Home Vitals & Hemodynamics */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Gauge className="w-4 h-4 text-sky-600" /> {t.vitalsTitle}
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.systolic}</label>
              <input
                type="number"
                value={systolicBp}
                onChange={(e) => setSystolicBp(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.diastolic}</label>
              <input
                type="number"
                value={diastolicBp}
                onChange={(e) => setDiastolicBp(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.pulse}</label>
              <input
                type="number"
                value={pulseBpm}
                onChange={(e) => setPulseBpm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.spo2}</label>
              <input
                type="number"
                value={spo2Pct}
                onChange={(e) => setSpo2Pct(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.temp}</label>
              <input
                type="number"
                step="0.1"
                value={temperatureC}
                onChange={(e) => setTemperatureC(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.respRate}</label>
              <input
                type="number"
                value={respRate}
                onChange={(e) => setRespRate(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Body Anthropometrics & Sarcopenia Markers */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Ruler className="w-4 h-4 text-amber-600" /> {t.bodyTitle}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.height}</label>
              <input
                type="number"
                value={heightCm}
                onChange={(e) => setHeightCm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.weight}</label>
              <input
                type="number"
                value={weightKg}
                onChange={(e) => setWeightKg(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Calculated BMI</label>
              <div className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold text-slate-800">
                {bmi} kg/m²
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.waist}</label>
              <input
                type="number"
                step="0.5"
                value={waistCm}
                onChange={(e) => setWaistCm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.hip}</label>
              <input
                type="number"
                step="0.5"
                value={hipCm}
                onChange={(e) => setHipCm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.muac}</label>
              <input
                type="number"
                step="0.1"
                value={muacCm}
                onChange={(e) => setMuacCm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
              <span className="text-[10px] text-slate-400">&lt;23 cm flags sarcopenia</span>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.chest}</label>
              <input
                type="number"
                step="0.5"
                value={chestCm}
                onChange={(e) => setChestCm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        {/* Step 3: Physical Mobility & ADL Function */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" /> Physical Function & Mobility
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.walkingDiff}</label>
              <select
                value={walkingDiff}
                onChange={(e) => setWalkingDiff(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              >
                <option value={0}>{t.none}</option>
                <option value={1}>{t.some}</option>
                <option value={2}>{t.severe}</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.stairsDiff}</label>
              <select
                value={stairsDiff}
                onChange={(e) => setStairsDiff(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              >
                <option value={0}>{t.none}</option>
                <option value={1}>{t.some}</option>
                <option value={2}>{t.severe}</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.chairDiff}</label>
              <select
                value={chairDiff}
                onChange={(e) => setChairDiff(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              >
                <option value={0}>{t.none}</option>
                <option value={1}>{t.some}</option>
                <option value={2}>{t.severe}</option>
              </select>
            </div>
          </div>
        </div>

        {/* Step 4: Cognition & Memory Reserve */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-600" /> Cognitive Function & Memory
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.memoryScore}</label>
              <input
                type="number"
                min="0"
                max="10"
                step="0.5"
                value={memoryScore}
                onChange={(e) => setMemoryScore(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.recallScore}</label>
              <input
                type="number"
                min="0"
                max="10"
                step="0.5"
                value={recallScore}
                onChange={(e) => setRecallScore(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        {/* Step 5: Chronic Conditions */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Heart className="w-4 h-4 text-rose-600" /> Chronic Disease History
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-sm">
              <input
                type="checkbox"
                checked={hasDiabetes}
                onChange={(e) => setHasDiabetes(e.target.checked)}
                className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              {t.diabetes}
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm">
              <input
                type="checkbox"
                checked={hasHypertension}
                onChange={(e) => setHasHypertension(e.target.checked)}
                className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              {t.hypertension}
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm">
              <input
                type="checkbox"
                checked={hasStroke}
                onChange={(e) => setHasStroke(e.target.checked)}
                className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              {t.stroke}
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm">
              <input
                type="checkbox"
                checked={hasHeartDisease}
                onChange={(e) => setHasHeartDisease(e.target.checked)}
                className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              {t.heartDisease}
            </label>
          </div>
        </div>

        {/* Step 6: Polypharmacy Review */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Pill className="w-4 h-4 text-amber-600" /> {t.medicationReview}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.medCount}</label>
              <input
                type="number"
                min="0"
                max="30"
                value={medCount}
                onChange={(e) => setMedCount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
              {medCount >= 5 && (
                <p className="text-xs text-rose-600 mt-1 font-semibold flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" /> {t.polypharmacyWarning}
                </p>
              )}
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Medication Names (Comma Separated)</label>
              <input
                type="text"
                placeholder="e.g. Metformin, Amlodipine, Aspirin"
                value={medList}
                onChange={(e) => setMedList(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onBack}
            className="px-5 py-2.5 border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50 font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold shadow-md transition-all disabled:opacity-50"
          >
            {submitting ? 'Calculating ML Risk Models...' : t.saveAndAssess}
          </button>
        </div>
      </form>
    </div>
  );
};
