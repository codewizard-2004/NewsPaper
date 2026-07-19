import type { AppSettings } from './types'

export const defaultSettings: AppSettings = {
  feed: {
    enabledSourceIds: [],
    enabledCategoryIds: [],
    maxArticlesPerPage: 6,
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
