import React from 'react';
import { Activity, ShieldCheck, TrendingDown, Users, Pill, Clock, ArrowRight, BookOpen } from 'lucide-react';
import { translations } from '../lib/i18n';

interface LandingProps {
  onGoToApp: () => void;
  lang: 'en' | 'hi';
}

export const LandingPage: React.FC<LandingProps> = ({ onGoToApp, lang }) => {
  const t = translations[lang];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-b from-sky-900 to-slate-900 text-white pt-20 pb-28 px-6 sm:px-12">
        <div className="max-w-6xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-semibold tracking-wide uppercase">
            <ShieldCheck className="w-4 h-4" /> Research-Grounded Clinical Decision Support
          </div>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight">
            HAALSI AI
          </h1>
          <p className="text-xl sm:text-2xl text-sky-200 max-w-3xl mx-auto font-light leading-relaxed">
            {t.tagline}
          </p>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            Moving geriatric healthcare from reactive crisis management to proactive intervention. Bringing predictive frailty vigilance to clinics, communities, and the last mile.
          </p>
          <div className="pt-6 flex flex-wrap justify-center gap-4">
            <button
              onClick={onGoToApp}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-medium shadow-lg shadow-sky-500/30 transition-all hover:-translate-y-0.5"
            >
              Launch Clinical Portal <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Core Capabilities */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16 space-y-2">
          <h2 className="text-3xl font-bold text-slate-900">Multi-Domain Longitudinal Analytics</h2>
          <p className="text-slate-500 max-w-2xl mx-auto text-sm">
            Trained on longitudinal multi-wave aging studies to capture subclinical decline across functional, cognitive, and metabolic domains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-sky-100 text-sky-600 flex items-center justify-center mb-4">
              <Activity className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">11-Domain Frailty Index</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Calculates a continuous deficit-accumulation score normalized via robust statistics to identify systemic physiological vulnerability before acute events occur.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4">
              <TrendingDown className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">Longitudinal Decline Prediction</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Calibrated gradient boosted classification predicting functional independence collapse over multi-year wave intervals.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center mb-4">
              <Clock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold mb-2">Estimated Independence Horizon</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Monte Carlo forward trajectory simulations projecting years remaining until physical dependence, giving families actionable lead-time for preventive care.
            </p>
          </div>
        </div>

        {/* Clinical Transparency & Safety Notice */}
        <div className="mt-16 bg-sky-50 border border-sky-200 rounded-xl p-6 text-sm text-sky-900 flex items-start gap-4">
          <BookOpen className="w-6 h-6 text-sky-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-semibold text-sky-950">Intended Clinical Evaluation Deployment</h4>
            <p className="text-sky-800 leading-relaxed">
              HAALSI AI is currently positioned for clinical evaluation, epidemiological research, and geriatric decision support. It empowers clinicians and authorized health workers with predictive vigilance and does not replace professional clinical diagnostic judgment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
