/**
 * Application constants and configuration
 */

import { Model, ColorTheme } from '@/types'

export const AVAILABLE_MODELS: Model[] = [
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Fast & efficient' },
  { id: 'gpt-4o', name: 'GPT-4o', description: 'Most capable' },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Classic choice' }
]

export const AVAILABLE_COLORS: ColorTheme[] = [
  { id: 'blue', name: 'Blue', description: 'Professional' },
  { id: 'teal', name: 'Teal', description: 'Modern' },
  { id: 'purple', name: 'Purple', description: 'Creative' },
  { id: 'indigo', name: 'Indigo', description: 'Elegant' },
  { id: 'rose', name: 'Rose', description: 'Warm' },
  { id: 'orange', name: 'Orange', description: 'Energetic' },
  { id: 'amber', name: 'Amber', description: 'Inviting' },
  { id: 'cyan', name: 'Cyan', description: 'Fresh' },
  { id: 'stone', name: 'Stone', description: 'Neutral' },
  { id: 'violet', name: 'Violet', description: 'Modern' },
  { id: 'red', name: 'Red', description: 'Bold' },
  { id: 'emerald', name: 'Emerald', description: 'Natural' }
]

export const DEFAULT_MODEL = 'gpt-4o-mini'
export const DEFAULT_COLOR = 'emerald'

// LocalStorage keys
export const STORAGE_KEYS = {
  MODEL: 'ragchat-model',
  COLOR: 'ragchat-color'
} as const

// Upload limits
export const MAX_PDF_MB = Number(process.env.NEXT_PUBLIC_MAX_PDF_MB ?? '4.5')
