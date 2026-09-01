"use client";

import { FormEvent, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://buildcost-pro-production.up.railway.app";
type Project = { id: string; code: string; name: string };
type Revision = { id: string; revision_no: number; name: string; budget_id?: string | null; status: string };
type Item = { id: string; item_code: string; description: string; unit: string; quantity: string; unit_rate: string; total: string };
type Summary = { budget_amount: string; estimate_total: string; variance: string; variance_percent?: string | null; item_count: number };

async function api(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("buildcost_access") : null;
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  return response.json();
}

export default function BOQPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState("");
  const [revisions, setRevisions] = useState<Revision[]>([]);
  const [revisionId, setRevisionId] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [form, setForm] = useState({ name: "Estimate Rev 1", budget_id: "" });
  const [item, setItem] = useState({ item_code: "", description: "", unit: "", quantity: "", unit_rate: "" });
  const [error, setError] = useState("");

  const loadProjects = async () => { const rows = await api("/api/v1/projects"); setProjects(rows); if (!projectId && rows[0]) setProjectId(rows[0].id); };
  const loadRevisions = async () => { if (!projectId) return; const rows = await api(`/api/v1/projects/${projectId}/boq`); setRevisions(rows); if (rows[0]) setRevisionId(rows[0].id); };
  const loadRevision = async () => { if (!revisionId) return; const [rows, totals] = await Promise.all([api(`/api/v1/boq/${revisionId}/items`), api(`/api/v1/boq/${revisionId}/summary`)]); setItems(rows); setSummary(totals); };
  useEffect(() => { void loadProjects().catch(e => setError(e.message)); }, []);
  useEffect(() => { void loadRevisions().catch(e => setError(e.message)); }, [projectId]);
  useEffect(() => { void loadRevision().catch(e => setError(e.message)); }, [revisionId]);

  const createRevision = async (e: FormEvent) => { e.preventDefault(); try { const row = await api(`/api/v1/projects/${projectId}/boq`, { method: "POST", body: JSON.stringify({ name: form.name, budget_id: form.budget_id || null }) }); setRevisionId(row.id); await loadRevisions(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to create revision"); } };
  const createItem = async (e: FormEvent) => { e.preventDefault(); try { await api(`/api/v1/boq/${revisionId}/items`, { method: "POST", body: JSON.stringify(item) }); setItem({ item_code: "", description: "", unit: "", quantity: "", unit_rate: "" }); await loadRevision(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to create item"); } };
  const money = (v?: string | null) => v == null ? "—" : Number(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return <main className="page"><div className="shell"><header className="header"><div><div className="brand">BuildCost Pro</div><div className="muted">BOQ & Estimating · STEP 32</div></div></header>
    {error && <div className="card error">{error}</div>}
    <section className="card"><h2>BOQ / Estimate</h2><label className="field"><span>Project</span><select value={projectId} onChange={e => setProjectId(e.target.value)}>{projects.map(p => <option key={p.id} value={p.id}>{p.code} — {p.name}</option>)}</select></label><form onSubmit={createRevision}><div className="field"><span>Revision name</span><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /></div><div className="field"><span>Budget ID (optional)</span><input value={form.budget_id} onChange={e => setForm({ ...form, budget_id: e.target.value })} /></div><button className="primary" disabled={!projectId}>Create revision</button></form><label className="field"><span>Revision</span><select value={revisionId} onChange={e => setRevisionId(e.target.value)}>{revisions.map(r => <option key={r.id} value={r.id}>Rev {r.revision_no} — {r.name}</option>)}</select></label></section>
    {revisionId && <><section className="stats"><div className="card"><div className="muted">Budget</div><div className="stat-value">{money(summary?.budget_amount)}</div></div><div className="card"><div className="muted">Estimate</div><div className="stat-value">{money(summary?.estimate_total)}</div></div><div className="card"><div className="muted">Variance</div><div className="stat-value">{money(summary?.variance)}</div></div></section><section className="card"><h2>Add estimate item</h2><form onSubmit={createItem}><div className="field"><span>Item code</span><input value={item.item_code} onChange={e => setItem({ ...item, item_code: e.target.value })} required /></div><div className="field"><span>Description</span><input value={item.description} onChange={e => setItem({ ...item, description: e.target.value })} required /></div><div className="field"><span>Unit</span><input value={item.unit} onChange={e => setItem({ ...item, unit: e.target.value })} required /></div><div className="field"><span>Quantity</span><input type="number" min="0.0001" step="0.0001" value={item.quantity} onChange={e => setItem({ ...item, quantity: e.target.value })} required /></div><div className="field"><span>Unit rate</span><input type="number" min="0" step="0.01" value={item.unit_rate} onChange={e => setItem({ ...item, unit_rate: e.target.value })} required /></div><button className="primary">Add item</button></form><div className="list">{items.length === 0 ? <div className="muted">No estimate items yet.</div> : items.map(x => <div className="row" key={x.id}><span><strong>{x.item_code}</strong> — {x.description}<br /><small className="muted">{x.quantity} {x.unit} × {money(x.unit_rate)}</small></span><strong>{money(x.total)}</strong></div>)}</div></section></>}
  </div></main>;
}
