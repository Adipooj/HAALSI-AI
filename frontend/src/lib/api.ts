const API_BASE = (import.meta as any).env?.VITE_API_URL || '/api/v1';

export const api = {
  getToken: () => localStorage.getItem('haalsi_token'),
  setToken: (token: string) => localStorage.setItem('haalsi_token', token),
  clearToken: () => localStorage.removeItem('haalsi_token'),

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.clearToken();
      window.location.reload();
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(err.detail || 'Request failed');
    }

    return response.json();
  },

  login: (credentials: { email: string; password: string }) =>
    api.request<{ access_token: string; full_name: string; role: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  getMetrics: () => api.request<any>('/dashboard/metrics'),
  getParticipants: (search?: string) => api.request<any[]>(`/participants/${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  createParticipant: (data: any) => api.request<any>('/participants/', { method: 'POST', body: JSON.stringify(data) }),
  getParticipant: (id: string) => api.request<any>(`/participants/${id}`),
  getParticipantAssessments: (id: string) => api.request<any[]>(`/participants/${id}/assessments`),
  createAssessment: (data: any) => api.request<any>('/assessments/', { method: 'POST', body: JSON.stringify(data) }),
  getAssessment: (id: string) => api.request<any>(`/assessments/${id}`),
};
