import type { AppSettings } from './types'

export const defaultSettings: AppSettings = {
  feed: {
    enabledSourceIds: [],
    enabledCategoryIds: [],
    maxArticlesPerPage: 6,
  },
  model: {
    provider: 'Gemini',
    apiKey: '',
    modelName: 'gemini-2.5-flash',
    temperature: 0.3,
    maxSummarySentences: 4,
  },
  layout: {
    density: 'balanced',
    showImages: true,
  },
  ui: {
    theme: 'newsprint',
    demoMode: 'live',
  },
}
