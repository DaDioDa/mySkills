#!/usr/bin/env node
// Install the snapshot without copying credentials or replacing unrelated settings.
import { cp, mkdir, readFile, writeFile, copyFile, access } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

if (process.argv.slice(2).length) throw new Error('Usage: node install.mjs (no arguments)');
const agentDir = join(homedir(), '.pi', 'agent');
if (process.env.PI_CODING_AGENT_DIR && resolve(process.env.PI_CODING_AGENT_DIR) !== resolve(agentDir)) {
  throw new Error('This extension reads ~/.pi/agent/settings.json. Custom PI_CODING_AGENT_DIR needs manual adaptation; no files changed.');
}
const source = fileURLToPath(new URL('.', import.meta.url));
const settingsPath = join(agentDir, 'settings.json');
let settings = {};
let original;
try { original = await readFile(settingsPath, 'utf8'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
if (original !== undefined) settings = JSON.parse(original);
if (!settings || typeof settings !== 'object' || Array.isArray(settings)) throw new Error('settings.json must be an object');
if (settings.packages !== undefined && !Array.isArray(settings.packages)) throw new Error('settings.packages must be an array');
const scriptPath = join(agentDir, 'statusline-openai.mjs');
const packagePath = join(agentDir, 'statusline-packages', 'pi-statusline');
// Fail before changing the destination if the transfer is incomplete.
await access(join(source, 'statusline-openai.mjs'));
await access(join(source, 'vendor', 'pi-statusline', 'src', 'index.ts'));
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const backup = join(agentDir, 'statusline-backups', stamp);
await mkdir(backup, { recursive: true });
if (original !== undefined) await writeFile(join(backup, 'settings.json'), original);
for (const [path, name] of [[scriptPath, 'statusline-openai.mjs'], [packagePath, 'pi-statusline']]) {
  try { await access(path); }
  catch (error) { if (error.code === 'ENOENT') continue; throw error; }
  await cp(path, join(backup, name), { recursive: true });
}
await mkdir(join(agentDir, 'statusline-packages'), { recursive: true });
await copyFile(join(source, 'statusline-openai.mjs'), scriptPath);
await cp(join(source, 'vendor', 'pi-statusline'), packagePath, { recursive: true });
const portablePath = (path) => path.replaceAll('\\', '/');
const isStatusline = (entry) => {
  const value = typeof entry === 'string' ? entry : entry?.source;
  return typeof value === 'string' && (
    /^npm:pi-statusline(?:@|$)/.test(value) || value === portablePath(packagePath) || value === packagePath
  );
};
settings.packages = (settings.packages ?? []).filter((entry) => !isStatusline(entry));
settings.packages.push(portablePath(packagePath));
// Use the installer Node executable; quote for the shell used by the extension.
const quote = process.platform === 'win32'
  ? (value) => { if (/["%\r\n]/.test(value)) throw new Error('Unsupported shell characters in path'); return `"${portablePath(value)}"`; }
  : (value) => `'${value.replaceAll("'", "'\\''")}'`;
settings.statusLine = {
  type: 'command',
  command: `${quote(process.execPath)} ${quote(scriptPath)}`,
  timeoutMs: 10000,
};
await writeFile(settingsPath, JSON.stringify(settings, null, 2) + '\n');
console.log(`Installed: ${scriptPath}\nPackage: ${packagePath}\nBackup: ${backup}\nRestart Pi to load the status line. No credentials were copied.`);
