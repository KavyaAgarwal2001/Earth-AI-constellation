import { useMemo, useState } from 'react'
import DeckGL from '@deck.gl/react'
import { OrthographicView } from '@deck.gl/core'
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers'
import { Minus, Plus, Scan, Sparkles } from 'lucide-react'
import type { ColorMode, Cluster, Paper } from '../types'
import { colorForPaper, truncate } from '../utils'

interface Props {
  papers: Paper[]
  clusters: Cluster[]
  mode: ColorMode
  selectedPaper: Paper | null
  onSelect: (paper: Paper) => void
}

interface HoverInfo {
  x: number
  y: number
  paper: Paper
}

const INITIAL_VIEW = { target: [0, 0, 0] as [number, number, number], zoom: 1.15, minZoom: -0.5, maxZoom: 5 }

export function Constellation({ papers, clusters, mode, selectedPaper, onSelect }: Props) {
  const [hover, setHover] = useState<HoverInfo | null>(null)
  const [viewState, setViewState] = useState(INITIAL_VIEW)

  const layers = useMemo(() => [
    new ScatterplotLayer<Paper>({
      id: 'paper-halos',
      data: papers,
      getPosition: (d) => [d.x, d.y],
      getRadius: (d) => d.id === selectedPaper?.id ? 14 : 7,
      radiusUnits: 'pixels',
      getFillColor: (d) => [...colorForPaper(d, mode), d.id === selectedPaper?.id ? 105 : 26],
      stroked: false,
      pickable: false,
      updateTriggers: { getFillColor: [mode, selectedPaper?.id], getRadius: [selectedPaper?.id] },
    }),
    new ScatterplotLayer<Paper>({
      id: 'papers',
      data: papers,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 90],
      getPosition: (d) => [d.x, d.y],
      getRadius: (d) => d.id === selectedPaper?.id ? 6.5 : 3.6,
      radiusUnits: 'pixels',
      radiusMinPixels: 2.5,
      getFillColor: (d) => [...colorForPaper(d, mode), 230],
      getLineColor: [255, 255, 255, 190],
      getLineWidth: (d) => d.id === selectedPaper?.id ? 1.5 : 0,
      lineWidthUnits: 'pixels',
      onHover: ({ object, x, y }) => setHover(object ? { paper: object, x, y } : null),
      onClick: ({ object }) => object && onSelect(object),
      updateTriggers: {
        getFillColor: [mode],
        getRadius: [selectedPaper?.id],
        getLineWidth: [selectedPaper?.id],
      },
    }),
    new TextLayer<Cluster>({
      id: 'cluster-labels',
      data: clusters,
      getPosition: (d) => [d.x, d.y],
      getText: (d) => d.name.toUpperCase(),
      getColor: [206, 220, 237, 145],
      getSize: 11,
      sizeUnits: 'pixels',
      getTextAnchor: 'middle',
      getAlignmentBaseline: 'center',
      fontFamily: 'Inter, system-ui, sans-serif',
      fontWeight: 600,
      background: true,
      getBackgroundColor: [8, 11, 16, 170],
      backgroundPadding: [6, 4],
      billboard: true,
      pickable: false,
    }),
  ], [papers, clusters, mode, selectedPaper, onSelect])

  const zoom = (delta: number) => setViewState((state) => ({ ...state, zoom: Math.min(5, Math.max(-0.5, state.zoom + delta)) }))

  return (
    <div className="constellation" aria-label={`Interactive semantic map showing ${papers.length} papers`}>
      <div className="map-kicker"><Sparkles size={13} /> Semantic paper landscape</div>
      <DeckGL
        views={new OrthographicView({ id: 'ortho', flipY: false })}
        viewState={viewState}
        onViewStateChange={({ viewState: next }) => setViewState(next as typeof viewState)}
        controller={{ dragPan: true, scrollZoom: true, doubleClickZoom: true, touchZoom: true, keyboard: true }}
        layers={layers}
        style={{ position: 'absolute', inset: '0' }}
      />
      <div className="map-grid" aria-hidden="true" />
      <div className="map-controls" aria-label="Map controls">
        <button onClick={() => zoom(0.4)} aria-label="Zoom in"><Plus size={16} /></button>
        <button onClick={() => zoom(-0.4)} aria-label="Zoom out"><Minus size={16} /></button>
        <button onClick={() => setViewState({ ...INITIAL_VIEW })} aria-label="Reset map view"><Scan size={16} /></button>
      </div>
      <div className="map-help">Scroll to zoom · drag to pan · select a point to inspect</div>
      {hover && (
        <div className="map-tooltip" style={{ left: Math.min(hover.x + 14, 480), top: Math.max(hover.y - 10, 12) }}>
          <span>{hover.paper.year} · {hover.paper.domain}</span>
          <strong>{truncate(hover.paper.title, 78)}</strong>
          <small>{hover.paper.aiMethod} · {hover.paper.aiRole}</small>
        </div>
      )}
    </div>
  )
}
