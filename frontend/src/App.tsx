import React, { useState } from 'react';
import { Activity, LayoutDashboard, Users, Globe, LogOut, FileText, ChevronRight } from 'lucide-react';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardView } from './pages/DashboardView';
import { ParticipantsView } from './pages/ParticipantsView';
import { ParticipantProfileView } from './pages/ParticipantProfileView';
import { AssessmentFormView } from './pages/AssessmentFormView';
import { api } from './lib/api';
import { translations } from './lib/i18n';

export const App: React.FC = () => {
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [token, setToken] = useState<string | null>(api.getToken());
  const [currentView, setCurrentView] = useState<'landing' | 'login' | 'dashboard' | 'participants' | 'profile' | 'new-assessment'>('landing');
  const [selectedParticipantId, setSelectedParticipantId] = useState<string | null>(null);
  const [selectedParticipant, setSelectedParticipant] = useState<any | null>(null);

  const t = translations[lang];

  const handleLogout = () => {
    api.clearToken();
    setToken(null);
    setCurrentView('landing');
  };

  const handleOpenParticipant = (id: string) => {
    setSelectedParticipantId(id);
    setCurrentView('profile');
  };

  const handleStartAssessment = async (participantId?: string) => {
    if (participantId) {
      const p = await api.getParticipant(participantId);
      setSelectedParticipant(p);
      setCurrentView('new-assessment');
    } else {
      // Pick first participant or go to participants list
      const parts = await api.getParticipants();
      if (parts.length > 0) {
        setSelectedParticipant(parts[0]);
        setCurrentView('new-assessment');
      } else {
        setCurrentView('participants');
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setCurrentView('landing')}
              className="flex items-center gap-2.5 font-bold text-lg text-slate-900"
            >
              <div className="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center">
                <Activity className="w-5 h-5" />
              </div>
              <span>HAALSI AI</span>
            </button>

            {token && (
              <nav className="hidden md:flex items-center gap-1">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    currentView === 'dashboard' ? 'bg-sky-50 text-sky-700' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {t.dashboard}
                </button>
                <button
                  onClick={() => setCurrentView('participants')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    currentView === 'participants' ? 'bg-sky-50 text-sky-700' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {t.participants}
                </button>
              </nav>
            )}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            {/* Language Switcher */}
            <button
              onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
              className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
            >
              <Globe className="w-3.5 h-3.5" />
              <span>{lang === 'en' ? 'हिन्दी' : 'EN'}</span>
            </button>

            {token ? (
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-rose-600 hover:bg-rose-50"
              >
                <LogOut className="w-3.5 h-3.5" /> <span className="hidden sm:inline">{t.logout}</span>
              </button>
            ) : (
              <button
                onClick={() => setCurrentView('login')}
                className="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-sm"
              >
                {t.login}
              </button>
            )}
          </div>
        </div>

        {/* Mobile Subnav when authenticated */}
        {token && (
          <div className="flex md:hidden border-t border-slate-100 px-4 py-2 bg-slate-50/80 justify-around text-xs font-semibold">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`py-1 px-3 rounded-md ${currentView === 'dashboard' ? 'bg-sky-600 text-white' : 'text-slate-600'}`}
            >
              {t.dashboard}
            </button>
            <button
              onClick={() => setCurrentView('participants')}
              className={`py-1 px-3 rounded-md ${currentView === 'participants' ? 'bg-sky-600 text-white' : 'text-slate-600'}`}
            >
              {t.participants}
            </button>
          </div>
        )}
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'landing' && (
          <LandingPage onGoToApp={() => (token ? setCurrentView('dashboard') : setCurrentView('login'))} lang={lang} />
        )}

        {currentView === 'login' && (
          <LoginPage
            onSuccess={() => {
              setToken(api.getToken());
              setCurrentView('dashboard');
            }}
            lang={lang}
          />
        )}

        {currentView === 'dashboard' && (
          <DashboardView
            onSelectParticipant={handleOpenParticipant}
            onNewAssessment={() => handleStartAssessment()}
            lang={lang}
          />
        )}

        {currentView === 'participants' && (
          <ParticipantsView
            onSelectParticipant={handleOpenParticipant}
            lang={lang}
          />
        )}

        {currentView === 'profile' && selectedParticipantId && (
          <ParticipantProfileView
            participantId={selectedParticipantId}
            onBack={() => setCurrentView('participants')}
            onNewAssessment={(id) => handleStartAssessment(id)}
            lang={lang}
          />
        )}

        {currentView === 'new-assessment' && selectedParticipant && (
          <AssessmentFormView
            participant={selectedParticipant}
            onBack={() => setCurrentView('profile')}
            onComplete={(assessment) => {
              setSelectedParticipantId(assessment.participant_id);
              setCurrentView('profile');
            }}
            lang={lang}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        <p>HAALSI AI • Clinical Evaluation Platform • Longitudinal Geriatric Decision Support System</p>
      </footer>
    </div>
  );
};
