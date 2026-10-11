import React, { useEffect, useState } from 'react';
import { Search, UserPlus, ArrowRight, Shield } from 'lucide-react';
import { api } from '../lib/api';
import { Participant } from '../types';
import { translations } from '../lib/i18n';

interface ParticipantsProps {
  onSelectParticipant: (id: string) => void;
  lang: 'en' | 'hi';
}

export const ParticipantsView: React.FC<ParticipantsProps> = ({ onSelectParticipant, lang }) => {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newCode, setNewCode] = useState('');
  const [newAge, setNewAge] = useState(70);
  const [newGender, setNewGender] = useState('Female');
  const [newPhone, setNewPhone] = useState('');
  const [newCaregiver, setNewCaregiver] = useState('');

  const t = translations[lang];

  const loadList = () => {
    setLoading(true);
    api.getParticipants(search)
      .then(setParticipants)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadList();
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createParticipant({
        participant_code: newCode,
        age: Number(newAge),
        gender: newGender,
        contact_phone: newPhone || undefined,
        caregiver_name: newCaregiver || undefined,
      });
      setShowAddModal(false);
      setNewCode('');
      loadList();
    } catch (err: any) {
      alert(err.message || 'Error creating participant');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t.participants}</h1>
          <p className="text-sm text-slate-500">Longitudinal participant directory</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-medium text-sm transition-all"
        >
          <UserPlus className="w-4 h-4" /> {t.addParticipant}
        </button>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          placeholder="Search by participant code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500"
        />
      </div>

      {/* Participants Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading participants...</div>
        ) : participants.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-3">
            <p className="text-sm">No participants registered yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-slate-50/50 text-slate-500 text-xs border-b border-slate-100">
                  <th className="px-6 py-3 font-medium">{t.code}</th>
                  <th className="px-6 py-3 font-medium">{t.age}</th>
                  <th className="px-6 py-3 font-medium">{t.gender}</th>
                  <th className="px-6 py-3 font-medium">Caregiver</th>
                  <th className="px-6 py-3 font-medium">Registration</th>
                  <th className="px-6 py-3 font-medium text-right">{t.actions}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {participants.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 font-mono font-medium text-slate-900">{p.participant_code}</td>
                    <td className="px-6 py-4">{p.age} yrs</td>
                    <td className="px-6 py-4">{p.gender}</td>
                    <td className="px-6 py-4 text-slate-500">{p.caregiver_name || 'None listed'}</td>
                    <td className="px-6 py-4 text-xs text-slate-400">{new Date(p.created_at).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => onSelectParticipant(p.id)}
                        className="text-sky-600 hover:text-sky-700 font-medium inline-flex items-center gap-1 text-xs"
                      >
                        {t.viewProfile} <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-4">{t.addParticipant}</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.code}</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. HAALSI-IND-004"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.age}</label>
                  <input
                    type="number"
                    min="40"
                    max="115"
                    value={newAge}
                    onChange={(e) => setNewAge(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">{t.gender}</label>
                  <select
                    value={newGender}
                    onChange={(e) => setNewGender(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                  >
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Caregiver Name</label>
                <input
                  type="text"
                  placeholder="e.g. Rahul Sharma"
                  value={newCaregiver}
                  onChange={(e) => setNewCaregiver(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm"
                />
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-medium"
                >
                  Save Participant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
