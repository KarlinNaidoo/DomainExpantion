/**
 * Overlay for vendor/bot-crossing/server/harnesses/index.mjs
 * Adds the Domain Expantion family next to Claude/Codex/Cursor.
 */
import claudeCode from './claude-code.mjs'
import codex from './codex.mjs'
import cursor from './cursor.mjs'
import domainExpantion from './domain-expantion.mjs'

export const HARNESSES = [domainExpantion, claudeCode, codex, cursor]

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
