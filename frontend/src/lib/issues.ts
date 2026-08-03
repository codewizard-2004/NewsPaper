import { db } from '@/lib/firebase'
import { doc, onSnapshot } from 'firebase/firestore'
import type { IssueDoc } from './adapter'

export { transformIssue } from './adapter'
export type { IssueDoc, ItemDoc, ArticleItemDoc, DsaItemDoc, ComicItemDoc, IssueSectionDoc } from './adapter'

export const getLocalISODate = (): string => {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

export function subscribeToIssue(
  date: string,
  callbacks: {
    onData: (doc: IssueDoc) => void
    onMissing: () => void
    onError: (error: Error) => void
  },
): () => void {
  const ref = doc(db, 'issues', date)
  return onSnapshot(
    ref,
    (snapshot) => {
      if (snapshot.exists()) {
        callbacks.onData(snapshot.data() as IssueDoc)
      } else {
        callbacks.onMissing()
      }
    },
    (error) => callbacks.onError(error),
  )
}
