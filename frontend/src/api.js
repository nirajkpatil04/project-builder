/**
 * Central API client for Project Builder.
 * Handles auth tokens, standard error handling, and API calls.
 */

const API_BASE = '/api';

export function getAuthToken() {
  return localStorage.getItem('pb_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('pb_token', token);
  } else {
    localStorage.removeItem('pb_token');
  }
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('pb_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  if (user) {
    localStorage.setItem('pb_user', JSON.stringify(user));
  } else {
    localStorage.removeItem('pb_user');
  }
}

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = data?.detail || `Request failed with status ${response.status}`;
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Auth
  register: (payload) => request('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  googleAuth: (payload) => request('/auth/google', { method: 'POST', body: JSON.stringify(payload) }),
  completeOnboarding: (payload) => request('/auth/onboarding', { method: 'POST', body: JSON.stringify(payload) }),
  getMe: () => request('/auth/me'),
  updateProfile: (payload) => request('/auth/profile', { method: 'PUT', body: JSON.stringify(payload) }),

  // Builder
  getOptions: () => request('/builder/options'),
  getSuggestions: (profile, limit = 3) =>
    request('/builder/suggest', { method: 'POST', body: JSON.stringify({ profile, limit }) }),
  generateBlueprint: (profile, idea_key, level, use_llm = true) =>
    request('/builder/generate', {
      method: 'POST',
      body: JSON.stringify({ profile, idea_key, level, use_llm }),
    }),

  // Projects
  getProjects: () => request('/projects'),
  getProject: (id) => request(`/projects/${id}`),
  saveProject: (blueprint, profile) =>
    request('/projects', { method: 'POST', body: JSON.stringify({ blueprint, profile }) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
  updateProgress: (id, completed) =>
    request(`/projects/${id}/progress`, { method: 'PUT', body: JSON.stringify({ completed }) }),
  submitReview: (id, decision, comment) =>
    request(`/projects/${id}/reviews`, { method: 'POST', body: JSON.stringify({ decision, comment }) }),

  // Export URLs
  getMarkdownExportUrl: (id) => `${API_BASE}/projects/${id}/export/markdown`,
  getHtmlExportUrl: (id) => `${API_BASE}/projects/${id}/export/html`,

  // Admin
  getUsers: () => request('/admin/users'),
  updateUserStatus: (id, role, is_active) =>
    request(`/admin/users/${id}`, { method: 'PUT', body: JSON.stringify({ role, is_active }) }),
  getStats: () => request('/admin/stats'),
  getAuditLogs: () => request('/admin/audit-logs'),
};
