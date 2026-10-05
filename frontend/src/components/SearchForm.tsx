import { useState } from "react";
import type { FormEvent } from "react";


interface SearchFormProps {
  onSearch: (query: string, city: string) => void;
}

export function SearchForm({ onSearch }: SearchFormProps) {
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSearch(query, city);
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-3">
      <input
        className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-amber-500"
        placeholder="Ex.: academias"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />

      <input
        className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-amber-500"
        placeholder="Ex.: Brasília"
        value={city}
        onChange={(event) => setCity(event.target.value)}
      />

      <button
        type="submit"
        className="rounded-lg bg-amber-500 px-5 py-3 font-semibold text-slate-950 hover:bg-amber-400"
      >
        Buscar leads
      </button>
    </form>
  );
}
