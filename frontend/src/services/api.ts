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
