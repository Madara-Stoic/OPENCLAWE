import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth
export const login = async (email, name, role) => {
  const response = await api.post('/auth/login', { email, name, role });
  return response.data;
};

// Patients
export const getPatients = async () => {
  const response = await api.get('/patients');
  return response.data;
};

export const getPatient = async (patientId) => {
  const response = await api.get(`/patients/${patientId}`);
  return response.data;
};

export const getPatientReadings = async (patientId, limit = 50) => {
  const response = await api.get(`/patients/${patientId}/readings?limit=${limit}`);
  return response.data;
};

export const getPatientAlerts = async (patientId, limit = 20) => {
  const response = await api.get(`/patients/${patientId}/alerts?limit=${limit}`);
  return response.data;
};

// Doctors
export const getDoctors = async () => {
  const response = await api.get('/doctors');
  return response.data;
};

export const getDoctor = async (doctorId) => {
  const response = await api.get(`/doctors/${doctorId}`);
  return response.data;
};

export const getDoctorPatients = async (doctorId) => {
  const response = await api.get(`/doctors/${doctorId}/patients`);
  return response.data;
};

// Hospitals
export const getHospitals = async () => {
  const response = await api.get('/hospitals');
  return response.data;
};

export const getHospital = async (hospitalId) => {
  const response = await api.get(`/hospitals/${hospitalId}`);
  return response.data;
};

export const getHospitalStats = async (hospitalId) => {
  const response = await api.get(`/hospitals/${hospitalId}/stats`);
  return response.data;
};

// Telemetry
export const getLiveTelemetry = async () => {
  const response = await api.get('/telemetry/live');
  return response.data;
};

export const recordReading = async (patientId) => {
  const response = await api.post(`/telemetry/reading?patient_id=${patientId}`);
  return response.data;
};

// Alerts
export const getAllAlerts = async (limit = 50) => {
  const response = await api.get(`/alerts?limit=${limit}`);
  return response.data;
};

export const getRecentAlerts = async () => {
  const response = await api.get('/alerts/recent');
  return response.data;
};

// Diet
export const generateDietPlan = async (patientId) => {
  const response = await api.post(`/diet/generate?patient_id=${patientId}`);
  return response.data;
};

export const getPatientDietPlans = async (patientId) => {
  const response = await api.get(`/diet/${patientId}`);
  return response.data;
};

// Moltbot
export const getMoltbotActivities = async (limit = 50) => {
  const response = await api.get(`/moltbot/activities?limit=${limit}`);
  return response.data;
};

export const getMoltbotStats = async () => {
  const response = await api.get('/moltbot/stats');
  return response.data;
};

// Dashboards
export const getPatientDashboard = async (patientId) => {
  const response = await api.get(`/dashboard/patient/${patientId}`);
  return response.data;
};

export const getDoctorDashboard = async (doctorId) => {
  const response = await api.get(`/dashboard/doctor/${doctorId}`);
  return response.data;
};

export const getOrganizationDashboard = async () => {
  const response = await api.get('/dashboard/organization');
  return response.data;
};

// Blockchain
export const verifyTransaction = async (txHash) => {
  const response = await api.get(`/blockchain/verify/${txHash}`);
  return response.data;
};

export default api;
