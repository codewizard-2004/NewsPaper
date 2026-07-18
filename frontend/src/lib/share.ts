import type { ArticleStory, DummyEdition, UserInterfaceSettings } from './types'

const escapeXml = (value: string) =>
  value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;')

export function buildCoverSvg(
  edition: DummyEdition,
  stories: ArticleStory[],
  theme: UserInterfaceSettings['theme'],
) {
  const accent = theme === 'night' ? '#d7c2a4' : '#7e2f1c'
  const ink = theme === 'night' ? '#f5f0e7' : '#171311'
  const paper = theme === 'night' ? '#101113' : '#f7f1e6'
  const panel = theme === 'night' ? '#17181c' : '#fffaf0'
  const border = theme === 'night' ? '#2b2f39' : '#d8c6ac'

  const headlineLines = stories.slice(0, 4).flatMap((story, index) => [
    `<text x="96" y="${420 + index * 190}" font-family="Georgia, serif" font-size="32" fill="${ink}" font-weight="700">${escapeXml(story.title)}</text>`,
    `<text x="96" y="${452 + index * 190}" font-family="Inter, Arial, sans-serif" font-size="18" fill="${accent}">${escapeXml(story.subtitle)}</text>`,
  ])

  return `
  <svg width="1200" height="1600" viewBox="0 0 1200 1600" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" stop-color="${paper}" />
        <stop offset="100%" stop-color="${theme === 'night' ? '#0a0b0d' : '#ece0cb'}" />
      </linearGradient>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="${theme === 'night' ? '#000' : '#5f4930'}" flood-opacity="0.24" />
      </filter>
    </defs>
    <rect width="1200" height="1600" fill="url(#bg)" />
    <rect x="48" y="44" width="1104" height="1512" rx="28" fill="${panel}" stroke="${border}" stroke-width="2" filter="url(#shadow)" />
    <text x="96" y="122" font-family="Georgia, serif" font-size="24" letter-spacing="8" fill="${accent}">THE DAILY DISPATCH</text>
    <text x="96" y="190" font-family="Georgia, serif" font-size="78" font-weight="700" fill="${ink}">${escapeXml(edition.title)}</text>
    <text x="96" y="244" font-family="Inter, Arial, sans-serif" font-size="22" fill="${accent}">${escapeXml(edition.subtitle)}</text>
    <text x="96" y="286" font-family="Inter, Arial, sans-serif" font-size="18" fill="${ink}">Vol. ${edition.volume}, No. ${edition.issue} · ${escapeXml(edition.issueDate)}</text>
    <rect x="96" y="330" width="1008" height="2" fill="${border}" />
    ${headlineLines.join('\n')}
    <text x="96" y="1244" font-family="Georgia, serif" font-size="28" font-weight="700" fill="${ink}">Top of the page</text>
    <text x="96" y="1286" font-family="Inter, Arial, sans-serif" font-size="18" fill="${accent}">Curated summaries and visible source attribution</text>
    <text x="96" y="1348" font-family="Inter, Arial, sans-serif" font-size="16" fill="${ink}">Pages: ${escapeXml(edition.pages.map((page) => page.title).join(' · '))}</text>
    <rect x="96" y="1390" width="1008" height="96" rx="18" fill="${theme === 'night' ? '#1a1d22' : '#f1e8d9'}" stroke="${border}" />
    <text x="126" y="1430" font-family="Inter, Arial, sans-serif" font-size="18" fill="${accent}">Read time</text>
    <text x="126" y="1462" font-family="Georgia, serif" font-size="30" font-weight="700" fill="${ink}">${stories.reduce((sum, story) => sum + (story.readTimeMin ?? 2), 0)} min on the front page</text>
  </svg>`
}
