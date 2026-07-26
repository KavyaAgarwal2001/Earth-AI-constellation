import { RotateCcw, Search, SlidersHorizontal, X } from 'lucide-react'
import { DOMAINS, METHODS, PHYSICS, ROLES } from '../constants'
import type { Filters } from '../types'

interface Props {
  filters: Filters
  setFilters: (filters: Filters) => void
  visibleCount: number
  totalCount: number
  yearRange: [number, number]
  isDemo: boolean
  open: boolean
  onClose: () => void
}

const MultiFilter = ({ label, options, selected, onChange }: { label: string; options: string[]; selected: string[]; onChange: (items: string[]) => void }) => (
  <details className="filter-group">
    <summary>
      <span>{label}</span>
      {selected.length > 0 && <b>{selected.length}</b>}
    </summary>
    <div className="filter-options">
      {options.map((option) => (
        <label key={option}>
          <input
            type="checkbox"
            checked={selected.includes(option)}
            onChange={() => onChange(selected.includes(option) ? selected.filter((item) => item !== option) : [...selected, option])}
          />
          <span>{option}</span>
        </label>
      ))}
    </div>
  </details>
)

export function FilterPanel({ filters, setFilters, visibleCount, totalCount, yearRange, isDemo, open, onClose }: Props) {
  const reset = () => setFilters({ search: '', yearMin: yearRange[0], yearMax: yearRange[1], domains: [], methods: [], roles: [], physics: [] })
  const active = filters.search || filters.yearMin !== yearRange[0] || filters.yearMax !== yearRange[1] || filters.domains.length || filters.methods.length || filters.roles.length || filters.physics.length

  return (
    <aside className={`filter-panel ${open ? 'open' : ''}`}>
      <div className="panel-heading">
        <div><SlidersHorizontal size={16} /><strong>Refine the corpus</strong></div>
        <button className="mobile-close" onClick={onClose} aria-label="Close filters"><X size={18} /></button>
      </div>
      <div className="visible-count">
        <strong>{visibleCount}</strong>
        <span>of {totalCount} {isDemo ? 'demo ' : ''}papers visible</span>
      </div>
      <label className="search-box">
        <Search size={16} />
        <input
          value={filters.search}
          onChange={(event) => setFilters({ ...filters, search: event.target.value })}
          placeholder="Search paper titles"
          aria-label="Search paper titles"
        />
        {filters.search && <button onClick={() => setFilters({ ...filters, search: '' })} aria-label="Clear search"><X size={14} /></button>}
      </label>
      <div className="year-filter">
        <div><span>Publication year</span><strong>{filters.yearMin}–{filters.yearMax}</strong></div>
        <label>From <input type="range" min={yearRange[0]} max={yearRange[1]} value={filters.yearMin} onChange={(e) => setFilters({ ...filters, yearMin: Math.min(Number(e.target.value), filters.yearMax) })} /></label>
        <label>To <input type="range" min={yearRange[0]} max={yearRange[1]} value={filters.yearMax} onChange={(e) => setFilters({ ...filters, yearMax: Math.max(Number(e.target.value), filters.yearMin) })} /></label>
      </div>
      <div className="filter-list">
        <MultiFilter label="Scientific domain" options={DOMAINS} selected={filters.domains} onChange={(domains) => setFilters({ ...filters, domains })} />
        <MultiFilter label="AI method" options={METHODS} selected={filters.methods} onChange={(methods) => setFilters({ ...filters, methods })} />
        <MultiFilter label="Scientific role" options={ROLES} selected={filters.roles} onChange={(roles) => setFilters({ ...filters, roles })} />
        <MultiFilter label="Physics integration" options={PHYSICS} selected={filters.physics} onChange={(physics) => setFilters({ ...filters, physics })} />
      </div>
      <button className="reset-button" onClick={reset} disabled={!active}><RotateCcw size={14} /> Reset all filters</button>
    </aside>
  )
}
