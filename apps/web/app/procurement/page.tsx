export default function ProcurementPage() {
  const stages = [
    ["1", "Purchase Request", "Create and track procurement requests"],
    ["2", "RFQ / Quotations", "Compare supplier quotations"],
    ["3", "Purchase Order", "Issue and track purchase orders"],
    ["4", "Receiving", "Track partial and completed receipts"],
  ];

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <h1>Procurement</h1>
      <p>Purchase request → quotation comparison → purchase order → receiving lifecycle.</p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16, marginTop: 24 }}>
        {stages.map(([number, title, description]) => (
          <article key={number} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20 }}>
            <strong>Stage {number}</strong>
            <h2>{title}</h2>
            <p>{description}</p>
          </article>
        ))}
      </section>
      <section style={{ marginTop: 32, borderTop: "1px solid #ddd", paddingTop: 24 }}>
        <h2>Procurement controls</h2>
        <ul>
          <li>Supplier must be active.</li>
          <li>Quantities must be greater than zero.</li>
          <li>Receiving cannot exceed ordered quantity.</li>
          <li>Quotation selection records the winning supplier offer.</li>
        </ul>
      </section>
    </main>
  );
}
