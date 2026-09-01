export default function AccountingPage() {
  const modules = [
    ["1", "Transactions", "Classify income, expense and adjustments with tax and retention fields."],
    ["2", "Payments", "Record payment settlement status against project transactions."],
    ["3", "Retention", "Track retained amounts and release status."],
    ["4", "Financial Periods", "Open and close accounting periods to protect financial history."],
    ["5", "Reconciliation", "Compare expected period totals with recorded transactions."],
  ];

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <h1>Accounting & Financial Controls</h1>
      <p>Transactions → payments → retention → financial periods → reconciliation.</p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16, marginTop: 24 }}>
        {modules.map(([number, title, description]) => (
          <article key={number} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20 }}>
            <strong>Module {number}</strong>
            <h2>{title}</h2>
            <p>{description}</p>
          </article>
        ))}
      </section>
      <section style={{ marginTop: 32, borderTop: "1px solid #ddd", paddingTop: 24 }}>
        <h2>Financial controls</h2>
        <ul>
          <li>Financial periods cannot have reversed date ranges.</li>
          <li>Closed periods reject new accounting transactions.</li>
          <li>Transaction dates must fall inside the selected period.</li>
          <li>Retention cannot exceed the transaction retention allowance.</li>
          <li>Reconciliation records both difference and match status.</li>
        </ul>
      </section>
    </main>
  );
}
