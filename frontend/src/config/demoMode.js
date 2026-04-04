const rawDemoMode = String(import.meta.env.VITE_DEMO_MODE || '').trim().toLowerCase()

export const isDemoMode =
  rawDemoMode === 'true' ||
  rawDemoMode === '1' ||
  rawDemoMode === 'yes' ||
  rawDemoMode === 'on'
