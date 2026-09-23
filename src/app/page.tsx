const findings = [["ACL","Pending inference"],["Meniscus","Pending inference"],["Cartilage","Pending inference"],["OA","Pending inference"]];
export default function Home() {
  return <main className="shell">
    <header className="topbar"><div><strong>OmniSkel-AI</strong><span> / Knee MRI Workbench</span></div><span className="status">RESEARCH MODE</span></header>
    <section className="grid"><div className="viewer"><div className="viewerHeader">Study Viewer</div><div className="viewport"><div className="placeholder">DICOM viewport</div><div className="slice">No study loaded</div></div></div>
    <aside className="panel"><h2>Findings</h2>{findings.map(([n,v])=><div className="finding" key={n}><span>{n}</span><span>{v}</span></div>)}
    <h2>Quantification</h2><div className="metric"><span>Cartilage thickness</span><b>—</b></div><div className="metric"><span>Joint-space width</span><b>—</b></div><div className="metric"><span>Meniscal extrusion</span><b>—</b></div>
    <h2>Pipeline</h2><ol>{["DICOM ingestion","Quality control","Anatomy segmentation","Pathology inference","Quantification","Explainability"].map(x=><li key={x}>{x}</li>)}</ol></aside></section>
  </main>;
}
