import { useEffect, useState } from 'react'

const isBrowser = typeof window !== 'undefined'

export function safeJsonParse<T>(value: string | null, fallback: T): T {
  if (!value) {
    return fallback
  }

  try {
    return JSON.parse(value) as T
  } catch {
    return fallback
  }
}

function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result: Record<string, unknown> = { ...target }
  for (const key of Object.keys(source) as (keyof T)[]) {
    const srcVal = source[key]
    const tgtVal = target[key]
    if (
      srcVal !== undefined &&
      typeof srcVal === 'object' &&
      !Array.isArray(srcVal) &&
      typeof tgtVal === 'object' &&
      !Array.isArray(tgtVal)
    ) {
      result[key as string] = deepMerge(
        tgtVal as Record<string, unknown>,
        srcVal as Partial<Record<string, unknown>>,
      ) as unknown
    } else if (srcVal !== undefined) {
      result[key as string] = srcVal as unknown
    }
  }
  return result as T
}

export function usePersistentState<T>(key: string, fallback: T) {
  const [state, setState] = useState<T>(() => {
    if (!isBrowser) {
      return fallback
    }

    const stored = safeJsonParse<T>(window.localStorage.getItem(key), fallback)
    if (typeof stored === 'object' && stored !== null && !Array.isArray(stored) &&
        typeof fallback === 'object' && fallback !== null && !Array.isArray(fallback)) {
      return deepMerge(fallback as Record<string, unknown>, stored as Record<string, unknown>) as unknown as T
    }
    return stored
  })

  useEffect(() => {
    if (!isBrowser) {
      return
    }

    window.localStorage.setItem(key, JSON.stringify(state))
  }, [key, state])

  return [state, setState] as const
}

export function removeStorageItem(key: string) {
  if (!isBrowser) {
    return
  }

  window.localStorage.removeItem(key)
}
