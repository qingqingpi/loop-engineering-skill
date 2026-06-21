# Deployment and monitoring

Read this when taking a loop live. Designing a loop well is necessary but not sufficient; a new
loop must earn autonomy in stages, with measurement at each stage.

## Staged rollout — do not jump a new loop to full autonomy

1. **Offline evaluation** — run on a representative set *and* an adversarial set (cases designed
   to game the verifier or hit edge conditions). Measure before any side effects.
2. **Shadow mode** — run the full loop but commit no external side effects; compare its proposed
   actions against what a human would do. This catches reward-hacking and miscalibration safely.
3. **Human-approved mode** — the loop proposes, a human approves each commit.
4. **Limited canary** — allow autonomous commits on a small slice with strict quotas (low max
   work items, low per-item budget, low concurrency).
5. **Expand** — widen scope only after measured targets are met (see metrics). Expansion is a
   decision backed by numbers, not a default.

Keep a **kill switch** (halt all loops immediately) and preserve an **audit trail** (every attempt,
verdict, action, and approval) at every stage.

## Monitoring metrics

Track per loop and in aggregate:

- **Acceptance rate** — fraction of work items the loop completes to threshold.
- **False-acceptance rate** — accepted items later found bad. The single most important safety
  metric; it should trend down, never up.
- **Average iterations per item** — rising means the task is drifting out of the loop's range or
  the verifier is getting noisier.
- **Cost per accepted work item** — the real unit economics; watch this, not just total spend.
- **Escalation rate** — too low can mean the loop fails silently instead of raising its hand; too
  high means the task isn't a good fit.
- **Rollback rate** — how often committed work had to be undone.
- **Verifier disagreement rate** — between checkers, or checker vs. human audit.
- **Time to resolution** per item.
- **Repeated failure fingerprints** — recurring stuck patterns to fix at the design level.
- **Token and tool cost** — broken out, so a runaway is visible early.

## Cost ceiling

Bound worst-case spend explicitly before running unattended:

```
maximum_cost =
    max_work_items
  × max_iterations_per_item
  × (maker_cost + verifier_cost + tool_cost)
  × concurrency_factor
```

If the worst case is unacceptable, the fix is tighter caps or a higher-fidelity (faster-stopping)
verifier — not hoping the loop stops early on its own.
