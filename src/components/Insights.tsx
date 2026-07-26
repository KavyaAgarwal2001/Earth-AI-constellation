import { useMemo } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ArrowUpRight } from 'lucide-react'
import { DOMAINS, METHODS, PALETTES, PHYSICS } from '../constants'
import type { Paper } from '../types'
import { percent } from '../utils'

const tooltipStyle = { background: '#111722', border: '1px solid #263244', borderRadius: 10, color: '#e8eef6', fontSize: 12 }

const countBy = (papers: Paper[], key: (paper: Paper) => string, labels?: string[]) => {
  const counts = new Map<string, number>()
  papers.forEach((paper) => counts.set(key(paper), (counts.get(key(paper)) ?? 0) + 1))
  return (labels ?? [...counts.keys()]).map((name) => ({ name, count: counts.get(name) ?? 0, percentage: Math.round(((counts.get(name) ?? 0) / papers.length) * 100) }))
}

export function Insights({ papers }: { papers: Paper[] }) {
  const data = useMemo(() => {
    const years = countBy(papers, (paper) => String(paper.year)).sort((a, b) => Number(a.name) - Number(b.name))
    const domains = countBy(papers, (paper) => paper.domain, DOMAINS)
    const methods = countBy(papers, (paper) => paper.aiMethod, METHODS).filter((item) => item.count > 0).sort((a, b) => b.count - a.count)
    const physics = countBy(papers, (paper) => paper.physicsIntegration, PHYSICS).filter((item) => item.count > 0)
    const unclear = papers.filter((paper) => ['Method unclear', 'AI discussed but not implemented'].includes(paper.aiMethod)).length
    const roleDomain = DOMAINS.map((domain) => {
      const domainPapers = papers.filter((paper) => paper.domain === domain)
      return {
        name: domain.replace('Earth observation and remote sensing', 'Earth observation').replace('Solid Earth and geophysics', 'Solid Earth'),
        Forecasting: domainPapers.filter((p) => p.aiRole === 'Forecasting').length,
        Detection: domainPapers.filter((p) => p.aiRole === 'Detection').length,
        Classification: domainPapers.filter((p) => p.aiRole === 'Classification').length,
        'Other roles': domainPapers.filter((p) => !['Forecasting', 'Detection', 'Classification'].includes(p.aiRole)).length,
      }
    })
    return { years, domains, methods, physics, unclear, roleDomain }
  }, [papers])

  return (
    <section className="insights-section" id="insights">
      <div className="section-intro">
        <div>
          <p className="eyebrow">READ THE LANDSCAPE</p>
          <h2>Signals in the demo corpus</h2>
        </div>
        <p>Descriptive summaries of the current selection. Counts and percentages update with the same {papers.length}-paper demo corpus shown above.</p>
      </div>
      <div className="insight-grid">
        <article className="chart-card chart-wide">
          <div className="chart-title"><div><span>Momentum</span><h3>Papers by publication year</h3></div><strong>{papers.length} total</strong></div>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={data.years} margin={{ top: 14, right: 8, bottom: 0, left: -22 }}>
              <CartesianGrid vertical={false} stroke="#202936" />
              <XAxis dataKey="name" stroke="#748195" tickLine={false} axisLine={false} fontSize={11} />
              <YAxis stroke="#748195" tickLine={false} axisLine={false} fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value, _name, item) => [`${value} papers (${item.payload.percentage}%)`, 'Count']} />
              <Bar dataKey="count" fill="#6ce5b1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="chart-card stat-card">
          <span>Taxonomy watch</span>
          <strong>{percent(data.unclear, papers.length)}</strong>
          <h3>of papers have an unclear or unimplemented AI method</h3>
          <p>{data.unclear} of {papers.length} demo records. A useful reminder that “AI” can be rhetoric as well as method.</p>
          <a href="#methodology">How labels work <ArrowUpRight size={14} /></a>
        </article>
        <article className="chart-card">
          <div className="chart-title"><div><span>Where</span><h3>Scientific domains</h3></div></div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={data.domains} dataKey="count" nameKey="name" innerRadius={58} outerRadius={91} paddingAngle={2} stroke="none">
                {data.domains.map((item, index) => <Cell key={item.name} fill={PALETTES.domain[index]} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} formatter={(value, _name, item) => [`${value} papers (${item.payload.percentage}%)`, item.payload.name]} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mini-legend">{data.domains.map((item, i) => <span key={item.name}><i style={{ background: PALETTES.domain[i] }} />{item.name}<b>{item.count} · {item.percentage}%</b></span>)}</div>
        </article>
        <article className="chart-card">
          <div className="chart-title"><div><span>How</span><h3>AI method distribution</h3></div></div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={data.methods.slice(0, 10)} layout="vertical" margin={{ top: 8, right: 12, bottom: 0, left: 12 }}>
              <CartesianGrid horizontal={false} stroke="#202936" />
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={118} tick={{ fill: '#9daabc', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={tooltipStyle} formatter={(value, _name, item) => [`${value} papers (${item.payload.percentage}%)`, 'Count']} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {data.methods.slice(0, 10).map((item, index) => <Cell key={item.name} fill={PALETTES.method[METHODS.indexOf(item.name)] ?? PALETTES.method[index]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="chart-card chart-wide">
          <div className="chart-title"><div><span>Purpose</span><h3>AI roles by scientific domain</h3></div></div>
          <ResponsiveContainer width="100%" height={270}>
            <BarChart data={data.roleDomain} margin={{ top: 16, right: 8, bottom: 12, left: -20 }}>
              <CartesianGrid vertical={false} stroke="#202936" />
              <XAxis dataKey="name" stroke="#748195" tickLine={false} axisLine={false} fontSize={10} interval={0} />
              <YAxis stroke="#748195" tickLine={false} axisLine={false} fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#9daabc' }} />
              <Bar dataKey="Forecasting" stackId="a" fill="#55b8ff" />
              <Bar dataKey="Detection" stackId="a" fill="#ffbd66" />
              <Bar dataKey="Classification" stackId="a" fill="#6ce5b1" />
              <Bar dataKey="Other roles" stackId="a" fill="#ad8cff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="chart-card">
          <div className="chart-title"><div><span>Connection to theory</span><h3>Physics integration</h3></div></div>
          <div className="distribution-list">
            {data.physics.sort((a, b) => b.count - a.count).map((item) => (
              <div key={item.name}>
                <div><span>{item.name}</span><strong>{item.count} · {item.percentage}%</strong></div>
                <i><b style={{ width: `${item.percentage}%` }} /></i>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  )
}
