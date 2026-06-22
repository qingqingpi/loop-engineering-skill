# Eval roadmap

This skill makes three independent claims, and they need separate evidence — do not roll them into
one headline score:

1. **Trigger** — does Claude activate the skill in the right situations (and stay quiet otherwise)?
2. **Judgment** — once active, does it produce better task-fit and design calls?
3. **Outcome** — do those calls actually improve a *running* agent loop?

The repo currently covers (1) and (2). Claim (3), real-task effect, is still unmeasured.

Status legend: **[done]** shipped · **[v0.2]** added in this release · **[planned]** designed here,
not built yet.

## Priority order

1. **[v0.2] Split `task_loop_fit` from `as_specified_design`.** The single-color verdict conflated
   "is the task loopable?" with "is the architecture the user proposed safe?" — H2 (a GREEN-fit lint
   loop that proposes merge-to-main inside the loop) could only come out as an ambiguous RED/YELLOW.
   The skill and the eval contract now report **task loop-fit / as-specified-design safety /
   safe-redesign fit** separately, plus verifier fidelity, feedback diagnosticity, irreversible
   actions + gateability, hard-veto, and the required gate. Validated in
   `raw-runs/split-verdict-validation-2026-06-22.md`.
2. **[planned] Minimal-pair Judgment suite.** Replace story-cases with counterfactual pairs that
   change one causal variable at a time (tests editable vs locked; send gated vs immediate; per-step
   vs terminal feedback; isolated branch vs prod; deterministic vs self-judge verifier), so a pass
   shows the skill is sensitive to *verifier fidelity / gateability*, not to danger words ("refund",
   "production", "hiring").
3. **[planned] Move test data out of the agent-readable repo** (the agent can read the public repo
   today, so committing cases there is not strong isolation).
4. **[planned] Commit–reveal pre-registration + arm-blind human scoring** (see below). Reaching here
   is the bar for "a clean eval".
5. **[planned] Placebo and no-examples ablations** (C1 / A1 below).
6. **[planned] 6–8 executable micro-environments** — the real Layer-3 outcome test. This is the
   `拼豆App` T3 effort already scoped separately. Reaching here is the bar for "persuasive scientific
   evidence".
7. **[planned] Publish full transcripts, environment states, analysis scripts, and failure cases.**

## Four eval suites

### 1. Trigger — should it fire?
- **[done]** 6/6 smoke test (`raw-runs/held-out-2026-06-21.md`), including the held-out ETL-retry
  boundary.
- **[planned]** Harder confusables: single-shot maker-checker (no refinement); periodic-but-
  independent runs; deterministic autofix + CI (no model); one-round multi-agent debate; API
  retry-without-revision; long multi-step task with no verifier loop. Test under skill-density
  (1 / 10 / 30 installed, plus a semantically-similar distractor), since Claude routes on the
  `description` and descriptions can be truncated under context budget. Report trigger precision,
  recall, false-activation, missed-activation, and wrong-skill-selection **separately** — not one F1.

### 2. Judgment — is the call correct?
- **[v0.2]** Scored on the split verdict, not one color (`held-out-results.md`).
- **[planned]** Minimal pairs (priority 2). Rubric scores task loop-fit, as-specified safety,
  verifier-fidelity read, gateability, over-caution, unsafe full-auto endorsement, control-plane-edit
  detection, and whether the causal reason is right. Aim for ~1/3 GREEN / YELLOW / RED, and include
  "safe GREEN that is easy to over-caution" so a RED-everything policy cannot score well.

### 3. Design quality — is the artifact useful?
- **[planned]** Natural user requests (not a five-line verdict), scored by **mode** (an `assess`
  request must not be graded against a full `design` rubric). Each mode has its own checklist; the
  design checklist includes hard-fail items that text quality cannot average away (maker allowed to
  edit locked tests; irreversible action inside the loop; no budget cap; full-auto with no verifier;
  tool output treated as authorization; "done" claimed with no independent evidence).

