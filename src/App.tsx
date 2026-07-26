import { useEffect, useMemo, useState } from 'react'
import { ArrowDown, BookOpen, Filter, Github, Info, Orbit, Sparkles } from 'lucide-react'
import { Constellation } from './components/Constellation'
import { FilterPanel } from './components/FilterPanel'
import { Insights } from './components/Insights'
import { Legend } from './components/Legend'
import { PaperDetails } from './components/PaperDetails'
import { MODE_LABELS } from './constants'
import type { Cluster, ColorMode, Filters, Paper, Summary } from './types'

const defaultFilters: Filters = { search: '', yearMin: 2015, yearMax: 2025, domains: [], methods: [], roles: [], physics: [] }

export default function App() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [mode, setMode] = useState<ColorMode>('domain')
  const [filters, setFilters] = useState(defaultFilters)
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
        <a className="brand" href="#top"><Orbit size={20} /><span>EARTH / AI</span></a>
        <nav>
          <a href="#explore">Explore</a>
          <a href="#insights">Insights</a>
          <a href="#methodology">Methodology</a>
        </nav>
        <a className="github-link" href="https://github.com/" target="_blank" rel="noreferrer"><Github size={16} /> View source</a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <div className="demo-banner"><Sparkles size={13} /> Visual demo · synthetic corpus</div>
            <p className="eyebrow">AN INTERACTIVE CONSTELLATION OF RESEARCH</p>
            <h1>What Does <em>“AI”</em> Mean<br />in Earth Science?</h1>
            <p className="subtitle">Explore how machine learning is actually used across Earth and planetary research.</p>
            <div className="hero-primer">
              <span><b>01</b> Each point is one paper</span>
              <span><b>02</b> Nearby papers are semantically related</span>
              <span><b>03</b> Recolor the map to shift perspective</span>
            </div>
          </div>
          <div className="hero-orbit" aria-hidden="true">
            <div className="orbital-ring ring-one"><i /><i /><i /></div>
            <div className="orbital-ring ring-two"><i /><i /></div>
            <div className="planet"><span>108</span><small>DEMO<br />PAPERS</small></div>
          </div>
          <a className="scroll-cue" href="#explore">Begin exploring <ArrowDown size={15} /></a>
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
            <FilterPanel filters={filters} setFilters={setFilters} visibleCount={visiblePapers.length} totalCount={papers.length} open={filtersOpen} onClose={() => setFiltersOpen(false)} />
            <div className="map-shell">
              {visiblePapers.length ? (
                <Constellation papers={visiblePapers} clusters={clusters} mode={mode} selectedPaper={selectedPaper} onSelect={setSelectedPaper} />
              ) : (
                <div className="empty-state"><Orbit size={30} /><h3>No papers match this view</h3><p>Broaden the filters to bring the constellation back into view.</p><button onClick={() => setFilters(defaultFilters)}>Reset filters</button></div>
              )}
            </div>
          </div>
        </section>

        <Insights papers={papers} />

        <section className="method-section" id="methodology">
          <div className="method-heading">
            <p className="eyebrow">METHOD BEFORE MEANING</p>
            <h2>How this map is made</h2>
            <p>This first release uses clearly marked synthetic records to test the interface. The included open pipeline replaces them with a selected OpenAlex corpus.</p>
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
        <div><Orbit size={22} /><strong>EARTH / AI</strong></div>
        <p>An open-source experiment in making scientific language visible.</p>
        <span>Demo data · No scientific conclusions implied</span>
      </footer>
      <PaperDetails paper={selectedPaper} onClose={() => setSelectedPaper(null)} />
      {filtersOpen && <button className="drawer-backdrop" onClick={() => setFiltersOpen(false)} aria-label="Close filter drawer" />}
    </>
  )
}
