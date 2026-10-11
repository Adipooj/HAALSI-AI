import React, { useState } from 'react';
import { Activity, ShieldCheck } from 'lucide-react';
import { api } from '../lib/api';
import { translations } from '../lib/i18n';

interface LoginProps {
  onSuccess: (user: any) => void;
  lang: 'en' | 'hi';
}

export const LoginPage: React.FC<LoginProps> = ({ onSuccess, lang }) => {
  const [email, setEmail] = useState('doctor@haalsi.ai');
  const [password, setPassword] = useState('doctor123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const t = translations[lang];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login({ email, password });
      api.setToken(data.access_token);
      onSuccess(data);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-sky-50 text-sky-600 rounded-xl flex items-center justify-center mx-auto">
            <Activity className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{t.title}</h1>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
            Clinical Practitioner Portal
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Clinician Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold shadow-md transition-all disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : t.login}
          </button>
        </form>

        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-500 space-y-1">
          <p className="font-semibold text-slate-700">Preloaded Demo Credentials:</p>
          <p>Email: <span className="font-mono text-sky-700">doctor@haalsi.ai</span></p>
          <p>Password: <span className="font-mono text-sky-700">doctor123</span></p>
        </div>
      </div>
    </div>
  );
};
