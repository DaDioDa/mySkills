import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';
import { agentDir, createTracker } from './stats.mjs';

export default function (pi: ExtensionAPI) {
  const tracker = createTracker(agentDir());
  pi.on('turn_start', (_event, ctx) => {
    tracker.turnStart(ctx.sessionManager.getSessionId());
  });
  pi.on('message_end', (event, ctx) => {
    tracker.end(event.message, ctx.sessionManager.getSessionId());
  });
  for (const event of ['session_start', 'session_shutdown', 'session_before_switch',
    'session_before_fork', 'session_before_tree', 'agent_end'] as const) {
    pi.on(event, () => { tracker.clear(); });
  }
}
