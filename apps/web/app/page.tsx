"use client";

import { FormEvent, useEffect, useState } from "react";

const WEB_ORIGIN = "https://buildcost-pro-production.up.railway.app";
const DEFAULT_API_BASE = "https://reasonable-determination-production-52dc.up.railway.app";
const configuredApiBase = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
// Never send API calls back to the web service itself. This prevents a production
// env mismatch from turning valid API routes such as /auth/login into web 404s.
const API = configuredApiBase && configuredApiBase !== WEB_ORIGIN ? configuredApiBase : DEFAULT_API_BASE;
type Project = { id: string; code: string; name: string; status: string; description?: string | null };
type Summary = { budget_total: string; cost_total: string; income_total: string; expense_total: string; balance: string; budget_remaining: string };

async function api(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("buildcost_access") : null;
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem("buildcost_access");
    localStorage.removeItem("buildcost_refresh");
  }
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      const response = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      localStorage.setItem("buildcost_access", response.access_token);
      localStorage.setItem("buildcost_refresh", response.refresh_token);
      onLogin();
    } catch (e) { setError(e instanceof Error ? e.message : "Login failed"); }
    finally { setBusy(false); }
  };
  return <main className="page"><div className="shell"><section className="card form"><div className="brand">BuildCost Pro</div><p className="muted">V1.1 core application</p><form onSubmit={submit}><label className="field"><span>Email</span><input type="email" value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" required /></label><label className="field"><span>Password</span><input type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" required /></label>{error && <div className="error">{error}</div>}<button className="primary" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button></form></section></div></main>;
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selected, setSelected] = useState<Project | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState("");
  const [projectForm, setProjectForm] = useState({ code: "", name: "" });
  const [budgetForm, setBudgetForm] = useState({ name: "", amount: "" });
  const [costForm, setCostForm] = useState({ category: "", quantity: "", unit_cost: "" });
  const [txForm, setTxForm] = useState({ type: "EXPENSE", amount: "", description: "" });

  const load = async (preferred?: Project) => {
    try {
      setLoading(true); setError("");
      const rows = await api("/api/v1/projects");
      setProjects(rows);
      const next = preferred ?? rows.find((p: Project) => p.id === selected?.id) ?? rows[0];
      if (next) await select(next);
      else { setSelected(null); setSummary(null); }
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to load projects"); }
    finally { setLoading(false); }
  };
  const select = async (project: Project) => {
    try { setSelected(project); setSummary(await api(`/api/v1/projects/${project.id}/summary`)); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to load project summary"); }
  };
  useEffect(() => { void load(); }, []);

  const submit = async (event: FormEvent, key: string, action: () => Promise<void>) => {
    event.preventDefault(); setSaving(key); setError("");
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "Operation failed"); }
    finally { setSaving(""); }
  };
  const submitProject = (event: FormEvent) => submit(event, "project", async () => {
    const project = await api("/api/v1/projects", { method: "POST", body: JSON.stringify(projectForm) });
    setProjectForm({ code: "", name: "" }); await load(project);
  });
  const submitBudget = (event: FormEvent) => submit(event, "budget", async () => {
    if (!selected) return;
    await api(`/api/v1/projects/${selected.id}/budgets`, { method: "POST", body: JSON.stringify({ name: budgetForm.name, amount: budgetForm.amount }) });
    setBudgetForm({ name: "", amount: "" }); await select(selected);
  });
  const submitCost = (event: FormEvent) => submit(event, "cost", async () => {
    if (!selected) return;
    await api(`/api/v1/projects/${selected.id}/costs`, { method: "POST", body: JSON.stringify({ category: costForm.category, quantity: costForm.quantity, unit_cost: costForm.unit_cost }) });
    setCostForm({ category: "", quantity: "", unit_cost: "" }); await select(selected);
  });
  const submitTransaction = (event: FormEvent) => submit(event, "transaction", async () => {
    if (!selected) return;
    await api(`/api/v1/projects/${selected.id}/transactions`, { method: "POST", body: JSON.stringify(txForm) });
    setTxForm({ type: "EXPENSE", amount: "", description: "" }); await select(selected);
  });
  const money = (value?: string) => value == null ? "—" : Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const button = (key: string, label: string) => saving === key ? `${label}…` : label;

  return <main className="page"><div className="shell"><header className="header"><div><div className="brand">BuildCost Pro</div><div className="muted">Core business dashboard · V1.1</div></div><div className="actions"><button className="secondary" onClick={() => void load()}>Refresh</button><button className="secondary" onClick={onLogout}>Sign out</button></div></header>
    {error && <div className="card error">{error}<button className="secondary" onClick={() => setError("")}>Dismiss</button></div>}
    <section className="stats"><div className="card"><div className="muted">Budget</div><div className="stat-value">{money(summary?.budget_total)}</div></div><div className="card"><div className="muted">Costs</div><div className="stat-value">{money(summary?.cost_total)}</div></div><div className="card"><div className="muted">Income</div><div className="stat-value">{money(summary?.income_total)}</div></div><div className="card"><div className="muted">Balance</div><div className="stat-value">{money(summary?.balance)}</div></div></section>
    <div className="grid"><section className="card"><h2>Projects</h2><form onSubmit={submitProject}><div className="field"><span>Code</span><input value={projectForm.code} onChange={e => setProjectForm({ ...projectForm, code: e.target.value })} required /></div><div className="field"><span>Name</span><input value={projectForm.name} onChange={e => setProjectForm({ ...projectForm, name: e.target.value })} required /></div><button className="primary" disabled={saving === "project"}>{button("project", "Create project")}</button></form><div className="list">{loading ? <div className="muted">Loading projects…</div> : projects.length === 0 ? <div className="muted">No projects yet.</div> : projects.map(project => <button key={project.id} className={`row ${selected?.id === project.id ? "selected" : ""}`} onClick={() => void select(project)}><span><strong>{project.name}</strong><br /><small className="muted">{project.code}</small></span><span className="muted">{project.status}</span></button>)}</div></section>
      <section className="card"><h2>{selected ? selected.name : "Selected project"}</h2>{selected ? <><p className="muted">{selected.description || "No description"}</p><div className="row"><span>Budget remaining</span><strong>{money(summary?.budget_remaining)}</strong></div><div className="row"><span>Expenses</span><strong>{money(summary?.expense_total)}</strong></div><h3>Add budget</h3><form onSubmit={submitBudget}><div className="field"><span>Name</span><input value={budgetForm.name} onChange={e => setBudgetForm({ ...budgetForm, name: e.target.value })} required /></div><div className="field"><span>Amount</span><input type="number" min="0" step="0.01" value={budgetForm.amount} onChange={e => setBudgetForm({ ...budgetForm, amount: e.target.value })} required /></div><button className="primary" disabled={saving === "budget"}>{button("budget", "Add budget")}</button></form><h3>Add cost</h3><form onSubmit={submitCost}><div className="field"><span>Category</span><input value={costForm.category} onChange={e => setCostForm({ ...costForm, category: e.target.value })} required /></div><div className="field"><span>Quantity</span><input type="number" min="0.0001" step="0.0001" value={costForm.quantity} onChange={e => setCostForm({ ...costForm, quantity: e.target.value })} required /></div><div className="field"><span>Unit cost</span><input type="number" min="0" step="0.01" value={costForm.unit_cost} onChange={e => setCostForm({ ...costForm, unit_cost: e.target.value })} required /></div><button className="primary" disabled={saving === "cost"}>{button("cost", "Add cost")}</button></form><h3>Add transaction</h3><form onSubmit={submitTransaction}><div className="field"><span>Type</span><select value={txForm.type} onChange={e => setTxForm({ ...txForm, type: e.target.value })}><option>INCOME</option><option>EXPENSE</option><option>ADJUSTMENT</option></select></div><div className="field"><span>Amount</span><input type="number" min="0.01" step="0.01" value={txForm.amount} onChange={e => setTxForm({ ...txForm, amount: e.target.value })} required /></div><div className="field"><span>Description</span><input value={txForm.description} onChange={e => setTxForm({ ...txForm, description: e.target.value })} /></div><button className="primary" disabled={saving === "transaction"}>{button("transaction", "Add transaction")}</button></form></> : <p className="muted">Create or select a project to begin.</p>}</section></div>
  </div></main>;
}

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  useEffect(() => setAuthenticated(Boolean(localStorage.getItem("buildcost_access"))), []);
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;
  return <Dashboard onLogout={() => { localStorage.removeItem("buildcost_access"); localStorage.removeItem("buildcost_refresh"); setAuthenticated(false); }} />;
}
