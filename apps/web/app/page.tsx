"use client";

import { FormEvent, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://buildcost-pro-production.up.railway.app";

type Project = { id: string; code: string; name: string; status: string; description?: string | null };
type Summary = { budget_total: string; cost_total: string; income_total: string; expense_total: string; balance: string; budget_remaining: string };

async function api(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("buildcost_access") : null;
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError("");
    try {
      const response = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      localStorage.setItem("buildcost_access", response.access_token);
      localStorage.setItem("buildcost_refresh", response.refresh_token);
      onLogin();
    } catch (e) { setError(e instanceof Error ? e.message : "Login failed"); }
  };
  return <main className="page"><div className="shell"><section className="card form">
    <div className="brand">BuildCost Pro</div><p className="muted">Project cost management platform</p>
    <form onSubmit={submit}>
      <label className="field"><span>Email</span><input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></label>
      <label className="field"><span>Password</span><input type="password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
      {error && <div className="error">{error}</div>}
      <button className="primary">Sign in</button>
    </form>
  </section></div></main>;
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const load = async () => {
    try { const rows = await api("/api/v1/projects"); setProjects(rows); if (rows[0]) await select(rows[0]); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to load projects"); }
  };
  const select = async (project: Project) => { setSelected(project); setSummary(await api(`/api/v1/projects/${project.id}/summary`)); };
  useEffect(() => { void load(); }, []);
  const money = (value?: string) => value == null ? "—" : Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return <main className="page"><div className="shell">
    <header className="header"><div><div className="brand">BuildCost Pro</div><div className="muted">Core business dashboard</div></div><button className="secondary" onClick={onLogout}>Sign out</button></header>
    {error && <div className="card error">{error}</div>}
    <section className="stats">
      <div className="card"><div className="muted">Budget</div><div className="stat-value">{money(summary?.budget_total)}</div></div>
      <div className="card"><div className="muted">Costs</div><div className="stat-value">{money(summary?.cost_total)}</div></div>
      <div className="card"><div className="muted">Income</div><div className="stat-value">{money(summary?.income_total)}</div></div>
      <div className="card"><div className="muted">Balance</div><div className="stat-value">{money(summary?.balance)}</div></div>
    </section>
    <div className="grid">
      <section className="card"><h2>Projects</h2><div className="list">{projects.length === 0 ? <div className="muted">No projects yet.</div> : projects.map(project => <button key={project.id} className="row" onClick={() => void select(project)}><span><strong>{project.name}</strong><br /><small className="muted">{project.code}</small></span><span className="muted">{project.status}</span></button>)}</div></section>
      <section className="card"><h2>Selected project</h2>{selected ? <><h3>{selected.name}</h3><p className="muted">{selected.description || "No description"}</p><div className="row"><span>Budget remaining</span><strong>{money(summary?.budget_remaining)}</strong></div><div className="row"><span>Expenses</span><strong>{money(summary?.expense_total)}</strong></div></> : <p className="muted">Select a project to view financials.</p>}</section>
    </div>
  </div></main>;
}

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  useEffect(() => setAuthenticated(Boolean(localStorage.getItem("buildcost_access"))), []);
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;
  return <Dashboard onLogout={() => { localStorage.removeItem("buildcost_access"); localStorage.removeItem("buildcost_refresh"); setAuthenticated(false); }} />;
}
