import { DOMAINS, METHODS, PALETTES, PHYSICS, ROLES } from './constants'
import type { ColorMode, Paper } from './types'

export type RGB = [number, number, number]

export const hexToRgb = (hex: string): RGB => {
  const value = Number.parseInt(hex.slice(1), 16)
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255]
}

export const colorForPaper = (paper: Paper, mode: ColorMode): RGB => {
  if (mode === 'year') {
    const t = Math.max(0, Math.min(1, (paper.year - 2015) / 11))
    return [Math.round(79 + 164 * t), Math.round(133 + 84 * t), Math.round(192 - 105 * t)]
  }
  if (mode === 'confidence') {
    const t = Math.max(0, Math.min(1, (paper.confidence - 0.45) / 0.55))
    return [Math.round(242 - 134 * t), Math.round(127 + 98 * t), Math.round(122 + 46 * t)]
  }
  const config = {
    domain: [DOMAINS, PALETTES.domain],
    method: [METHODS, PALETTES.method],
    role: [ROLES, PALETTES.role],
    physics: [PHYSICS, PALETTES.physics],
  } as const
  const [labels, colors] = config[mode]
  const key = mode === 'domain' ? paper.domain : mode === 'method' ? paper.aiMethod : mode === 'role' ? paper.aiRole : paper.physicsIntegration
  return hexToRgb(colors[Math.max(0, labels.indexOf(key)) % colors.length])
}

export const percent = (part: number, total: number) => total ? `${Math.round((part / total) * 100)}%` : '0%'

export const truncate = (text: string, limit: number) => text.length > limit ? `${text.slice(0, limit).trim()}…` : text
