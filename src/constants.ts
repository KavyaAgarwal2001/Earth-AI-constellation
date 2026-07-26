import type { ColorMode } from './types'

export const DOMAINS = [
  'Weather and climate',
  'Oceans and coasts',
  'Earth observation and remote sensing',
  'Solid Earth and geophysics',
  'Planetary science',
]

export const METHODS = [
  'Classical statistical models',
  'Random forests and tree models',
  'Support vector machines',
  'CNNs',
  'Recurrent networks',
  'Transformers',
  'Graph neural networks',
  'Physics-informed neural networks',
  'Neural operators',
  'Foundation models',
  'Reinforcement learning',
  'Large language models',
  'Method unclear',
  'AI discussed but not implemented',
]

export const ROLES = [
  'Detection',
  'Classification',
  'Segmentation',
  'Estimation',
  'Forecasting',
  'Inverse modeling',
  'Simulator emulation',
  'Data assimilation',
  'Control and optimization',
  'Scientific discovery',
  'Workflow automation',
  'Role unclear',
]

export const PHYSICS = [
  'Purely data-driven',
  'Physical variables used as inputs',
  'Physical consistency evaluated',
  'Physics included in the loss',
  'Physics encoded in the architecture',
  'Coupled with a simulator',
  'Emulator of a simulator',
  'Physics relationship unclear',
]

export const MODE_LABELS: Record<ColorMode, string> = {
  domain: 'Scientific domain',
  method: 'AI method',
  role: 'Scientific role',
  physics: 'Physics integration',
  year: 'Publication year',
  confidence: 'Classification confidence',
}

export const PALETTES = {
  domain: ['#6ce5b1', '#55b8ff', '#ffbd66', '#ff7892', '#ad8cff'],
  method: ['#6ce5b1', '#ffbd66', '#58b8ff', '#fa7f72', '#ca92ff', '#71d4d2', '#ff8fbd', '#b8d86a', '#e6a2ff', '#7fb7ff', '#ff9f5c', '#a3b0c4', '#778195', '#525d70'],
  role: ['#6ce5b1', '#55b8ff', '#ffbd66', '#ff7892', '#ad8cff', '#71d4d2', '#ff8fbd', '#b8d86a', '#e5a45a', '#8ca8ff', '#c2d3e8', '#687487'],
  physics: ['#55b8ff', '#6ce5b1', '#b8d86a', '#ffbd66', '#ff7892', '#ad8cff', '#71d4d2', '#687487'],
}
