import { useState } from "react";
import { SearchForm } from "../components/SearchForm";
import { LeadTable } from "../components/LeadTable";
import { searchLeads } from "../services/api";
import type { Lead } from "../types/lead";

export function Home() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch(query: string, city: string) {
    setLoading(true);
    try {
      const data = await searchLeads(query, city);
      setLeads(data.results ?? []);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-10">
        <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-amber-500">
          Prospecção
        </p>
        <h2 className="text-4xl font-bold text-white">Encontre novos leads.</h2>
        <p className="mt-3 max-w-2xl text-slate-400">
          Busque empresas por segmento e localização.
        </p>
      </div>

      <SearchForm onSearch={handleSearch} />

      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-white">Resultados</h3>
          {loading && <span className="text-sm text-slate-400">Buscando...</span>}
        </div>
        <LeadTable leads={leads} />
      </section>
    </main>
  );
}
