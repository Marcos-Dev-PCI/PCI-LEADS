import axios from "axios";
import type { Lead } from "../types/lead";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
});

export async function getLeads(): Promise<Lead[]> {
  const response = await api.get<Lead[]>("/leads/");
  return response.data;
}

export async function searchLeads(query: string, city: string) {
  const response = await api.post<{ results: Lead[] }>("/leads/search/", {
    query,
    city,
  });
  return response.data;
}

// Interceptor de requisição:  o Token automaticamente antes do pedido sair
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pcleads_token');
  if (token && config.headers) {
    // IMPORTANTE: O DRF usa o prefixo 'Token ' por padrão
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor de resposta: Intercepta o erro 401 que vem do Django
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Se o backend retornar 401, limpa os dados locais e joga para a rota de login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('pcleads_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


