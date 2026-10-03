import type { Lead } from "../types/lead";

interface LeadCardProps {
  lead: Lead;
}

export function LeadCard({ lead }: LeadCardProps) {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <h3 className="font-semibold text-white">{lead.company || lead.name}</h3>
      <p className="mt-1 text-sm text-slate-400">{lead.name}</p>
      <p className="mt-3 text-sm text-slate-300">
        {lead.city} {lead.state && `- ${lead.state}`}
      </p>
      {lead.email && <p className="mt-1 text-sm text-slate-400">{lead.email}</p>}
      {lead.phone && <p className="mt-1 text-sm text-slate-400">{lead.phone}</p>}
    </article>
  );
}
