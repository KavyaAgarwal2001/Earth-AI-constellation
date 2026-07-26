import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, BookOpen, Database, Filter, Github, Info, Orbit } from 'lucide-react'
import { Constellation } from './components/Constellation'
import { FilterPanel } from './components/FilterPanel'
import { Insights } from './components/Insights'
import { Legend } from './components/Legend'
import { PaperDetails } from './components/PaperDetails'
import { MODE_LABELS } from './constants'
import type { Cluster, ColorMode, Filters, Paper, Summary } from './types'

const initialFilters: Filters = { search: '', yearMin: 2015, yearMax: 2026, domains: [], methods: [], roles: [], physics: [] }

export default function App() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [mode, setMode] = useState<ColorMode>('domain')
  const [filters, setFilters] = useState(initialFilters)
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const base = import.meta.env.BASE_URL
    Promise.all([
      fetch(`${base}data/papers.json`).then((response) => response.ok ? response.json() : Promise.reject(new Error('Paper data unavailable'))),
      fetch(`${base}data/clusters.json`).then((response) => response.json()),
      fetch(`${base}data/summary.json`).then((response) => response.json()),
    ]).then(([paperData, clusterData, summaryData]) => {
      setPapers(paperData)
      setClusters(clusterData)
      setSummary(summaryData)
      setFilters((current) => ({ ...current, yearMin: summaryData.yearRange[0], yearMax: summaryData.yearRange[1] }))
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load the constellation'))
  }, [])

  const visiblePapers = useMemo(() => papers.filter((paper) =>
    paper.year >= filters.yearMin &&
    paper.year <= filters.yearMax &&
    (!filters.search || paper.title.toLowerCase().includes(filters.search.toLowerCase())) &&
    (!filters.domains.length || filters.domains.includes(paper.domain)) &&
    (!filters.methods.length || filters.methods.includes(paper.aiMethod)) &&
    (!filters.roles.length || filters.roles.includes(paper.aiRole)) &&
    (!filters.physics.length || filters.physics.includes(paper.physicsIntegration))
  ), [papers, filters])

  if (error) return <main className="state-screen"><Orbit size={38} /><h1>The constellation could not load.</h1><p>{error}. Try refreshing the page.</p></main>
  if (!summary) return <main className="state-screen loading"><Orbit size={38} /><h1>Charting the research landscape…</h1><p>Loading paper positions and classifications.</p></main>

  return (
    <>
      <header className="site-header">
        <a className="brand" href="#top"><span>EARTH AI ATLAS</span><small>RELEASE 01</small></a>
        <nav>
          <a href="#explore">Explore</a>
          <a href="#insights">Insights</a>
          <a href="#methodology">Methodology</a>
        </nav>
        <a className="github-link" href="https://github.com/KavyaAgarwal2001/Earth-AI-constellation" target="_blank" rel="noreferrer"><Github size={15} /> Source</a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">OPEN RESEARCH ATLAS / 2015—2026</p>
            <h1>What does <em>“AI”</em> mean <span>in Earth science?</span></h1>
            <p className="subtitle">A semantic map of how machine learning is actually used across Earth and planetary research—not just how it is described.</p>
            <div className="hero-actions">
              <a className="primary-action" href="#explore">Explore the papers <ArrowRight size={16} /></a>
              <a className="text-action" href="#methodology">Read the methodology</a>
            </div>
          </div>
          <aside className="data-ledger">
            <div className="ledger-heading"><Database size={15} /><span>DATA RELEASE</span><b>{summary.generatedAt}</b></div>
            <dl>
              <div><dt>Papers</dt><dd>{summary.paperCount.toLocaleString()}</dd></div>
              <div><dt>Domains</dt><dd>5</dd></div>
              <div><dt>Clusters</dt><dd>{clusters.length}</dd></div>
              <div><dt>Source</dt><dd>{summary.source ?? 'OpenAlex'}</dd></div>
            </dl>
            <p>Selected corpus. Automatic labels remain visible as evidence, uncertainty, and “unclear” classifications.</p>
          </aside>
          <div className="hero-primer">
            <span><b>01</b> One point per paper</span>
            <span><b>02</b> Proximity reflects language</span>
            <span><b>03</b> Six analytical lenses</span>
          </div>
        </section>

        <section className="explorer-section" id="explore">
          <div className="explorer-heading">
            <div>
              <p className="eyebrow">ONE MAP, SIX LENSES</p>
              <h2>Explore the constellation</h2>
            </div>
            <button className="mobile-filter-button" onClick={() => setFiltersOpen(true)}><Filter size={15} /> Filters <b>{visiblePapers.length}</b></button>
          </div>
          <div className="mode-tabs" role="tablist" aria-label="Color papers by">
            {(Object.keys(MODE_LABELS) as ColorMode[]).map((key) => (
              <button key={key} className={mode === key ? 'active' : ''} onClick={() => setMode(key)}>{MODE_LABELS[key]}</button>
            ))}
          </div>
          <Legend mode={mode} />
          <div className="explorer-layout">
            <FilterPanel filters={filters} setFilters={setFilters} visibleCount={visiblePapers.length} totalCount={papers.length} yearRange={summary.yearRange} isDemo={summary.demo} open={filtersOpen} onClose={() => setFiltersOpen(false)} />
            <div className="map-shell">
              {visiblePapers.length ? (
                <Constellation papers={visiblePapers} clusters={clusters} mode={mode} selectedPaper={selectedPaper} onSelect={setSelectedPaper} />
              ) : (
                <div className="empty-state"><Orbit size={30} /><h3>No papers match this view</h3><p>Broaden the filters to bring the constellation back into view.</p><button onClick={() => setFilters({ ...initialFilters, yearMin: summary.yearRange[0], yearMax: summary.yearRange[1] })}>Reset filters</button></div>
              )}
            </div>
          </div>
        </section>

        <Insights papers={papers} />

        <section className="method-section" id="methodology">
          <div className="method-heading">
            <p className="eyebrow">METHOD BEFORE MEANING</p>
            <h2>How this map is made</h2>
            <p>{summary.demo ? 'This preview uses clearly marked synthetic records to test the interface. The included open pipeline replaces them with a selected OpenAlex corpus.' : `This release maps ${summary.paperCount.toLocaleString()} selected OpenAlex papers using transparent automatic labels and a reproducible semantic layout.`}</p>
          </div>
          <div className="method-steps">
            <article><span>01</span><div><h3>Collect</h3><p>Query OpenAlex for Earth and planetary research that mentions machine-learning terminology. Cache raw records and document the selection.</p></div></article>
            <article><span>02</span><div><h3>Classify</h3><p>Transparent title-and-abstract patterns assign domain, method, scientific role, and physics integration—with evidence and confidence.</p></div></article>
            <article><span>03</span><div><h3>Embed</h3><p>A sentence transformer turns each title and abstract into a semantic vector representing its language and research focus.</p></div></article>
            <article><span>04</span><div><h3>Project</h3><p>Seeded UMAP reduces those vectors to two approximate dimensions. Nearby points use similar language; distance is not an exact metric.</p></div></article>
          </div>
          <div className="method-notes">
            <article>
              <Info size={18} />
              <div><h3>What confidence means</h3><p>Confidence reflects the strength and specificity of matched textual evidence—not scientific quality or a probability that the label is correct. “Unclear” is a valid result.</p></div>
            </article>
            <article>
              <BookOpen size={18} />
              <div><h3>What this corpus cannot tell us</h3><ul>
                <li>It is a selected corpus, not every Earth-science paper.</li>
                <li>Abstracts can be missing; automated labels can be wrong.</li>
                <li>Fields overlap, and UMAP positions are approximate.</li>
                <li>Mentioning a method is not the same as implementing it.</li>
                <li>Citation counts do not represent scientific quality.</li>
              </ul></div>
            </article>
          </div>
        </section>
      </main>

      <footer>
        <div><strong>EARTH AI ATLAS</strong><span>Open-source research visualization</span></div>
        <p>Designed and built by Kavya Agarwal.</p>
        <span>{summary.demo ? 'Demo data · No scientific conclusions implied' : `OpenAlex snapshot · ${summary.generatedAt}`}</span>
      </footer>
      <PaperDetails paper={selectedPaper} onClose={() => setSelectedPaper(null)} />
      {filtersOpen && <button className="drawer-backdrop" onClick={() => setFiltersOpen(false)} aria-label="Close filter drawer" />}
    </>
  )
}
