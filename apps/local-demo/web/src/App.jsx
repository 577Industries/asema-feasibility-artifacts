import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Download, GitBranch, ShieldCheck } from 'lucide-react';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function useJson(path) {
  const [data, setData] = useState([]);
  useEffect(() => { fetch(`${API}${path}`).then(r => r.json()).then(setData).catch(() => setData([])); }, [path]);
  return data;
}

function App() {
  const evidence = useJson('/evidence');
  const scores = useJson('/scores');
  const recs = useJson('/recommendations');
  return (
    <main>
      <header>
        <ShieldCheck size={28} />
        <div><h1>AegisGraph ASEMA</h1><p>Local evidence graph demo over generated public artifacts and SQLite.</p></div>
      </header>
      <section className="metrics">
        <article><GitBranch /><strong>{evidence.length}</strong><span>evidence records</span></article>
        <article><ShieldCheck /><strong>{scores.length}</strong><span>scored paths</span></article>
        <article><Download /><strong>{recs.length}</strong><span>recommendations</span></article>
      </section>
      <section><h2>Top Assessment Paths</h2>{scores.map(s => <div className="row" key={`${s.target_id}-${s.path_id}`}><span>{s.target_id} / {s.path_id}</span><b>{Number(s.score).toFixed(1)}</b></div>)}</section>
      <section><h2>Recommendation Worklist</h2>{recs.map(r => <div className="row" key={r.recommendation_id}><span>{r.title}</span><b>{r.recommendation_id}</b></div>)}</section>
      <footer>Static real-target observations are review-priority signals, not vulnerability claims.</footer>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
