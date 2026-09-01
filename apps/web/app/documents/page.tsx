export default function DocumentsPage() {
  const modules = [
    ["1", "Document Register", "Track project documents with type, number, status and current version."],
    ["2", "Versioning", "Create immutable version records and keep the current version pointer."],
    ["3", "Attachments", "Reference stored files without coupling the workflow to a storage provider."],
    ["4", "Approval Workflow", "Move documents through draft, review, approval and rejection states."],
    ["5", "Audit Trail", "Record version, attachment, approval and status-change events."],
  ];
  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <h1>Documents & Workflow</h1>
      <p>Metadata → versions → attachments → approval → audit trail.</p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16, marginTop: 24 }}>
        {modules.map(([number, title, description]) => (
          <article key={number} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 20 }}>
            <strong>Module {number}</strong><h2>{title}</h2><p>{description}</p>
          </article>
        ))}
      </section>
      <section style={{ marginTop: 32, borderTop: "1px solid #ddd", paddingTop: 24 }}>
        <h2>Workflow controls</h2>
        <ul>
          <li>Archived documents cannot be versioned.</li>
          <li>Only valid status transitions are accepted.</li>
          <li>Approval is only accepted while a document is in review.</li>
          <li>Attachments must reference an existing document version.</li>
          <li>Every state-changing action creates an audit record.</li>
        </ul>
      </section>
    </main>
  );
}
