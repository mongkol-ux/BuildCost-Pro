"use client";

import { useState } from "react";

export default function ReportsPage() {
  const [projectId, setProjectId] = useState("");
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  async function loadReport() {
    setError("");
    setData(null);
    if (!projectId.trim()) {
      setError("Enter a project ID.");
      return;
    }
    try {
      const response = await fetch(`/api/v1/reports/projects/${encodeURIComponent(projectId)}/dashboard`);
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      setData(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load report.");
    }
  }

  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: 32 }}>
      <h1>Reporting & Dashboard</h1>
      <p>Budget vs actual, commitments, BOQ and cost analytics for a project.</p>
      <section style={{ display: "flex", gap: 12, marginTop: 24 }}>
        <input value={projectId} onChange={(e) => setProjectId(e.target.value)} placeholder="Project ID" aria-label="Project ID" style={{ flex: 1, padding: 12, border: "1px solid #ccc", borderRadius: 8 }} />
        <button onClick={loadReport} style={{ padding: "12px 18px", borderRadius: 8, border: "1px solid #222", cursor: "pointer" }}>Load report</button>
      </section>
      {error && <p role="alert" style={{ marginTop: 16 }}>{error}</p>}
      {data && (
        <>
          <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 16, marginTop: 28 }}>
            {Object.entries(data.kpi).map(([key, value]) => (
              <article key={key} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 18 }}>
                <small>{key.replaceAll("_", " ")}</small>
                <h2 style={{ marginBottom: 0 }}>{String(value ?? "—")}</h2>
              </article>
            ))}
          </section>
          <section style={{ marginTop: 28 }}>
            <h2>Cost by category</h2>
            <ul>{data.cost_by_category.map((row: any) => <li key={row.category}>{row.category}: {row.amount}</li>)}</ul>
            <p>BOQ total: {data.boq_total} ({data.boq_items} items)</p>
            <p>Procurement commitment: {data.procurement_commitment}</p>
          </section>
          <a href={`/api/v1/reports/projects/${encodeURIComponent(projectId)}/export.csv`} style={{ display: "inline-block", marginTop: 12 }}>Export CSV</a>
        </>
      )}
    </main>
  );
}
