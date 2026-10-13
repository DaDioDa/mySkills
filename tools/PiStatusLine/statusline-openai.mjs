#!/usr/bin/env node
/**
 * OpenAI Codex usage status line for pi-statusline.
 *
 * Reads pi-statusline's Claude-like JSON payload from stdin and reads the
 * OpenAI Codex OAuth credentials that pi already manages.  The ChatGPT usage
 * endpoint is cached briefly so a status-line refresh does not hit it each turn.
 */
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, isAbsolute, join, resolve } from "node:path";

const BAR_WIDTH = 10;
const CACHE_TTL_MS = 30_000;
const HOME = homedir();
const AGENT_DIR = process.env.PI_CODING_AGENT_DIR || join(HOME, ".pi", "agent");
const AUTH_FILE = join(AGENT_DIR, "auth.json");
const CACHE_FILE = join(AGENT_DIR, "cache", "openai-codex-usage.json");

const C = {
  model: "\x1b[1;97m", thinking: "\x1b[35m", ctx: "\x1b[96m", usage: "\x1b[93m", reset: "\x1b[33m",
  sep: "\x1b[90m", dir: "\x1b[92m", branch: "\x1b[95m", off: "\x1b[0m",
};

function percent(value) {
  const n = Math.round(Number(value));
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : null;
}

function bar(value) {
  const filled = Math.max(0, Math.min(BAR_WIDTH, Math.round(value * BAR_WIDTH / 100)));
  return "#".repeat(filled) + "-".repeat(BAR_WIDTH - filled);
}

function countdown(resetAt) {
  let seconds = Number(resetAt) - Math.floor(Date.now() / 1000);
  if (!Number.isFinite(seconds) || seconds <= 0) return "now";
  const days = Math.floor(seconds / 86400);
  seconds %= 86400;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (days) return `${days}d${hours}h`;
  if (hours) return `${hours}h${minutes}m`;
  return minutes ? `${minutes}m` : "1m";
}

function windowLabel(seconds, fallback) {
  seconds = Number(seconds);
  if (seconds >= 86400 && seconds % 86400 === 0) return `${seconds / 86400}d`;
  if (seconds >= 3600 && seconds % 3600 === 0) return `${seconds / 3600}h`;
  return fallback;
}

function gitBranch(cwd) {
  let dir = cwd;
  for (let i = 0; i < 40 && dirname(dir) !== dir; i++, dir = dirname(dir)) {
    const dotGit = join(dir, ".git");
    let head = join(dotGit, "HEAD");
    try {
      if (!existsSync(head) && existsSync(dotGit)) {
        const gitFile = readFileSync(dotGit, "utf8").trim();
        if (gitFile.startsWith("gitdir: ")) {
          const gitDir = gitFile.slice(8).trim();
          head = join(isAbsolute(gitDir) ? gitDir : resolve(dir, gitDir), "HEAD");
        }
      }
      if (!existsSync(head)) continue;
      const value = readFileSync(head, "utf8").trim();
      return value.startsWith("ref: refs/heads/") ? value.slice(16) : value.slice(0, 7);
    } catch { /* not a repository */ }
  }
  return "";
}

async function readCache() {
  try {
    const cache = JSON.parse(await readFile(CACHE_FILE, "utf8"));
    return Date.now() - cache.fetchedAt < CACHE_TTL_MS ? cache.usage : null;
  } catch { return null; }
}

async function getOpenAIUsage() {
  const cached = await readCache();
  if (cached) return cached;
  try {
    const auth = JSON.parse(await readFile(AUTH_FILE, "utf8"))["openai-codex"];
    if (!auth?.access || !auth?.accountId) return null;
    const response = await fetch("https://chatgpt.com/backend-api/wham/usage", {
      headers: {
        Authorization: `Bearer ${auth.access}`,
        "ChatGPT-Account-Id": auth.accountId,
        "User-Agent": "pi-statusline",
      },
      signal: AbortSignal.timeout(8_000),
    });
    if (!response.ok) return null;
    const usage = await response.json();
    await mkdir(dirname(CACHE_FILE), { recursive: true });
    await writeFile(CACHE_FILE, JSON.stringify({ fetchedAt: Date.now(), usage }), "utf8");
    return usage;
  } catch { return null; }
}

const input = await new Promise((resolveInput) => {
  let text = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => { text += chunk; });
  process.stdin.on("end", () => { try { resolveInput(JSON.parse(text)); } catch { resolveInput({}); } });
});

const parts = [];
const model = input?.model?.display_name || input?.model?.id;
const thinking = input?.pi?.thinking_level || process.env.PI_REASONING_LEVEL;
if (model) {
  parts.push(`${C.model}${model}${C.off}${thinking ? ` ${C.thinking}${thinking}${C.off}` : ""}`);
}

const context = percent(input?.context_window?.used_percentage);
if (context !== null) parts.push(`${C.ctx}Ctx [${bar(context)}] ${context}%${C.off}`);

const usage = await getOpenAIUsage();
const rateLimit = usage?.rate_limit;
for (const [key, fallback] of [["primary_window", "5h"], ["secondary_window", "7d"]]) {
  const window = rateLimit?.[key];
  const used = percent(window?.used_percent);
  if (used === null) continue;
  const label = windowLabel(window.limit_window_seconds, fallback);
  parts.push(`${C.usage}OpenAI ${label} [${bar(used)}] ${used}%${C.off} ${C.reset}${countdown(window.reset_at)}${C.off}`);
}

const cwd = input?.workspace?.current_dir || input?.cwd;
if (cwd) {
  const branch = gitBranch(cwd);
  parts.push(`${C.sep}│${C.off} ${C.dir}${basename(cwd) || cwd}${C.off}${branch ? ` ${C.branch}${branch}${C.off}` : ""}`);
}

console.log(parts.length ? parts.join("   ") : `${C.sep}no status data yet${C.off}`);
