import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const clientsAPI = {
  getAll: () => api.get('/clients'),
  getOne: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  reassign: (clientId, employeeId) => api.patch(`/clients/${clientId}/reassign?new_employee_id=${employeeId}`),
  getCredentials: (clientId) => api.get(`/clients/${clientId}/credentials`),
};

export const casesAPI = {
  getAll: () => api.get('/cases'),
  getOne: (id) => api.get(`/cases/${id}`),
  update: (id, data) => api.patch(`/cases/${id}`, data),
};

export const messagesAPI = {
  getByClient: (clientId) => api.get(`/messages/client/${clientId}`),
  send: (data) => api.post('/messages', data),
  getUnreadCount: () => api.get('/messages/unread'),
};

export const visitorsAPI = {
  getAll: () => api.get('/visitors'),
  create: (data) => api.post('/visitors', data),
  checkout: (id) => api.patch(`/visitors/${id}/checkout`),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
};

export const employeesAPI = {
  getAll: () => api.get('/employees'),
  toggleStatus: (id) => api.patch(`/employees/${id}/toggle-status`),
};

export const workflowsAPI = {
  getAll: () => api.get('/workflows'),
};

export const paymentsAPI = {
  declare: (data) => api.post('/payments/declare', data),
  getPending: () => api.get('/payments/pending'),
  getHistory: () => api.get('/payments/history'), // Manager/SuperAdmin
  getClientHistory: () => api.get('/payments/client-history'), // Client only
  confirm: (id, data) => api.patch(`/payments/${id}/confirm`, data),
};

export default api;
