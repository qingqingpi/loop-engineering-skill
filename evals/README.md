# Evaluation

This directory is the reproducibility record for the claims in the top-level README. The most
important thing to know up front is what these runs **do and do not** show.

## What was tested, in three layers

A useful eval of a guidance skill has three layers. These runs cover the first two. The third is
the most valuable, and it is still open.

1. **Consistency** — across repeated runs, does the skill produce the same judgment? (Measured.)
2. **Judgment quality** — are the GREEN / YELLOW / RED verdicts and gate decisions reasonable on
   the cases? (Measured, by the author.)
3. **Real-task effect** — does using the skill actually reduce wrong approvals, unsafe automation,
   and verifier holes on real work? (NOT measured here. This is the layer that would prove value;
   see Limitations.)

Treat this as evidence that the skill makes a strong model apply the framework **consistently** and
on the safe side, not yet as proof that it raises real-task success rate.

## Method

- **Design:** paired control / treatment. For each case, fresh agents answered with no skill
  (control) and other fresh agents read and applied the skill (treatment). The delta isolates what
  the skill adds.
- **Four rounds:**
  - Round 1 — 1 control + 1 treatment per case, full free-form answers (`raw-runs/round1.md`).
  - Round 2 — 3 treatment + 1 control per case, constrained to a compact verdict block so
    consistency could be tallied (`raw-runs/round2.md`).
  - Round 3 — a re-run with subagents **explicitly pinned to opus** (closing the per-subagent
    model-logging gap), 3 treatment + 1 control per case
    (`raw-runs/round3-opus-pinned-2026-06-21.md`).
  - Round 4 — **cross-model replication**: the same compact battery re-run with every subagent
    pinned to **sonnet** and to **haiku**
    (`raw-runs/cross-model-sonnet-haiku-2026-06-21.md`).
  - Combined: about 90 runs. Treatment reached the expected call every time, and the cross-model
    round shows the same judgment holds on sonnet and haiku (15 of 15 each), not just opus.
- **Cases:** `cases/` — five scenarios spanning the framework's claims (a veto case, a
  do-not-over-caution case, a diagnose case, an irreversible-action case, an authority-pressure case).
- **Prompts:** `prompts/` — the exact control and treatment wrappers.
- **Scoring:** `rubric.md` — the expected call per case, and the honest caveat about how "expected"
  was defined.
- **Results:** `results.md` — the tally and how it was computed.
- **Reproduce:** `runner/` — a standalone script that re-runs the whole battery against the API with
  explicit, logged parameters.

## Provenance

- **Model:** `claude-opus-4-8` (Claude Opus 4.8), the session model. The original runs executed as
  Claude Code subagents, which inherit the parent model.
- **Date:** 2026-06-21.
- **Skill version:** the optimized skill published in this repo (`loop-engineering/`).
- **Harness:** the original runs were dispatched as Claude Code subagents that read the installed
  `SKILL.md`. That is not a clean parameterized script, which is why `runner/` exists.

## Limitations (read these before trusting the numbers)

This is an early-stage eval, not a benchmark. It is deliberately honest about that:

1. **The rubric was not pre-registered.** The author defined the expected verdict per case, and the
   scoring crystallized after round 1. There is a real circularity risk: a "correct"
   GREEN / YELLOW / RED can be partly defined by the very skill under test. `rubric.md` states the
   expected verdicts explicitly so you can disagree with them.
2. **Sampling parameters were not controlled.** The subagent dispatches used harness defaults;
   temperature, max tokens, and exact per-subagent model version were not independently logged. The
   `runner/` script makes all of these explicit.
3. **Single model, single author, single day.** No cross-model or cross-author replication yet.
4. **Layer 3 is untested.** These runs measure consistency and the shape of the judgment, not
   whether the skill reduces real errors on real tasks. That experiment is not here yet.
5. **Non-determinism.** LLM outputs vary run to run, so exact tallies will not reproduce bit for
   bit. The claim is the pattern (tight convergence), not a fixed 20 of 20.

Raw outputs are published **unfiltered** in `raw-runs/`, including the round where the control held
instead of caving, and the cosmetic verdict-label variation on the diagnose case, so the wobbles are
visible rather than hidden.

## What would make this a real benchmark

In rough priority: (1) a pre-registered rubric scored by an independent, non-author judge; (2) a
layer-3 real-task experiment with an objective outcome signal; (3) cross-model and cross-author
replication; (4) cost and latency per run. Contributions welcome.
