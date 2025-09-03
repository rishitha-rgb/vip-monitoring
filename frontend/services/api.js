import axios from 'axios';

const api = axios.create({
  baseURL: '/api', // Proxy to backend during development
  timeout: 30000,
});

export default api;
