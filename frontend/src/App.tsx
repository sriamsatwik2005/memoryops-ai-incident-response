import { useEffect, useState } from 'react';
import { Activity, BrainCircuit, CheckCircle2, Search, ShieldAlert, Server, X } from 'lucide-react';
import { getIncidents, investigate, resolveIncident } from './services/api';
import type { Incident, Investigation } from './types';

export default function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [analysis, setAnalysis] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    try { setIncidents(await getIncidents()); } catch (e) { setError(String(e)); }
  }
  useEffect(() => { load(); }, []);

  async function runInvestigation(incident: Incident) {
    setSelected(incident); setAnalysis(null); setLoading(true); setError('');
    try { setAnalysis(await investigate(incident.external_id)); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  async function approve() {
    if (!selected || !analysis) return;
    await resolveIncident(selected.external_id, analysis.recommendation);
    await load();
    setSelected(null); setAnalysis(null);
  }

  const open = incidents.filter(i => i.status === 'OPEN').length;
  const resolved = incidents.filter(i => i.status === 'RESOLVED').length;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><ShieldAlert size={26}/><span>MemoryOps</span></div>
        <div className="tagline">AI Incident Response</div>
        <nav>
          <div className="nav active"><Activity size={18}/> Incidents</div>
          <div className="nav"><BrainCircuit size={18}/> Hindsight Memory</div>
          <div className="nav"><Server size={18}/> Services</div>
        </nav>
        <div className="sidebar-note">Prototype mode<br/><span>Human approval required</span></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><h1>Incident Command Center</h1><p>Investigate incidents using current evidence and historical memory.</p></div>
          <div className="status"><span className="dot"/> Systems operational</div>
        </header>

        {error && <div className="error">{error}</div>}

        <section className="stats">
          <div className="stat"><span>Open incidents</span><strong>{open}</strong></div>
          <div className="stat"><span>Resolved</span><strong>{resolved}</strong></div>
          <div className="stat"><span>Memory bank</span><strong>Active</strong></div>
        </section>

        <section className="panel">
          <div className="panel-title"><h2>Incidents</h2><Search size={18}/></div>
          <div className="incident-list">
            {incidents.map(i => (
              <div className="incident-row" key={i.id}>
                <div className={`severity ${i.severity.toLowerCase()}`}>{i.severity}</div>
                <div className="incident-main">
                  <strong>{i.external_id} · {i.service}</strong>
                  <span>{i.summary}</span>
                  <small>{i.metrics}</small>
                </div>
                <div className={`status-pill ${i.status.toLowerCase()}`}>{i.status}</div>
                {i.status === 'OPEN' && <button onClick={() => runInvestigation(i)}>Investigate</button>}
              </div>
            ))}
          </div>
        </section>
      </main>

      {selected && (
        <div className="modal-backdrop">
          <div className="modal">
            <button className="close" onClick={() => {setSelected(null); setAnalysis(null)}}><X/></button>
            <div className="modal-head"><ShieldAlert/><div><h2>{selected.external_id}</h2><p>{selected.service} · {selected.severity}</p></div></div>
            <div className="evidence"><b>Current evidence</b><p>{selected.summary}</p><code>{selected.logs}</code><code>{selected.metrics}</code></div>
            {loading && <div className="loading"><BrainCircuit/> Agent investigating and recalling Hindsight memories…</div>}
            {analysis && <>
              <div className="memory-box"><div className="box-head"><BrainCircuit/> Hindsight Memory</div>
                {analysis.memories.length ? analysis.memories.map((m, idx) => <div className="memory" key={m.id || idx}><span>{m.type || 'experience'}</span><p>{m.text}</p></div>) : <p>No relevant historical memories found.</p>}
              </div>
              <div className="analysis"><h3>Agent Analysis</h3><p><b>Likely root cause:</b> {analysis.root_cause}</p><p><b>Confidence:</b> {Math.round(analysis.confidence * 100)}%</p><p><b>Why:</b> {analysis.reasoning}</p><div className="recommendation"><b>Recommended action</b><p>{analysis.recommendation}</p></div></div>
              <button className="approve" onClick={approve}><CheckCircle2/> Approve & Resolve</button>
            </>}
          </div>
        </div>
      )}
    </div>
  );
}
