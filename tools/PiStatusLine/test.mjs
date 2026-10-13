import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = fileURLToPath(new URL('.', import.meta.url));
const home = await mkdtemp(join(tmpdir(), 'pi-statusline-test-'));
const agent = join(home, '.pi', 'agent');
const env = { ...process.env, HOME: home, USERPROFILE: home, PI_CODING_AGENT_DIR: agent };
const run = (file, input) => {
  const result = spawnSync(process.execPath, [join(root, file)], { env, input, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
};
try {
  await mkdir(join(agent, 'cache'), { recursive: true });
  const original = { theme: 'light', defaultModel: 'keep-me', packages: ['npm:other', 'npm:pi-statusline'], statusLine: { command: 'old' } };
  await writeFile(join(agent, 'settings.json'), JSON.stringify(original));
  run('install.mjs');
  const installed = JSON.parse(await readFile(join(agent, 'settings.json'), 'utf8'));
  assert.equal(installed.theme, 'light');
  assert.equal(installed.defaultModel, 'keep-me');
  assert.deepEqual(installed.packages, ['npm:other', join(agent, 'statusline-packages', 'pi-statusline').replaceAll('\\', '/')]);
  run('install.mjs');
  assert.deepEqual(JSON.parse(await readFile(join(agent, 'settings.json'), 'utf8')), installed);
  const input = JSON.stringify({ model: { display_name: 'GPT-test' }, pi: { thinking_level: 'high' }, context_window: { used_percentage: 42 }, cwd: home });
  let output = run('statusline-openai.mjs', input);
  assert.match(output, /GPT-test/);
  assert.match(output, /high/);
  assert.match(output, /42%/);
  assert.doesNotMatch(output, /OpenAI/);
  await writeFile(join(agent, 'cache', 'openai-codex-usage.json'), JSON.stringify({ fetchedAt: Date.now(), usage: { rate_limit: {
    primary_window: { used_percent: 25, limit_window_seconds: 18000, reset_at: Date.now() / 1000 + 3600 },
    secondary_window: { used_percent: 60, limit_window_seconds: 604800, reset_at: Date.now() / 1000 + 86400 },
  } } }));
  output = run('statusline-openai.mjs', input);
  assert.match(output, /OpenAI 5h/);
  assert.match(output, /25%/);
  assert.match(output, /OpenAI 7d/);
  assert.match(output, /60%/);
  await writeFile(join(agent, 'settings.json'), '{invalid');
  const failed = spawnSync(process.execPath, [join(root, 'install.mjs')], { env, encoding: 'utf8' });
  assert.notEqual(failed.status, 0);
  assert.equal(await readFile(join(agent, 'settings.json'), 'utf8'), '{invalid');
  console.log('PASS: isolated install, preserved settings, repeat install, invalid JSON guard, rendering without auth and with mock usage. No real credentials or network used.');
} finally {
  await rm(home, { recursive: true, force: true });
}
