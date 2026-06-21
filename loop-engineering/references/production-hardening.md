# Production hardening

Read this when moving a working loop toward unattended or concurrent operation. It covers the
things the core skill points to but does not inline: verifier calibration, idempotent/transactional
actions, concurrency, and structured state.

## 1. Verifier calibration

A rubric or model-judge is not trustworthy because it exists — it is trustworthy because it has
been measured. A loop actively searches for the verifier's blind spots, so an uncalibrated judge
degrades faster under a loop than under a human.

Calibrate before relying on it, and re-calibrate on drift:

- Build a human-labeled sample of "good" and "not good" outputs for this task.
- Measure the judge against that sample. The headline metric is **false-acceptance rate (FAR)** —
  the fraction of actually-bad outputs the verifier passes — not average score. FAR is what the
  loop will exploit. Track false-reject rate too (it wastes iterations), but FAR is the safety
  metric.
- For boundary / disagreement cases, prefer pairwise comparison ("is A better than B?") over
  absolute scoring; pairwise is usually better calibrated.
- Periodically random-audit a sample of *already-passed* outputs with a human. "Passed" must keep
  correlating with "actually good."
- Monitor verifier output distribution for drift (mean score creeping up with no real quality
  change is a red flag for reward hacking or judge degradation).
- When verifiers disagree, escalate the case (to a stronger checker or a human) rather than
  picking one.
- **Re-calibrate whenever the rubric changes.** A rubric edit invalidates prior calibration.

Set an explicit reliability target (e.g. "FAR < X% on the calibration set") and treat the loop as
not production-ready until it is met.

## 2. Idempotent and transactional actions

Dry-run and sandbox (in the core skill) prevent bad *content*. This section prevents bad *delivery*:
duplicate sends, double charges, half-applied changes. For any action with external side effects,
do not just check once before executing. Use:

```
prepare → preview → validate → approve → commit → verify postcondition
```

Each external action should specify:

- **Idempotency key** — a stable key so a retry of "the same" action is recognized and not
  re-executed. Mandatory for send / pay / create.
- **Retry semantics** — is a retry safe? If not, it must be made safe via the idempotency key
  before the loop is allowed to retry it.
- **Preconditions** — assert the world is in the expected state before committing (the item is
  still unprocessed, the balance is sufficient, the branch is unchanged).
- **Postcondition verification** — after commit, verify the effect actually happened and matches
  intent. "The call returned 200" is not "the effect is correct."
- **Partial-failure handling** — what state are we in if step 3 of 5 fails? Define it explicitly.
- **Compensation / rollback** — for multi-step effects, a defined way to undo or compensate a
  partially-applied change.
- **Rate limits** — a loop can hammer an API far faster than a human; bound it.
- **Concurrency lock** — see below.

## 3. Concurrency and locking

When multiple agents run in parallel (the outer scheduler dispatches several):

- **Reserve / lock the work item** before the inner loop starts, so two agents don't process the
  same item.
- **Optimistic locking on state** — every state write carries a version; a write that finds the
  version has moved fails and re-reads rather than blindly overwriting. This is what stops agents
  from clobbering each other's progress.
- **Isolated workspaces** (git worktrees / sandboxes) so file-level work doesn't collide.
- Clean up reservations and worktrees on completion or abandonment; orphaned locks stall the
  queue, orphaned worktrees are disk debt.

## 4. Structured state schema

A free-text `STATE.md` is fine for a single serial loop. For multi-run or concurrent loops, keep
**structured state** (machine-updatable, lockable) alongside a human-readable summary. Keep four
things: structured current state, an append-only attempt log, the raw verifier evidence, and a
human summary.

Example structured-state record:

```json
{
  "goal_version": "v3",
  "verifier_version": "v2",
  "rubric_version": "v5",
  "work_item_id": "PR-418",
  "attempt": 4,
  "artifact_ref": "worktree://repo/pr-418",
  "last_verdict": "fail",
  "failed_criteria": ["AC-3", "AC-7"],
  "failure_fingerprint": "typecheck:UserId",
  "progress_metrics": { "failing_tests": 2, "unmet_rubric_items": 1 },
  "budget_remaining": { "iterations": 3, "tokens": 41000, "usd": 0.62 },
  "pending_approval": null,
  "updated_at": "2026-06-21T07:55:00Z",
  "state_version": 12
}
```

The version fields are the control-plane audit trail. If the acceptance contract, verifier, or
rubric changes mid-run, prior attempts were judged against a different target and may need
re-evaluation — and because the maker must not silently weaken any of these (it is the easiest
"fix" for a stuck agent), a version bump should correspond to an *approved* change, not an
agent-initiated one. `failure_fingerprint` and `progress_metrics` are what the no-progress check
reads. `state_version` drives optimistic locking.
