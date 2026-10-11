import React, { useEffect, useState } from 'react';
import { ArrowLeft, PlusCircle, Activity, AlertTriangle, Pill, Clock, CheckCircle2, TrendingDown, Gauge, Heart, Ruler, Calendar } from 'lucide-react';
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
  // Sort assessments ascending chronologically for chart display
  const chronological = [...assessments].sort(
    (a, b) => new Date(a.assessment_date).getTime() - new Date(b.assessment_date).getTime()
  );

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
          <PlusCircle className="w-4 h-4" /> {t.newAssessment}
        </button>
      </div>

      {/* Latest Assessment Highlights */}
      {latest ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
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

      {/* LONGITUDINAL MULTI-TIMEPOINT DECLINE CHART (Over Weeks/Months) */}
      {chronological.length > 1 && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-rose-500" /> {t.declineTrends}
              </h2>
              <p className="text-xs text-slate-500">
                Tracking decline across {chronological.length} longitudinal timepoints over weeks and months
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
              <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-rose-500 inline-block"></span> Overall Risk %</span>
              <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-sky-500 inline-block"></span> Frailty Index</span>
              <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-purple-500 inline-block"></span> Systolic BP</span>
            </div>
          </div>

          {/* SVG Longitudinal Decline Trajectory Line & Bar Chart */}
          <div className="w-full overflow-x-auto">
            <div className="min-w-[600px] h-64 relative flex items-end justify-between px-6 pb-8 pt-6 border-b border-l border-slate-200">
              {chronological.map((item, idx) => {
                const riskPct = Math.round(item.overall_risk_score * 100);
                const frailtyPct = Math.round(item.frailty_index * 100);
                const bpHeight = Math.min(100, Math.max(10, ((item.systolic_bp || 120) - 80) * 1.0));

                return (
                  <div key={item.id} className="flex-1 flex flex-col items-center justify-end h-full px-2 group">
                    {/* Tooltip on Hover */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[11px] p-2 rounded shadow-lg absolute -top-2 pointer-events-none z-10 space-y-0.5">
                      <p className="font-bold">{new Date(item.assessment_date).toLocaleDateString()}</p>
                      <p>Risk: {riskPct}% ({item.risk_tier})</p>
                      <p>Frailty: {item.frailty_index.toFixed(2)}</p>
                      {item.systolic_bp && <p>BP: {item.systolic_bp}/{item.diastolic_bp} mmHg</p>}
                      {item.pulse_bpm && <p>Pulse: {item.pulse_bpm} bpm</p>}
                      {item.mid_upper_arm_circ_cm && <p>Bicep (MUAC): {item.mid_upper_arm_circ_cm} cm</p>}
                    </div>

                    {/* Multi-Bar Representation for the Timepoint */}
                    <div className="w-full max-w-[64px] flex items-end justify-center gap-1.5 h-full">
                      {/* Risk Bar */}
                      <div
                        className={`w-4 rounded-t transition-all ${
                          item.risk_tier === 'High' ? 'bg-rose-500' :
                          item.risk_tier === 'Moderate' ? 'bg-amber-400' : 'bg-emerald-400'
                        }`}
                        style={{ height: `${Math.max(12, riskPct)}%` }}
                        title={`Overall Risk: ${riskPct}%`}
                      >
                        <span className="text-[10px] font-bold text-white block text-center pt-0.5">
                          {riskPct}%
                        </span>
                      </div>

                      {/* Frailty Bar */}
                      <div
                        className="w-4 bg-sky-500 rounded-t transition-all"
                        style={{ height: `${Math.max(10, frailtyPct)}%` }}
                        title={`Frailty: ${(item.frailty_index).toFixed(2)}`}
                      >
                        <span className="text-[9px] font-bold text-white block text-center pt-0.5">
                          {(item.frailty_index).toFixed(2)}
                        </span>
                      </div>

                      {/* BP Bar */}
                      {item.systolic_bp && (
                        <div
                          className="w-3 bg-purple-400 rounded-t transition-all"
                          style={{ height: `${bpHeight}%` }}
                          title={`BP: ${item.systolic_bp} mmHg`}
                        />
                      )}
                    </div>

                    {/* Date label at bottom */}
                    <div className="text-center mt-3 text-xs text-slate-600 font-medium">
                      <Calendar className="w-3 h-3 inline mr-1 text-slate-400" />
                      {new Date(item.assessment_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 px-2">
            <span>← Earlier Observations (Baseline)</span>
            <span className="font-semibold text-rose-600">Trajectory: {latest.trajectory_category} →</span>
          </div>
        </div>
      )}

      {/* Latest Vitals & Body Anthropometric Highlights (Nursing Home Metrics) */}
      {latest && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Gauge className="w-4 h-4 text-sky-600" /> Nursing Home Vitals & Body Measurements (Latest Visit)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 text-center">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">BP</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.systolic_bp ? `${latest.systolic_bp}/${latest.diastolic_bp}` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">mmHg</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Pulse</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.pulse_bpm ? `${latest.pulse_bpm}` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">bpm</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">SpO2</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.spo2_pct ? `${latest.spo2_pct}%` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">oxygen</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Temp</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.temperature_c ? `${latest.temperature_c}°C` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">body temp</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Bicep / MUAC</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.mid_upper_arm_circ_cm ? `${latest.mid_upper_arm_circ_cm} cm` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">arm muscle</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Waist</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.waist_cm ? `${latest.waist_cm} cm` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">abdominal</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Hip</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.hip_cm ? `${latest.hip_cm} cm` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">pelvic</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Chest</span>
              <span className="text-sm font-bold text-slate-900 font-mono">
                {latest.chest_cm ? `${latest.chest_cm} cm` : 'N/A'}
              </span>
              <span className="text-[9px] text-slate-400 block">thoracic</span>
            </div>
          </div>
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

      {/* Historical Longitudinal Assessments Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="text-base font-semibold text-slate-900">Longitudinal Assessment History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="bg-slate-50/50 text-slate-500 text-xs border-b border-slate-100">
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Risk Tier</th>
                <th className="px-4 py-3 font-medium">Frailty</th>
                <th className="px-4 py-3 font-medium">BP (mmHg)</th>
                <th className="px-4 py-3 font-medium">Pulse</th>
                <th className="px-4 py-3 font-medium">SpO2</th>
                <th className="px-4 py-3 font-medium">Bicep / MUAC</th>
                <th className="px-4 py-3 font-medium">Waist</th>
                <th className="px-4 py-3 font-medium">Trajectory</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 text-xs">
              {assessments.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">{new Date(a.assessment_date).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded font-semibold ${
                      a.risk_tier === 'High' ? 'bg-rose-100 text-rose-700' :
                      a.risk_tier === 'Moderate' ? 'bg-amber-100 text-amber-700' :
                      'bg-emerald-100 text-emerald-700'
                    }`}>
                      {a.risk_tier}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono font-medium">{a.frailty_index.toFixed(2)}</td>
                  <td className="px-4 py-3 font-mono">{a.systolic_bp ? `${a.systolic_bp}/${a.diastolic_bp}` : '-'}</td>
                  <td className="px-4 py-3 font-mono">{a.pulse_bpm || '-'}</td>
                  <td className="px-4 py-3 font-mono">{a.spo2_pct ? `${a.spo2_pct}%` : '-'}</td>
                  <td className="px-4 py-3 font-mono">{a.mid_upper_arm_circ_cm ? `${a.mid_upper_arm_circ_cm} cm` : '-'}</td>
                  <td className="px-4 py-3 font-mono">{a.waist_cm ? `${a.waist_cm} cm` : '-'}</td>
                  <td className="px-4 py-3">{a.trajectory_category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
