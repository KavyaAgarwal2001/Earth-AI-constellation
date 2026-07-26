import { DOMAINS, METHODS, MODE_LABELS, PALETTES, PHYSICS, ROLES } from '../constants'
import type { ColorMode } from '../types'

const categorical = {
  domain: [DOMAINS, PALETTES.domain],
  method: [METHODS, PALETTES.method],
  role: [ROLES, PALETTES.role],
  physics: [PHYSICS, PALETTES.physics],
} as const

export function Legend({ mode }: { mode: ColorMode }) {
  if (mode === 'year' || mode === 'confidence') {
    return (
      <div className="continuous-legend">
        <span>{mode === 'year' ? '2015' : 'Lower confidence'}</span>
        <i className={mode} />
        <span>{mode === 'year' ? '2026' : 'Higher confidence'}</span>
      </div>
    )
  }
  const [labels, colors] = categorical[mode]
  return (
    <div className="legend" aria-label={`${MODE_LABELS[mode]} legend`}>
      {labels.map((label, index) => (
        <span key={label}><i style={{ background: colors[index] }} />{label}</span>
      ))}
    </div>
  )
}
