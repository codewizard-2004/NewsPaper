import { useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import { defaultSettings } from '@/lib/settings'
import { removeStorageItem, usePersistentState } from '@/lib/storage'
import type {
  AppSettings,
  ArticleImportance,
  ArticleStory,
  AuthState,
  DummyEdition,
  EditionPage,
  UserFeedSettings,
  UserLayoutSettings,
} from '@/lib/types'
import './App.css'

const STORAGE_SETTINGS_KEY = 'daily-dispatch-settings'
const STORAGE_AUTH_KEY = 'daily-dispatch-auth'

const DEFAULT_AUTH: AuthState = {
  signedIn: false,
  name: 'Nora Patel',
  email: 'nora@dailydispatch.dev',
}

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value))

const formatIssueDate = (value: string) =>
  new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(value))

const formatPageLabel = (page: number) => `A${String(page).padStart(2, '0')}`

const importanceLabel: Record<ArticleImportance, string> = {
  1: 'brief',
  2: 'short',
  3: 'regular',
  4: 'major',
  5: 'front',
}

function App() {
  const [settings, setSettings] = usePersistentState<AppSettings>(
    STORAGE_SETTINGS_KEY,
    defaultSettings,
  )
  const [auth, setAuth] = usePersistentState<AuthState>(STORAGE_AUTH_KEY, DEFAULT_AUTH)
  const [screen, setScreen] = useState<'paper' | 'settings'>('paper')
  const [edition, setEdition] = useState<DummyEdition | null>(null)
  const [loadState, setLoadState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [loadError, setLoadError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState(0)
  const [pageIndex, setPageIndex] = useState(0)
  const [selectedArticle, setSelectedArticle] = useState<ArticleStory | null>(null)
  const closeButtonRef = useRef<HTMLButtonElement | null>(null)
  const lastTriggerRef = useRef<HTMLElement | null>(null)
  const hydratedSettingsRef = useRef(false)

  useEffect(() => {
    let active = true

    fetch('/dummy.json', { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Unable to load dummy edition (${response.status})`)
        }

        return response.json() as Promise<DummyEdition>
      })
      .then((data) => {
        if (!active) {
          return
        }

        setEdition(data)
        setLoadState('ready')
      })
      .catch((error: unknown) => {
        if (!active) {
          return
        }

        setLoadState('error')
        setLoadError(error instanceof Error ? error.message : 'Unable to load the edition.')
      })

    return () => {
      active = false
    }
  }, [reloadToken])

  useEffect(() => {
    if (!edition || hydratedSettingsRef.current) {
      return
    }

    hydratedSettingsRef.current = true
    setSettings((current) => normalizeSettings(current, edition))
  }, [edition, setSettings])

  const pages = useMemo(() => {
    if (!edition) {
      return []
    }

    return edition.pages.map((page) => ({
      ...page,
      articles: page.articles
        .filter((article) => settings.feed.enabledCategoryIds.includes(article.category))
        .filter((article) =>
          article.sourceIds.some((sourceId) => settings.feed.enabledSourceIds.includes(sourceId)),
        )
        .slice(0, settings.feed.maxArticlesPerPage),
    }))
  }, [
    edition,
    settings.feed.enabledCategoryIds,
    settings.feed.enabledSourceIds,
    settings.feed.maxArticlesPerPage,
  ])

  const safePageIndex = pages.length === 0 ? 0 : clamp(pageIndex, 0, pages.length - 1)
  const currentPage = pages[safePageIndex] ?? null

  const openArticle = (article: ArticleStory, sourceElement?: HTMLElement | null) => {
    lastTriggerRef.current = sourceElement ?? null
    setSelectedArticle(article)
  }

  const closeArticle = () => {
    setSelectedArticle(null)
    window.requestAnimationFrame(() => {
      lastTriggerRef.current?.focus()
      lastTriggerRef.current = null
    })
  }

  useEffect(() => {
    if (!selectedArticle) {
      return undefined
    }

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      const isTextInput =
        target?.tagName === 'INPUT' ||
        target?.tagName === 'TEXTAREA' ||
        target?.isContentEditable === true

      if (isTextInput) {
        return
      }

      if (event.key === 'Escape') {
        closeArticle()
      }
    }

    window.addEventListener('keydown', handleKeyDown as unknown as EventListener)
    return () => window.removeEventListener('keydown', handleKeyDown as unknown as EventListener)
  }, [selectedArticle])

  useEffect(() => {
    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      const isTextInput =
        target?.tagName === 'INPUT' ||
        target?.tagName === 'TEXTAREA' ||
        target?.isContentEditable === true

      if (isTextInput) {
        return
      }

      if (event.key === 'Escape' && screen === 'settings') {
        setScreen('paper')
        return
      }

      if (screen !== 'paper' || selectedArticle) {
        return
      }

      if (event.key === 'ArrowLeft') {
        setPageIndex((current) => clamp(current - 1, 0, Math.max(pages.length - 1, 0)))
      }

      if (event.key === 'ArrowRight') {
        setPageIndex((current) => clamp(current + 1, 0, Math.max(pages.length - 1, 0)))
      }
    }

    window.addEventListener('keydown', handleKeyDown as unknown as EventListener)
    return () => window.removeEventListener('keydown', handleKeyDown as unknown as EventListener)
  }, [pages.length, screen, selectedArticle])

  useEffect(() => {
    if (selectedArticle && closeButtonRef.current) {
      closeButtonRef.current.focus()
    }
  }, [selectedArticle])

  const updateFeed = (patch: Partial<UserFeedSettings>) => {
    setSettings((current) => ({
      ...current,
      feed: {
        ...current.feed,
        ...patch,
      },
    }))
  }

  const updateModel = (patch: Partial<AppSettings['model']>) => {
    setSettings((current) => ({
      ...current,
      model: {
        ...current.model,
        ...patch,
      },
    }))
  }

  const updateLayout = (patch: Partial<UserLayoutSettings>) => {
    setSettings((current) => ({
      ...current,
      layout: {
        ...current.layout,
        ...patch,
      },
    }))
  }

  const toggleSource = (sourceId: string) => {
    setSettings((current) => {
      const enabled = current.feed.enabledSourceIds.includes(sourceId)
      return {
        ...current,
        feed: {
          ...current.feed,
          enabledSourceIds: enabled
            ? current.feed.enabledSourceIds.filter((item) => item !== sourceId)
            : [...current.feed.enabledSourceIds, sourceId],
        },
      }
    })
  }

  const toggleCategory = (categoryId: string) => {
    setSettings((current) => {
      const enabled = current.feed.enabledCategoryIds.includes(categoryId)
      return {
        ...current,
        feed: {
          ...current.feed,
          enabledCategoryIds: enabled
            ? current.feed.enabledCategoryIds.filter((item) => item !== categoryId)
            : [...current.feed.enabledCategoryIds, categoryId],
        },
      }
    })
  }

  const resetDemo = () => {
    if (edition) {
      setSettings(normalizeSettings(defaultSettings, edition))
    } else {
      setSettings(defaultSettings)
    }

    removeStorageItem(STORAGE_SETTINGS_KEY)
    setPageIndex(0)
    setSelectedArticle(null)
    setScreen('paper')
  }

  const retryLoad = () => {
    hydratedSettingsRef.current = false
    setEdition(null)
    setLoadState('loading')
    setLoadError(null)
    setReloadToken((current) => current + 1)
  }

  if (loadState === 'loading') {
    return <BootScreen />
  }

  if (loadState === 'error') {
    return (
      <StateScreen
        title="The presses stalled"
        description={loadError ?? 'The dummy edition could not be loaded.'}
        actionLabel="Try again"
        onAction={retryLoad}
      />
    )
  }

  if (!auth.signedIn) {
    return (
      <AuthScreen
        onSignIn={() =>
          setAuth({
            signedIn: true,
            name: 'Nora Patel',
            email: 'nora@dailydispatch.dev',
          })
        }
      />
    )
  }

  if (!edition) {
    return (
      <StateScreen
        title="No edition loaded"
        description="The dummy edition is missing. Reload the page to try again."
        actionLabel="Reload"
        onAction={() => window.location.reload()}
      />
    )
  }

  if (screen === 'settings') {
    return (
      <SettingsScreen
        edition={edition}
        settings={settings}
        onBack={() => setScreen('paper')}
        onToggleSource={toggleSource}
        onToggleCategory={toggleCategory}
        onUpdateFeed={updateFeed}
        onUpdateModel={updateModel}
        onUpdateLayout={updateLayout}
        onReset={resetDemo}
      />
    )
  }

  const visibleContentCount = pages.reduce((sum, page) => sum + page.articles.length, 0)
  if (visibleContentCount === 0) {
    return (
      <StateScreen
        title="No stories match the current paper"
        description="Open settings and re-enable sources or categories to bring the edition back."
        actionLabel="Open settings"
        onAction={() => setScreen('settings')}
      />
    )
  }

  const pageLabel = currentPage ? formatPageLabel(currentPage.page) : 'A01'

  return (
    <div className="app-shell">
      <header className="masthead">
        {/* Top rule */}
        <div className="masthead-rule masthead-rule--top" aria-hidden="true" />

        {/* Title row: flanking boxes + big title */}
        <div className="masthead-title-row">
          <div className="masthead-flank masthead-flank--left">
            <p className="masthead-flank-motto">&ldquo;Curated signal,<br />zero noise.&rdquo;</p>
            <span className="masthead-flank-attr">The news that matters, sourced and verified</span>
          </div>

          <div className="masthead-nameplate">
            <h1>{edition.title}</h1>
          </div>

          <div className="masthead-flank masthead-flank--right">
            <span className="masthead-flank-label">Page</span>
            <strong className="masthead-flank-value">{pageLabel}</strong>
            <span className="masthead-flank-label">{formatIssueDate(edition.issueDate)}</span>
          </div>
        </div>

        {/* Thin double rule */}
        <div className="masthead-rule" aria-hidden="true" />

        {/* Bottom meta strip with settings */}
        <div className="masthead-subline">
          <span>Vol.&nbsp;{edition.volume} &middot; No.&nbsp;{edition.issue}</span>
          <span className="masthead-subline-motto">All the signal that&rsquo;s fit to read</span>
          <button type="button" className="masthead-link" onClick={() => setScreen('settings')}>
            ⚙ Settings
          </button>
        </div>
      </header>

      <main className="paper-frame">
        <div className="press-nav">
          <button
            type="button"
            className="page-arrow"
            onClick={() => setPageIndex((current) => clamp(current - 1, 0, pages.length - 1))}
            disabled={safePageIndex === 0}
            aria-label="Previous page"
          >
            ←
          </button>

          <div className="press-nav-label">
            <small>{currentPage?.title ?? 'Empty page'}</small>
            <span>{pageLabel}</span>
          </div>

          <button
            type="button"
            className="page-arrow"
            onClick={() => setPageIndex((current) => clamp(current + 1, 0, pages.length - 1))}
            disabled={safePageIndex === pages.length - 1}
            aria-label="Next page"
          >
            →
          </button>
        </div>

        <section className="paper-page" aria-label={`Page ${pageLabel}`}>
          {currentPage ? (
            <PaperPage
              page={currentPage}
              settings={settings}
              onOpenArticle={openArticle}
            />
          ) : (
            <div className="page-empty">
              <p className="front-kicker">Paper state</p>
              <h2>No stories available</h2>
              <p>Adjust filters in settings to bring stories back onto the page.</p>
            </div>
          )}
        </section>

        <div className="paper-footer">
          <span>Use the left and right arrows to move through the paper.</span>
        </div>
      </main>

      {selectedArticle ? (
        <ReadingModal
          article={selectedArticle}
          onClose={closeArticle}
          closeRef={closeButtonRef}
        />
      ) : null}
    </div>
  )
}

function normalizeSettings(settings: AppSettings, edition: DummyEdition): AppSettings {
  const sourceIds = edition.sources.map((source) => source.id)
  const categoryIds = edition.categories.map((category) => category.id)
  const legacySources = (settings.feed as unknown as Record<string, unknown>).enabledSources
  const legacyCategories = (settings.feed as unknown as Record<string, unknown>).enabledSections

  let enabledSourceIds = settings.feed.enabledSourceIds.filter((sourceId) =>
    sourceIds.includes(sourceId),
  )
  if (enabledSourceIds.length === 0 && legacySources && typeof legacySources === 'object') {
    enabledSourceIds = Object.entries(legacySources as Record<string, boolean>)
      .filter(([, enabled]) => enabled)
      .map(([sourceId]) => sourceId)
      .filter((sourceId) => sourceIds.includes(sourceId))
  }
  if (enabledSourceIds.length === 0) {
    enabledSourceIds = [...sourceIds]
  }

  let enabledCategoryIds = settings.feed.enabledCategoryIds.filter((categoryId) =>
    categoryIds.includes(categoryId),
  )
  if (enabledCategoryIds.length === 0 && Array.isArray(legacyCategories)) {
    enabledCategoryIds = legacyCategories.filter((categoryId) => categoryIds.includes(categoryId))
  }
  if (enabledCategoryIds.length === 0) {
    enabledCategoryIds = [...categoryIds]
  }

  return {
    ...settings,
    feed: {
      ...settings.feed,
      enabledSourceIds,
      enabledCategoryIds,
      maxArticlesPerPage: clamp(settings.feed.maxArticlesPerPage, 1, 12),
    },
  }
}

function PaperPage({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  switch (page.template) {
    case 'front':
      return (
        <FrontLayout page={page} settings={settings} onOpenArticle={onOpenArticle} />
      )
    case 'split':
      return <SplitLayout page={page} settings={settings} onOpenArticle={onOpenArticle} />
    case 'three-column':
      return (
        <ThreeColumnLayout page={page} settings={settings} onOpenArticle={onOpenArticle} />
      )
    case 'longform':
      return <LongformLayout page={page} settings={settings} onOpenArticle={onOpenArticle} />
    case 'stack':
    default:
      return <StackLayout page={page} settings={settings} onOpenArticle={onOpenArticle} />
  }
}


function getBroadsheetSpan(article: ArticleStory, isTopRow = false): string {
  if (article.importance === 5) {
    return isTopRow ? 'col-span-4' : 'col-span-3'
  }
  if (article.importance === 4) {
    return 'col-span-2'
  }
  if (article.importance === 3) {
    return 'col-span-1'
  }
  return 'col-span-1'
}

function FrontLayout({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  const [lead, ...rest] = page.articles

  return (
    <div className={`page-layout page-template-front density-${settings.layout.density}`}>
      {lead ? (
        <div className="newspaper-banner-hero">
          <ArticleCard
            article={lead}
            size="hero"
            showImages={settings.layout.showImages}
            onOpenArticle={onOpenArticle}
          />
        </div>
      ) : null}

      {rest.length > 0 && lead ? <hr className="newspaper-divider" /> : null}

      {rest.length > 0 ? (
        <div className="broadsheet-grid broadsheet-grid--4">
          {rest.map((article, index) => (
            <div
              key={article.id}
              className={`broadsheet-cell ${getBroadsheetSpan(article, index === 0 && article.importance === 5)}`}
            >
              <ArticleCard
                article={article}
                size={article.importance >= 5 ? 'hero' : article.importance === 4 ? 'major' : article.importance === 3 ? 'regular' : article.importance === 2 ? 'compact' : 'brief'}
                showImages={settings.layout.showImages}
                onOpenArticle={onOpenArticle}
              />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function SplitLayout({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  const [lead, ...rest] = page.articles
  const hasBannerLead = lead && lead.importance >= 5

  return (
    <div className={`page-layout page-template-split density-${settings.layout.density}`}>
      {hasBannerLead ? (
        <div className="newspaper-banner-hero">
          <ArticleCard
            article={lead}
            size="hero"
            showImages={settings.layout.showImages}
            onOpenArticle={onOpenArticle}
          />
        </div>
      ) : null}

      {hasBannerLead && rest.length > 0 ? <hr className="newspaper-divider" /> : null}

      <div className="broadsheet-grid broadsheet-grid--4">
        {(hasBannerLead ? rest : page.articles).map((article) => (
          <div key={article.id} className={`broadsheet-cell ${getBroadsheetSpan(article)}`}>
            <ArticleCard
              article={article}
              size={article.importance >= 5 ? 'hero' : article.importance === 4 ? 'major' : article.importance === 3 ? 'regular' : article.importance === 2 ? 'compact' : 'brief'}
              showImages={settings.layout.showImages}
              onOpenArticle={onOpenArticle}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

function ThreeColumnLayout({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  return (
    <div className={`page-layout page-template-three density-${settings.layout.density}`}>
      <div className="broadsheet-grid broadsheet-grid--4">
        {page.articles.map((article) => (
          <div key={article.id} className={`broadsheet-cell ${getBroadsheetSpan(article)}`}>
            <ArticleCard
              article={article}
              size={article.importance >= 5 ? 'hero' : article.importance === 4 ? 'major' : article.importance === 3 ? 'regular' : article.importance === 2 ? 'compact' : 'brief'}
              showImages={settings.layout.showImages}
              onOpenArticle={onOpenArticle}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

function LongformLayout({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  const [lead, ...rest] = page.articles

  return (
    <div className={`page-layout page-template-longform density-${settings.layout.density}`}>
      {lead ? (
        <div className="newspaper-banner-hero">
          <ArticleCard
            article={lead}
            size="hero"
            showImages={settings.layout.showImages}
            onOpenArticle={onOpenArticle}
          />
        </div>
      ) : null}

      {rest.length > 0 && lead ? <hr className="newspaper-divider" /> : null}

      {rest.length > 0 ? (
        <div className="broadsheet-grid broadsheet-grid--4">
          {rest.map((article) => (
            <div key={article.id} className={`broadsheet-cell ${getBroadsheetSpan(article)}`}>
              <ArticleCard
                article={article}
                size={article.importance >= 5 ? 'hero' : article.importance === 4 ? 'major' : article.importance === 3 ? 'regular' : article.importance === 2 ? 'compact' : 'brief'}
                showImages={settings.layout.showImages}
                onOpenArticle={onOpenArticle}
              />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function StackLayout({
  page,
  settings,
  onOpenArticle,
}: {
  page: EditionPage
  settings: AppSettings
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  return (
    <div className={`page-layout page-template-stack density-${settings.layout.density}`}>
      <div className="broadsheet-grid broadsheet-grid--4">
        {page.articles.map((article) => (
          <div key={article.id} className={`broadsheet-cell ${getBroadsheetSpan(article)}`}>
            <ArticleCard
              article={article}
              size={article.importance >= 5 ? 'hero' : article.importance === 4 ? 'major' : article.importance === 3 ? 'regular' : article.importance === 2 ? 'compact' : 'brief'}
              showImages={settings.layout.showImages}
              onOpenArticle={onOpenArticle}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

function ArticleCard({
  article,
  size,
  showImages,
  onOpenArticle,
}: {
  article: ArticleStory
  size: 'hero' | 'major' | 'regular' | 'compact' | 'brief'
  showImages: boolean
  onOpenArticle: (article: ArticleStory, sourceElement?: HTMLElement | null) => void
}) {
  const image = article.images[0]
  const readTime = article.readTimeMin ?? estimateReadTime(article)
  const authors = article.authors.map((author) => author.name).join(' · ')
  const sourceNames = article.sources.map((source) => source.name).join(' · ')
  const hasMedia = Boolean(showImages && image && article.importance > 1)

  return (
    <article
      className={`article-card article-card--${size} article-card--importance-${article.importance} ${hasMedia ? 'article-card--has-media' : 'article-card--text-only'}`}
      role="button"
      tabIndex={0}
      aria-label={`Open article: ${article.title}`}
      onClick={(event) => onOpenArticle(article, event.currentTarget)}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onOpenArticle(article, event.currentTarget)
        }
      }}
    >
      <div className="article-card__inner">
        <div className="article-main-content">
          <div className="article-card__head">
            <div>
              <p className="article-kicker">
                {article.kicker ?? article.category.replaceAll('_', ' ')}
              </p>
              <h3>{article.title}</h3>
            </div>
            <div className="article-badge">
              <span>{importanceLabel[article.importance]}</span>
              <small>{readTime} min</small>
            </div>
          </div>

          <p className="article-subtitle">{article.subtitle}</p>

          <div className="article-meta">
            <span>{authors || 'Dispatch desk'}</span>
            <span>Page {formatPageLabel(article.page)}</span>
          </div>

          {hasMedia && size !== 'major' ? (
            <figure className={`article-media article-media--${article.importance}`}>
              <img src={image.src} alt={image.alt} loading="lazy" />
              {image.caption || image.credit ? (
                <figcaption>
                  {image.caption}
                  {image.credit ? <span>{image.caption ? ` · ${image.credit}` : image.credit}</span> : null}
                </figcaption>
              ) : null}
            </figure>
          ) : null}

          <div className="article-body">
            {hasMedia && size === 'major' ? (
              <figure className={`article-media article-media--${article.importance} article-media--floated`}>
                <img src={image.src} alt={image.alt} loading="lazy" />
                {image.caption || image.credit ? (
                  <figcaption>
                    {image.caption}
                    {image.credit ? <span>{image.caption ? ` · ${image.credit}` : image.credit}</span> : null}
                  </figcaption>
                ) : null}
              </figure>
            ) : null}
            {article.content.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>

          <div className="article-footer">
            <div className="article-sources">
              {article.sources.map((source) => (
                <a
                  key={`${article.id}-${source.url}`}
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(event) => event.stopPropagation()}
                >
                  {source.name}
                </a>
              ))}
            </div>
            <span className="article-source-note">{sourceNames}</span>
          </div>
        </div>
      </div>
    </article>
  )
}

function estimateReadTime(article: ArticleStory) {
  const words = article.content.join(' ').trim().split(/\s+/).filter(Boolean).length
  return Math.max(2, Math.round(words / 180) || 2)
}

function ReadingModal({
  article,
  onClose,
  closeRef,
}: {
  article: ArticleStory
  onClose: () => void
  closeRef: RefObject<HTMLButtonElement | null>
}) {
  const image = article.images[0]
  const readTime = article.readTimeMin ?? estimateReadTime(article)

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="reading-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reading-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="reading-modal__head">
          <div>
            <p className="front-kicker">{article.category.replaceAll('_', ' ')}</p>
            <h2 id="reading-title">{article.title}</h2>
            <p className="reading-dek">{article.subtitle}</p>
          </div>
          <button ref={closeRef} type="button" className="page-arrow" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="reading-meta">
          <span>{article.authors.map((author) => author.name).join(' · ')}</span>
          <span>{readTime} minute read</span>
          <span>Page {formatPageLabel(article.page)}</span>
          <span>Importance {article.importance}</span>
        </div>

        {image ? (
          <figure className="reading-figure">
            <img src={image.src} alt={image.alt} />
            {(image.caption || image.credit) && (
              <figcaption>
                {image.caption}
                {image.credit ? <span>{image.caption ? ` · ${image.credit}` : image.credit}</span> : null}
              </figcaption>
            )}
          </figure>
        ) : null}

        <div className="reading-body">
          {article.content.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>

        <div className="reading-sources">
          <h3>Sources</h3>
          <div className="source-list">
            {article.sources.map((source) => (
              <a key={`${article.id}-${source.url}`} href={source.url} target="_blank" rel="noreferrer">
                {source.name}
              </a>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

function SettingsScreen({
  edition,
  settings,
  onBack,
  onToggleSource,
  onToggleCategory,
  onUpdateFeed,
  onUpdateModel,
  onUpdateLayout,
  onReset,
}: {
  edition: DummyEdition
  settings: AppSettings
  onBack: () => void
  onToggleSource: (sourceId: string) => void
  onToggleCategory: (categoryId: string) => void
  onUpdateFeed: (patch: Partial<UserFeedSettings>) => void
  onUpdateModel: (patch: Partial<AppSettings['model']>) => void
  onUpdateLayout: (patch: Partial<UserLayoutSettings>) => void
  onReset: () => void
}) {
  return (
    <div className="settings-shell">
      <header className="settings-head">
        <button type="button" className="link-button" onClick={onBack}>
          ← Back to paper
        </button>
        <div>
          <p className="front-kicker">Settings</p>
          <h1>Newspaper controls</h1>
          <p className="settings-lede">
            Configure sources, model defaults, layout density, and the subjects that survive into
            each page of the paper.
          </p>
        </div>
      </header>

      <div className="settings-grid">
        <section className="settings-card">
          <h2>Feed configuration</h2>
          <div className="settings-block">
            <h3>Sources</h3>
            <div className="settings-list">
              {edition.sources.map((source) => (
                <label key={source.id} className="check-row">
                  <input
                    type="checkbox"
                    checked={settings.feed.enabledSourceIds.includes(source.id)}
                    onChange={() => onToggleSource(source.id)}
                  />
                  <span>
                    {source.name}
                    <small>{source.description ?? source.url.replace('https://', '')}</small>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="settings-block">
            <h3>Subjects</h3>
            <div className="settings-list">
              {edition.categories.map((category) => (
                <label key={category.id} className="check-row">
                  <input
                    type="checkbox"
                    checked={settings.feed.enabledCategoryIds.includes(category.id)}
                    onChange={() => onToggleCategory(category.id)}
                  />
                  <span>
                    {category.title}
                    <small>{category.description ?? category.id}</small>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="settings-block">
            <h3>Max articles per page</h3>
            <label className="slider-row">
              <span>{settings.feed.maxArticlesPerPage}</span>
              <input
                type="range"
                min={1}
                max={8}
                value={settings.feed.maxArticlesPerPage}
                onChange={(event) =>
                  onUpdateFeed({ maxArticlesPerPage: Number(event.target.value) })
                }
              />
            </label>
          </div>
        </section>

        <section className="settings-card">
          <h2>Model settings</h2>
          <div className="settings-block">
            <h3>Provider</h3>
            <div className="button-row">
              {(['Gemini', 'OpenAI', 'Ollama Cloud'] as const).map((provider) => (
                <button
                  key={provider}
                  type="button"
                  className={settings.model.provider === provider ? 'tab-pill active' : 'tab-pill'}
                  onClick={() => onUpdateModel({ provider })}
                >
                  {provider}
                </button>
              ))}
            </div>
          </div>

          <div className="settings-block">
            <label className="field">
              <span>API key</span>
              <input
                type="password"
                value={settings.model.apiKey}
                onChange={(event) => onUpdateModel({ apiKey: event.target.value })}
              />
            </label>
            <label className="field">
              <span>Model name</span>
              <input
                type="text"
                value={settings.model.modelName}
                onChange={(event) => onUpdateModel({ modelName: event.target.value })}
              />
            </label>
          </div>

          <div className="settings-block">
            <label className="slider-row">
              <span>Temperature</span>
              <strong>{settings.model.temperature.toFixed(1)}</strong>
              <input
                type="range"
                min={0}
                max={1}
                step={0.1}
                value={settings.model.temperature}
                onChange={(event) => onUpdateModel({ temperature: Number(event.target.value) })}
              />
            </label>
            <label className="slider-row">
              <span>Summary sentences</span>
              <strong>{settings.model.maxSummarySentences}</strong>
              <input
                type="range"
                min={2}
                max={6}
                step={1}
                value={settings.model.maxSummarySentences}
                onChange={(event) =>
                  onUpdateModel({ maxSummarySentences: Number(event.target.value) })
                }
              />
            </label>
          </div>
        </section>

        <section className="settings-card">
          <h2>Layout</h2>
          <div className="settings-block">
            <h3>Story density</h3>
            <div className="button-row">
              {(['compact', 'balanced', 'generous'] as const).map((density) => (
                <button
                  key={density}
                  type="button"
                  className={
                    settings.layout.density === density ? 'tab-pill active' : 'tab-pill'
                  }
                  onClick={() => onUpdateLayout({ density })}
                >
                  {density}
                </button>
              ))}
            </div>
          </div>

          <div className="settings-block">
            <label className="check-row">
              <input
                type="checkbox"
                checked={settings.layout.showImages}
                onChange={() => onUpdateLayout({ showImages: !settings.layout.showImages })}
              />
              <span>
                Show images
                <small>Use the dummy photo blocks on article cards.</small>
              </span>
            </label>
          </div>
        </section>
      </div>

      <footer className="settings-footer">
        <button type="button" className="tab-pill" onClick={onReset}>
          Reset demo settings
        </button>
        <button type="button" className="primary-button" onClick={onBack}>
          Return to paper
        </button>
      </footer>
    </div>
  )
}

function AuthScreen({ onSignIn }: { onSignIn: () => void }) {
  return (
    <div className="auth-screen">
      <section className="auth-card">
        <p className="front-kicker">Daily Dispatch</p>
        <h1>Open the morning paper</h1>
        <p className="auth-copy">
          Frontend-only sign-in for the mock edition. The newspaper is live; the backend comes
          later.
        </p>
        <div className="auth-actions">
          <button type="button" className="primary-button" onClick={onSignIn}>
            Continue
          </button>
        </div>
      </section>
    </div>
  )
}

function BootScreen() {
  return (
    <div className="auth-screen">
      <section className="boot-card">
        <p className="front-kicker">The Daily Dispatch</p>
        <h1>Setting the presses...</h1>
        <p>Loading the dummy edition and assembling the paper spread.</p>
      </section>
    </div>
  )
}

function StateScreen({
  title,
  description,
  actionLabel,
  onAction,
}: {
  title: string
  description: string
  actionLabel: string
  onAction: () => void
}) {
  return (
    <div className="auth-screen">
      <section className="auth-card">
        <p className="front-kicker">Paper state</p>
        <h1>{title}</h1>
        <p className="auth-copy">{description}</p>
        <button type="button" className="primary-button" onClick={onAction}>
          {actionLabel}
        </button>
      </section>
    </div>
  )
}

export default App
