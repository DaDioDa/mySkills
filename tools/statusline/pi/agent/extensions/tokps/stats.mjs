import { createHash, randomUUID } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync, renameSync, unlinkSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { homedir } from 'node:os';

export const agentDir = () => process.env.PI_CODING_AGENT_DIR || join(homedir(), '.pi', 'agent');
const key = value => createHash('sha256').update(value).digest('hex');
export const samplePath = (dir, session) => join(dir, 'cache', 'tokps', `${key(session)}.json`);
function read(path) { try { return JSON.parse(readFileSync(path, 'utf8')); } catch { return null; } }
export function atomicWrite(path, data) {
  const temp = `${path}.${randomUUID()}.tmp`;
  try {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(temp, JSON.stringify(data), { mode: 0o600 });
    renameSync(temp, path);
    return true;
  } catch { return false; }
  finally { try { unlinkSync(temp); } catch {} }
}
const valid = s => Number.isSafeInteger(s?.tokens) && s.tokens >= 30 && Number.isFinite(s?.ms) && s.ms > 0;
export function loadStats(dir, session) {
  if (typeof session !== 'string' || !session) return null;
  const data = read(samplePath(dir, session));
  return data?.version === 1 && typeof data.revision === 'string' && Array.isArray(data.samples) &&
    data.samples.length > 0 && data.samples.length <= 10 && data.samples.every(valid) ? data : null;
}
export function rate(samples) {
  return Math.round(samples.reduce((n, s) => n + s.tokens, 0) * 1000 / samples.reduce((n, s) => n + s.ms, 0));
}
export function record(dir, session, sample) {
  if (typeof session !== 'string' || !session || !valid(sample)) return false;
  const samples = [...(loadStats(dir, session)?.samples || []), sample].slice(-10);
  return atomicWrite(samplePath(dir, session), { version: 1, revision: randomUUID(), samples });
}
// Separate consumer state: a repaint must not modify the producer's sample file.
export function statusSegment(dir, session, consumer = 'statusline-openai') {
  const stats = loadStats(dir, session);
  if (!stats) return '';
  const path = join(dir, 'cache', 'tokps', `${key(session)}.${key(consumer)}.seen.json`);
  const fresh = read(path)?.revision !== stats.revision;
  if (fresh) atomicWrite(path, { revision: stats.revision });
  return `\x1b[${fresh ? '32' : '90'}m${rate(stats.samples)} tok/s\x1b[0m`;
}

export function createTracker(dir, now = () => performance.now()) {
  let pending;
  return {
    clear() { pending = undefined; },
    // Pi emits turn_start before request preparation/API work, after prior tools.
    // message_start is too late (provider stream-start), so never re-arm there.
    turnStart(session) {
      pending = { session, start: now() };
    },
    end(message, session) {
      if (message.role !== 'assistant') return;
      const started = pending;
      pending = undefined;
      if (!started || started.session !== session || message.errorMessage ||
          !['stop', 'length', 'toolUse'].includes(message.stopReason)) return;
      record(dir, session, { tokens: message.usage?.output, ms: now() - started.start });
    },
  };
}
