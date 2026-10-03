import { useEffect, useState } from "react";
import { LeadCard } from "../components/LeadCard";
import { getLeads } from "../services/api";
import type { Lead } from "../types/lead";

export function Leads() {
  const [leads, setLeads] = useState<Lead[]>([]);

  useEffect(() => {
    getLeads().then(setLeads).catch(console.error);
  }, []);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h2 className="mb-6 text-3xl font-bold text-white">Leads salvos</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {leads.map((lead) => (
          <LeadCard key={lead.id} lead={lead} />
        ))}
      </div>
    </main>
  );
}
