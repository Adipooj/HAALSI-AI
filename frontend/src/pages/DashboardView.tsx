import React, { useEffect, useState } from 'react';
import { Users, Activity, AlertTriangle, Pill, Clock, ArrowUpRight, TrendingUp } from 'lucide-react';
import { api } from '../lib/api';
import { DashboardMetrics } from '../types';
import { translations } from '../lib/i18n';

interface DashboardProps {
  onSelectParticipant: (id: string) => void;
  onNewAssessment: () => void;
  lang: 'en' | 'hi';
}

export const DashboardView: React.FC<DashboardProps> = ({ onSelectParticipant, onNewAssessment, lang }) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const t = translations[lang];

  useEffect(() => {
    api.getMetrics()
      .then(setMetrics)
      .catch((err) => console.error("Error loading dashboard metrics:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="p-8 text-center text-slate-500">
        Unable to load dashboard metrics. Check server connection.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t.dashboard}</h1>
          <p className="text-sm text-slate-500">Real-time longitudinal cohort health monitoring</p>
        </div>
        <button
          onClick={onNewAssessment}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-medium text-sm shadow-sm transition-all"
        >
          <Activity className="w-4 h-4" /> {t.newAssessment}
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.totalParticipants}</span>
            <Users className="w-4 h-4 text-sky-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{metrics.total_participants}</div>
          <div className="text-xs text-slate-400 mt-1">Active registered cohort</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.highRiskCases}</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-600 mt-2">{metrics.high_risk_count}</div>
          <div className="text-xs text-rose-400 mt-1">Requires clinical intervention</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.polypharmacyAlerts}</span>
            <Pill className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-600 mt-2">{metrics.polypharmacy_alert_count}</div>
          <div className="text-xs text-amber-500 mt-1">≥5 concurrent medications</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500 uppercase">{t.avgFrailty}</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{metrics.average_frailty_index}</div>
          <div className="text-xs text-slate-400 mt-1">Cohort deficit-index mean</div>
        </div>
      </div>

      {/* Recent Longitudinal Assessments Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">{t.recentActivity}</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50/50 text-slate-500 text-xs border-b border-slate-100">
                <th className="px-6 py-3 font-medium">{t.date}</th>
                <th className="px-6 py-3 font-medium">{t.riskTier}</th>
                <th className="px-6 py-3 font-medium">{t.frailtyIndex}</th>
                <th className="px-6 py-3 font-medium">{t.trajectoryCategory}</th>
                <th className="px-6 py-3 font-medium">{t.estYears}</th>
                <th className="px-6 py-3 font-medium text-right">{t.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {metrics.recent_assessments.map((a) => (
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
                  <td className="px-6 py-4 font-mono font-medium">{a.frailty_index.toFixed(2)}</td>
                  <td className="px-6 py-4">{a.trajectory_category}</td>
                  <td className="px-6 py-4 font-semibold text-slate-900">
                    {a.estimated_years_to_independence_loss ? `${a.estimated_years_to_independence_loss} yrs` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => onSelectParticipant(a.participant_id)}
                      className="text-sky-600 hover:text-sky-700 font-medium inline-flex items-center gap-1 text-xs"
                    >
                      {t.viewProfile} <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
