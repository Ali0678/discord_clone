import axios from "axios";

// 1. Create a base Axios instance pointing to your FastAPI backend
export const api = axios.create({
  baseURL: "http://localhost:8000", 
  headers: {
    "Content-Type": "application/json",
  },
});

// 2. Add an interceptor to inject the JWT Bearer token[cite: 1]
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`; // Matches backend requirement[cite: 1]
  }
  return config;
});