import type { Lead } from "../types/lead";

interface LeadTableProps {
  leads: Lead[];
}

export function LeadTable({ leads }: LeadTableProps) {
  if (!leads.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-slate-400">
        Nenhum lead encontrado.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-900 text-slate-300">
          <tr>
            <th className="px-4 py-3">Empresa</th>
            <th className="px-4 py-3">Contato</th>
            <th className="px-4 py-3">Cidade</th>
            <th className="px-4 py-3">E-mail</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id} className="border-t border-slate-800 text-slate-300">
              <td className="px-4 py-3">{lead.company || "-"}</td>
              <td className="px-4 py-3">{lead.name || "-"}</td>
              <td className="px-4 py-3">
                {lead.city} {lead.state && `- ${lead.state}`}
              </td>
              <td className="px-4 py-3">{lead.email || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
