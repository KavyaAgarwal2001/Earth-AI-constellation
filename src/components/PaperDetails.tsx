import { ArrowUpRight, Beaker, BrainCircuit, Orbit, X } from 'lucide-react'
import type { Paper } from '../types'

const Field = ({ label, value }: { label: string; value: string }) => (
  <div className="detail-field"><span>{label}</span><strong>{value}</strong></div>
)

export function PaperDetails({ paper, onClose }: { paper: Paper | null; onClose: () => void }) {
  if (!paper) return null
  return (
    <aside className="details-panel" aria-label="Selected paper details">
      <div className="details-top">
        <span className="demo-pill">{paper.demo ? 'DEMO PAPER' : 'OPENALEX PAPER'}</span>
        <button onClick={onClose} aria-label="Close paper details"><X size={18} /></button>
      </div>
      <p className="eyebrow">{paper.year} · {paper.cluster}</p>
      <h2>{paper.title}</h2>
      <p className="authors">{paper.authors.join(', ')}</p>
      <p className="abstract">{paper.abstract}</p>
      <div className="detail-grid">
        <Field label="Scientific domain" value={paper.domain} />
        <Field label="Detected AI method" value={paper.aiMethod} />
        <Field label="Scientific role" value={paper.aiRole} />
        <Field label="Physics integration" value={paper.physicsIntegration} />
        {paper.venue && <Field label="Venue" value={paper.venue} />}
        {paper.citationCount !== undefined && <Field label="OpenAlex citations" value={paper.citationCount.toLocaleString()} />}
      </div>
      <div className="confidence-block">
        <div><span>Classification confidence</span><strong>{Math.round(paper.confidence * 100)}%</strong></div>
        <div className="confidence-track"><i style={{ width: `${paper.confidence * 100}%` }} /></div>
      </div>
      <div className="evidence">
        <Beaker size={16} />
        <div><span>Classification evidence</span><p>“{paper.evidence}”</p></div>
      </div>
      <div className="detail-icons">
        <span><BrainCircuit size={14} /> Rule-based automatic label</span>
        <span><Orbit size={14} /> Approximate semantic position</span>
      </div>
      <a className="paper-link" href={paper.url} target="_blank" rel="noreferrer">Open paper record <ArrowUpRight size={15} /></a>
    </aside>
  )
}
