export type ColorMode = 'domain' | 'method' | 'role' | 'physics' | 'year' | 'confidence'

export interface Paper {
  id: string
  title: string
  abstract: string
  year: number
  authors: string[]
  domain: string
  aiMethod: string
  aiRole: string
  physicsIntegration: string
  confidence: number
  evidence: string
  x: number
  y: number
  cluster: string
  url: string
  demo: boolean
}

export interface Cluster {
  name: string
  x: number
  y: number
}

export interface Summary {
  demo: boolean
  generatedAt: string
  paperCount: number
  yearRange: [number, number]
}

export interface Filters {
  search: string
  yearMin: number
  yearMax: number
  domains: string[]
  methods: string[]
  roles: string[]
  physics: string[]
}
