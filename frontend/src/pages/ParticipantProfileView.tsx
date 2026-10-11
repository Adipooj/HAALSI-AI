import React, { useEffect, useState } from 'react';
import { ArrowLeft, PlusCircle, Activity, AlertTriangle, Pill, Clock, CheckCircle2 } from 'lucide-react';
import { api } from '../lib/api';
import { Participant, Assessment } from '../types';
import { translations } from '../lib/i18n';

interface ProfileProps {
  participantId: string;
  onBack: () => void;
  onNewAssessment: (participantId: string) => void;
  lang: 'en' | 'hi';
}

export const ParticipantProfileView: React.FC<ProfileProps> = ({ participantId, onBack, onNewAssessment, lang }) => {
  const [participant, setParticipant] = useState<Participant | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const t = translations[lang];

  useEffect(() => {
    Promise.all([
      api.getParticipant(participantId),
      api.getParticipantAssessments(participantId)
    ])
      .then(([p, a]) => {
        setParticipant(p);
        setAssessments(a);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [participantId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  if (!participant) {
    return <div className="p-8 text-center text-slate-500">Participant not found.</div>;
  }

  const latest = assessments[0];

  return (
    <div className="space-y-8">
      {/* Back button & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">{participant.participant_code}</h1>
              {participant.is_demo && (
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-600">
                  Demo
                </span>
              )}
            </div>
            <p className="text-sm text-slate-500">
              {participant.gender}, {participant.age} years old • Caregiver: {participant.caregiver_name || 'None'}
            </p>
          </div>
        </div>
        <button
          onClick={() => onNewAssessment(participant.id)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-medium text-sm transition-all"
        >
          <PlusCircle className="w-4 h-4" /> Add Assessment
        </button>
      </div>

      {/* Latest Assessment Highlights */}
      {latest ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.riskTier}</span>
            <div className="mt-2">
              <span className={`inline-flex items-center px-2.5 py-1 rounded text-sm font-bold ${
                latest.risk_tier === 'High' ? 'bg-rose-100 text-rose-700' :
                latest.risk_tier === 'Moderate' ? 'bg-amber-100 text-amber-700' :
                'bg-emerald-100 text-emerald-700'
              }`}>
                {latest.risk_tier} Risk
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-2">Overall Score: {(latest.overall_risk_score * 100).toFixed(1)}%</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.frailtyIndex}</span>
            <div className="text-2xl font-bold font-mono text-slate-900 mt-2">
              {latest.frailty_index.toFixed(2)}
            </div>
            <div className="text-xs text-slate-400 mt-2">11-Domain Deficit Score</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.estYears}</span>
            <div className="text-2xl font-bold text-sky-600 mt-2">
              {latest.estimated_years_to_independence_loss} yrs
            </div>
            <div className="text-xs text-slate-400 mt-2">Estimated Functional Independence</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.medicationReview}</span>
            <div className="text-2xl font-bold text-slate-900 mt-2">
              {latest.medications_count} Meds
            </div>
            <div className="text-xs mt-2">
              {latest.is_polypharmacy ? (
                <span className="text-rose-600 font-semibold flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> Polypharmacy Alert
                </span>
              ) : (
                <span className="text-emerald-600 font-medium">Standard Regimen</span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500">
          No clinical assessments recorded for this participant. Click "Add Assessment" to calculate risk.
        </div>
      )}

      {/* Recommendations & SHAP Explainability Breakdown */}
      {latest && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recommendations */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> {t.recommendations}
            </h3>
            <div className="space-y-2 text-sm text-slate-700">
              {latest.clinical_recommendations?.map((rec, idx) => (
                <div key={idx} className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                  {rec}
                </div>
              ))}
            </div>
          </div>

          {/* Model Risk Drivers (SHAP Attribution) */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-600" /> {t.shapDrivers}
            </h3>
            <div className="space-y-3">
              {latest.shap_contributions && Object.entries(latest.shap_contributions).map(([feature, val]) => (
                <div key={feature} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-700">{feature}</span>
                    <span className="font-mono text-slate-500">+{(val * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-sky-500 h-2 rounded-full"
                      style={{ width: `${Math.min(100, Math.max(5, val * 200))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Historical Longitudinal Assessments */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="text-base font-semibold text-slate-900">Longitudinal Assessment History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="bg-slate-50/50 text-slate-500 text-xs border-b border-slate-100">
                <th className="px-6 py-3 font-medium">Assessment Date</th>
                <th className="px-6 py-3 font-medium">Risk Tier</th>
                <th className="px-6 py-3 font-medium">Frailty Index</th>
                <th className="px-6 py-3 font-medium">BMI</th>
                <th className="px-6 py-3 font-medium">Trajectory</th>
                <th className="px-6 py-3 font-medium">Model Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {assessments.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4">{new Date(a.assessment_date).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                      a.risk_tier === 'High' ? 'bg-rose-100 text-rose-700' :
                      a.risk_tier === 'Moderate' ? 'bg-amber-100 text-amber-700' :
                      'bg-emerald-100 text-emerald-700'
                    }`}>
                      {a.risk_tier}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono">{a.frailty_index.toFixed(2)}</td>
                  <td className="px-6 py-4">{a.bmi ? a.bmi.toFixed(1) : 'N/A'}</td>
                  <td className="px-6 py-4">{a.trajectory_category}</td>
                  <td className="px-6 py-4 text-xs font-mono text-slate-400">{a.model_version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
