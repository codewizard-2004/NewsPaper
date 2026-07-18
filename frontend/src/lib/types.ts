export type ArticleImportance = 1 | 2 | 3 | 4 | 5

export type PageTemplate = 'front' | 'split' | 'three-column' | 'longform' | 'stack'

export interface SourceRecord {
  id: string
  name: string
  url: string
  description?: string
}

export interface CategoryRecord {
  id: string
  title: string
  description?: string
}

export interface ArticleImage {
  src: string
  alt: string
  caption?: string
  credit?: string
  aspect?: 'landscape' | 'portrait' | 'square'
}

export interface ArticleAuthor {
  name: string
  role?: string
  aiGenerated?: boolean
}

export interface ArticleSource {
  name: string
  url: string
  note?: string
}

export interface ArticleStory {
  id: string
  page: number
  category: string
  importance: ArticleImportance
  title: string
  subtitle: string
  kicker?: string
  authors: ArticleAuthor[]
  content: string[]
  sourceIds: string[]
  sources: ArticleSource[]
  images: ArticleImage[]
  tags?: string[]
  publishedAt: string
  readTimeMin?: number
  layoutHint?: 'hero' | 'feature' | 'brief'
}

export interface EditionPage {
  page: number
  template: PageTemplate
  title: string
  deck?: string
  articles: ArticleStory[]
}

export interface DummyEdition {
  title: string
  subtitle: string
  volume: number
  issue: number
  issueDate: string
  pages: EditionPage[]
  sources: SourceRecord[]
  categories: CategoryRecord[]
}

export interface UserFeedSettings {
  enabledSourceIds: string[]
  enabledCategoryIds: string[]
  maxArticlesPerPage: number
}

export interface UserLayoutSettings {
  density: 'compact' | 'balanced' | 'generous'
  showImages: boolean
}

export interface UserModelSettings {
  provider: 'Gemini' | 'OpenAI' | 'Ollama Cloud'
  apiKey: string
  modelName: string
  temperature: number
  maxSummarySentences: number
}

export interface UserInterfaceSettings {
  theme: 'newsprint' | 'night'
  demoMode: 'live' | 'loading' | 'empty' | 'error'
}

export interface AppSettings {
  feed: UserFeedSettings
  model: UserModelSettings
  layout: UserLayoutSettings
  ui: UserInterfaceSettings
}

export interface AuthState {
  signedIn: boolean
  name: string
  email: string
}
