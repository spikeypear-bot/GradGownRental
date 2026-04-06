const cacheStore = new Map()

export function readCached(key, ttlMs) {
  const entry = cacheStore.get(key)
  if (!entry) return null

  if (Date.now() - entry.createdAt > ttlMs) {
    cacheStore.delete(key)
    return null
  }

  return entry.value
}

export function writeCached(key, value) {
  cacheStore.set(key, {
    value,
    createdAt: Date.now(),
  })
  return value
}

export function clearCached(key) {
  cacheStore.delete(key)
}
