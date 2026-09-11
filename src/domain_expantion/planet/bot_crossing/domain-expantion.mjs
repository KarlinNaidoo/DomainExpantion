/**
 * Harness adapter: Domain Expantion family.
 *
 * Bot Crossing's unit is a thread. We map one Thread per family inhabitant
 * (supervisor + specialists). State is written by the Python CLI into
 * <root>/.data/planet-family.json — this adapter only reads it.
 */
import fsp from 'node:fs/promises'
import path from 'node:path'
import { exists } from '../lib/fsutil.mjs'

const root = () => process.env.DOMAIN_EXPANTION_ROOT || process.cwd()
const snapshotPath = () => path.join(root(), '.data', 'planet-family.json')

export default {
  id: 'domain-expantion',
  name: 'Domain Expantion',
  detect,
  scanThreads,
  openThread,
  newSession,
}

async function detect() {
  return exists(snapshotPath())
}

async function scanThreads() {
  const file = snapshotPath()
  if (!(await exists(file))) return []
  let payload
  try {
    payload = JSON.parse(await fsp.readFile(file, 'utf8'))
  } catch {
    return []
  }
  const inhabitants = Array.isArray(payload.inhabitants) ? payload.inhabitants : []
  const projectPath = root()
  const now = Date.now()
  return inhabitants.map((item) => {
    const run = item.run_state || 'idle'
    const rawTs = Number(item.run_ts)
    const ts = !rawTs ? now : rawTs > 1e12 ? rawTs : rawTs * 1000
    const campus = campusFor(item)
    const size = campusSizeBytes(item, run)
    return {
      id: `domain-expantion:${item.name}`,
      harness: 'domain-expantion',
      title: item.title || item.name,
      preview: item.run_detail || item.when_to_use || '',
      project: campus,
      projectPath,
      worktree: '',
      cwd: projectPath,
      gitBranch: '',
      model: 'grok-4.6',
      effort: '',
      createdAt: ts,
      lastActivityAt: ts,
      lastFocusedAt: 0,
      running: run === 'working',
      unread: run === 'waiting',
      hasError: run === 'error',
      starred: false,
      routine: false,
      prState: '',
      archived: false,
      sizeBytes: size,
      source: item.role || 'specialist',
      canOpen: true,
      ref: { name: item.name },
    }
  })
}

const CAMPUSES = {
  research: { project: 'Research Center', bytes: 220_000 },
  architecture: { project: 'Architecture Studio', bytes: 180_000 },
  code: { project: 'Code Works', bytes: 120_000 },
  supervisor: { project: 'DomainExpantion', bytes: 90_000 },
}

function campusFor(item) {
  return CAMPUSES[item.name]?.project || 'DomainExpantion'
}

function campusSizeBytes(item, run) {
  const campus = CAMPUSES[item.name]
  if (campus) return campus.bytes
  if (run === 'working') return 80_000
  if (item.status === 'live') return 40_000
  return 4_000
}

const CHAT = 'http://127.0.0.1:8766/chat.html'

async function openThread(ref) {
  const name = ref?.name || 'supervisor'
  const thread = name === 'supervisor' ? 'colony-main' : `colony-${name}`
  return { ok: true, url: `${CHAT}?thread=${encodeURIComponent(thread)}&agent=${encodeURIComponent(name)}` }
}

async function newSession() {
  const thread = `colony-${Date.now()}`
  return { ok: true, url: `${CHAT}?thread=${encodeURIComponent(thread)}&agent=supervisor` }
}
