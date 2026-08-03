import type { ArticleImportance, ArticleStory, CategoryRecord, DummyEdition, EditionPage, PageTemplate, SourceRecord } from './types'

export interface ArticleItemDoc {
  id: string
  type: 'article'
  headline: string
  body: string
  sources?: string[]
  confidence_rating?: number
  importance_rating?: number
  image_url?: string | null
}

export interface DsaItemDoc {
  id: string
  type: 'dsa_question'
  prompt: string
  difficulty?: string
}

export interface ComicItemDoc {
  id: string
  type: 'comic'
  image_url?: string | null
  caption?: string
}

export type ItemDoc = ArticleItemDoc | DsaItemDoc | ComicItemDoc

export interface IssueSectionDoc {
  name: string
  items?: ItemDoc[]
}

export interface IssueDoc {
  date?: string
  sections?: IssueSectionDoc[]
}

const PAGE_TEMPLATES: Record<string, PageTemplate> = {
  'Front page': 'front',
  'AI/ML': 'three-column',
  Security: 'three-column',
  Misc: 'stack',
}

const PAGE_TITLES: Record<string, string> = {
  'Front page': 'Front page',
  'AI/ML': 'AI & Machine Learning',
  Security: 'Security',
  Misc: 'Miscellany',
}

const SOURCE_HOMEPAGES: Record<string, string> = {
  'hacker news': 'https://news.ycombinator.com',
  reddit: 'https://www.reddit.com',
  'dev.to': 'https://dev.to',
  github: 'https://github.com',
  techcrunch: 'https://techcrunch.com',
  'the verge': 'https://www.theverge.com',
}

const slugify = (value: string): string =>
  value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'unknown'

const importanceFromRating = (rating: number): ArticleImportance => {
  if (rating >= 8) return 5
  if (rating >= 6) return 4
  if (rating >= 4) return 3
  if (rating >= 2) return 2
  return 1
}

function paragraphize(body: string): string[] {
  const blocks = body
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean)
  if (blocks.length > 1) {
    return blocks
  }

  const text = blocks[0] ?? body
  const sentences = text.split(/(?<=[.!?])\s+/).filter(Boolean)
  const paragraphs: string[] = []
  for (let index = 0; index < sentences.length; index += 3) {
    paragraphs.push(sentences.slice(index, index + 3).join(' '))
  }
  return paragraphs.length > 0 ? paragraphs : [text]
}

const subtitleFrom = (body: string): string => {
  const first = paragraphize(body)[0] ?? body
  return first.length > 200 ? `${first.slice(0, 197).trimEnd()}…` : first
}

const readTimeOf = (body: string): number => {
  const words = body.trim().split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.round(words / 180))
}

function ensureSource(sourcesMap: Map<string, SourceRecord>, name: string): string {
  const id = slugify(name)
  if (!sourcesMap.has(id)) {
    sourcesMap.set(id, { id, name, url: SOURCE_HOMEPAGES[name.toLowerCase()] ?? '#' })
  }
  return id
}

function mapItemToStory(
  item: ItemDoc,
  sectionName: string,
  page: number,
  issueDate: string,
  sourcesMap: Map<string, SourceRecord>,
): ArticleStory | null {
  const publishedAt = `${issueDate}T06:30:00Z`

  if (item.type === 'dsa_question') {
    return {
      id: item.id,
      page,
      category: 'Daily DSA',
      importance: 1,
      title: 'Daily DSA Question',
      subtitle: item.difficulty ? `Difficulty: ${item.difficulty}` : 'Daily practice',
      kicker: 'Daily DSA',
      authors: [{ name: 'Gazette Desk', aiGenerated: true }],
      content: paragraphize(item.prompt),
      sourceIds: [],
      sources: [],
      images: [],
      layoutHint: 'brief',
      publishedAt,
    }
  }

  if (item.type === 'comic') {
    return {
      id: item.id,
      page,
      category: 'Comic',
      importance: 1,
      title: "Today's Comic",
      subtitle: item.caption || 'The continuing strip',
      kicker: 'Comic',
      authors: [{ name: 'The Inkwell', aiGenerated: true }],
      content: item.caption ? paragraphize(item.caption) : [],
      sourceIds: [],
      sources: [],
      images: item.image_url ? [{ src: item.image_url, alt: 'Comic strip' }] : [],
      layoutHint: 'brief',
      publishedAt,
    }
  }

  const headline = item.headline || 'Untitled story'
  const body = item.body || ''
  const sourceNames = Array.isArray(item.sources)
    ? item.sources.filter((name): name is string => typeof name === 'string')
    : []
  const sourceIds = sourceNames.map((name) => ensureSource(sourcesMap, name))
  const images = item.image_url ? [{ src: item.image_url, alt: headline }] : []

  return {
    id: item.id,
    page,
    category: sectionName,
    importance: importanceFromRating(Number(item.importance_rating) || 0),
    title: headline,
    subtitle: subtitleFrom(body),
    kicker: sectionName,
    authors: [{ name: 'Gazette Desk', role: 'Reporter', aiGenerated: true }],
    content: paragraphize(body),
    sourceIds,
    sources: sourceIds.map((id) => sourcesMap.get(id)!),
    images,
    readTimeMin: readTimeOf(body),
    publishedAt,
  }
}

function dateStats(date: string) {
  const [year, month, day] = date.split('-').map(Number)
  const startOfYear = Date.UTC(year, 0, 1)
  const today = Date.UTC(year, month - 1, day)
  const dayOfYear = Math.floor((today - startOfYear) / 86400000) + 1
  return { year, dayOfYear }
}

export function transformIssue(doc: unknown, fallbackDate: string): DummyEdition | null {
  if (!doc || typeof doc !== 'object') {
    return null
  }

  const issue = doc as IssueDoc
  const sections = issue.sections
  if (!Array.isArray(sections)) {
    return null
  }

  const issueDate = typeof issue.date === 'string' && issue.date ? issue.date : fallbackDate
  const categories: CategoryRecord[] = []
  const seenCategories = new Set<string>()
  const sourcesMap = new Map<string, SourceRecord>()
  const pages: EditionPage[] = []
  let pageNumber = 1

  for (const section of sections) {
    const sectionName = typeof section?.name === 'string' && section.name ? section.name : 'Misc'
    const items = Array.isArray(section?.items) ? section.items : []
    if (items.length === 0) {
      continue
    }

    const articles: ArticleStory[] = []
    for (const item of items) {
      if (!item || typeof item !== 'object') {
        continue
      }
      const story = mapItemToStory(item, sectionName, pageNumber, issueDate, sourcesMap)
      if (story) {
        articles.push(story)
      }
    }
    if (articles.length === 0) {
      continue
    }

    for (const story of articles) {
      const categoryId = slugify(story.category)
      if (!seenCategories.has(categoryId)) {
        seenCategories.add(categoryId)
        categories.push({ id: categoryId, title: story.category })
      }
    }

    pages.push({
      page: pageNumber,
      template: PAGE_TEMPLATES[sectionName] ?? 'stack',
      title: PAGE_TITLES[sectionName] ?? sectionName,
      articles,
    })
    pageNumber += 1
  }

  if (pages.length === 0) {
    return null
  }

  const { year, dayOfYear } = dateStats(issueDate)
  return {
    title: 'The Kernel Gazette',
    subtitle: 'Curated signal, zero noise.',
    volume: Math.max(1, year - 2026 + 1),
    issue: dayOfYear,
    issueDate,
    pages,
    sources: [...sourcesMap.values()],
    categories,
  }
}
