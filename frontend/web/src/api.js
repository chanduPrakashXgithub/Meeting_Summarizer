
import axios from 'axios';
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export const uploadFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return axios.post(`${API_BASE}/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

export const transcribeFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return axios.post(`${API_BASE}/transcribe`, form);
};

export const summarizeTranscript = (transcript) => {
  return axios.post(`${API_BASE}/summarize`, { transcript });
};

export const getMeetings = () => {
  return axios.get(`${API_BASE}/meetings`);
};