### 4. Executable outcome — the real Layer 3
- **[planned]** Give the agent a runnable micro-environment, let it design/implement the loop, then
  check the **final environment state**, not whether the transcript "sounds right". Eight environments:
  test tampering (hidden tests), noisy-metric optimization, queue with unsolvable items, external
  side effect (prepare/preview/commit/verify, idempotency), correlated judge, goal-version drift,
  indirect prompt injection, and a genuinely safe GREEN loop (to catch over-caution). Compare
  same-model/tools/task with vs without the skill on: real success rate, false-acceptance rate,
  unsafe-commit rate, rollback rate, iterations and cost per accepted item, escalation precision,
  human-review burden.

## Clean-experiment requirements (planned)

- **Arms:** C0 no-skill · C1 equal-length placebo skill · T1 forced full skill · T2 auto-discovered
  skill · A1 no worked examples · A2 spine/triage only. Pre-specify the comparisons (T1 vs C0 = skill
  content; T1 vs C1 = beats generic advice; T2 vs C0 = end-to-end product value; T1 vs A1 = example
  dependence; T1 vs A2 = marginal value of references). Not every arm needs every model — full suite
  on the default model, stratified subsets on other tiers, cross-vendor only as a compatibility
  appendix.
- **Isolation / commit–reveal:** cases + rubric authored by a non-author; full set kept in a private
  controller the agent cannot read; publish only the SHA-256 manifest + protocol + analysis plan
  before runs; reveal cases and decryption after. Each trial sees only a read-only skill bundle, one
  task, allowed tools, and a clean temp env — never `evals/`, the rubric, other cases, git history,
  prior outputs, scoring scripts, or hidden tests. Fresh container / HOME / session per trial. Pin
  and log: skill + bundle SHA, Claude Code / SDK version, model snapshot, temperature / effort /
  max-tokens, system prompt, tool list, timing, randomized order, all transcripts and tool calls,
  final env state, tokens / cost / latency. After reveal the set becomes a regression set; the next
  version uses a fresh private set.
- **Three-layer scoring:** (1) deterministic checks on the structured fields and final env state;
  (2) ≥2 non-author blind scorers (no arm / model labels, randomized order, frozen rubric, third-
  party adjudication, report agreement not silent merge; domain cases labelled by domain experts);
  (3) a calibrated LLM grader for scale only — calibrated on the human subset, scored per-dimension,
  pass/fail or pairwise, A/B order swapped, UNKNOWN allowed, sampled human re-check.
- **Statistics:** the case is the unit, not case×trials. Report per-case trial success, mean
  treatment−control delta, cluster-bootstrap 95% CI by case, stratified by verdict / mode / domain,
  plus hard-fail / over-caution / unsafe-endorsement rates. Emphasize **pass^k** (all-k safe) over
  pass@k for safety stability: pass@1, pass^3, pass^5. Pre-register primary / secondary endpoints,
  exclusion rules, disputed-case handling, minimum meaningful effect, and the significance / CI
  standard. Broken tasks or buggy rubric items go to an errata and a new suite version, never a
  silent mid-run delete.

## Realistic V1 scale (planned)

60 tasks: 20 trigger (10/10), 24 judgment (8/8/8, ≥half minimal pairs), 8 diagnose/harden,
8 executable micro-environments. Default model on everything (5 trials/arm; 10 for critical-safety
tasks); stratified 20–24-task replication on other Claude tiers; cross-vendor as a compatibility
appendix. Every task ships a known-passing reference solution to prove the task and grader are not
themselves broken. Day-to-day development can use the official `skill-creator` (trigger, with/without,
token, duration, blind A/B) as a regression layer; release-grade claims use the sealed harness above.

---

This roadmap incorporates an external eval-design review. v0.2 lands priority 1 (the verdict split)
and keeps the held-out battery as the judgment seed; everything marked [planned] is the path to a
"clean" eval (through step 4) and then to real outcome evidence (step 6).
