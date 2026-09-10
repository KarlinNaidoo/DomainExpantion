/**
 * Overlay for vendor/bot-crossing/server/harnesses/index.mjs
 * Family only — do not scan Claude/Codex/Cursor on this machine.
 */
import domainExpantion from './domain-expantion.mjs'

export const HARNESSES = [domainExpantion]

export const harnessById = (id) => HARNESSES.find((h) => h.id === id) || null

export async function detectedHarnesses() {
  const flags = await Promise.all(
    HARNESSES.map(async (h) => {
      try {
        return await h.detect()
      } catch {
        return false
      }
    }),
  )
  return HARNESSES.filter((_, i) => flags[i])
}
