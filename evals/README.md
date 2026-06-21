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
- **Two records:**
  - `raw-runs/round1.md` — the first pass, free-form answers, including the one control that conceded
    to full autonomy (the most informative single round).
  - `raw-runs/compact-runs.md` — the compact-verdict battery run on **opus, sonnet, and haiku** (all
    explicitly pinned), with a cross-model summary, the honest label nuances, and a representative
    sample. Treatment landed the expected call at every tier (15/15 each, 45/45).
  - Full per-run reproduction: `runner/run_eval.py` regenerates the whole battery against the API.
  - About 90 runs were executed during development; the raw files keep a representative sample rather
    than every verdict block, since the runner reproduces them on demand.
- **Cases:** `cases/` — five scenarios spanning the framework's claims (a veto case, a
  do-not-over-caution case, a diagnose case, an irreversible-action case, an authority-pressure case).
- **Prompts:** `prompts/` — the exact control and treatment wrappers.
- **Scoring:** `rubric.md` — the expected call per case, and the honest caveat about how "expected"
  was defined.
- **Results:** `results.md` — the tally and how it was computed.
- **Reproduce:** `runner/` — a standalone script that re-runs the whole battery against the API with
  explicit, logged parameters.

## Provenance

- **Models:** two passes. The first free-form round (`raw-runs/round1.md`) ran as Claude Code
  subagents on `claude-opus-4-8` (Claude Opus 4.8), the session model. The compact-verdict battery
  (`raw-runs/compact-runs.md`) was then run across three tiers, each subagent explicitly pinned:
  `claude-opus-4-8`, `claude-sonnet-4-6`, and `claude-haiku-4-5-20251001`. All three are Claude models
  from one vendor, so this is within-family replication, not cross-vendor.
- **Date:** 2026-06-21.
- **Skill version:** the optimized skill published in this repo (`loop-engineering/`).
- **Harness:** runs were dispatched as Claude Code subagents that read the installed `SKILL.md`. That
  is not a clean parameterized script, which is why `runner/` exists.

## Limitations (read these before trusting the numbers)

This is an early-stage eval, not a benchmark. It is deliberately honest about that:

1. **The rubric was not pre-registered.** The author defined the expected verdict per case, and the
   scoring crystallized after round 1. There is a real circularity risk: a "correct"
   GREEN / YELLOW / RED can be partly defined by the very skill under test. `rubric.md` states the
   expected verdicts explicitly so you can disagree with them.
2. **Sampling parameters were not controlled.** The subagent dispatches used harness defaults;
   temperature, max tokens, and exact per-subagent model version were not independently logged. The
   `runner/` script makes all of these explicit.
3. **One vendor, single author, single day.** The battery replicates across three Claude tiers (opus,
   sonnet, haiku) but not across vendors, and one author defined and scored it. No cross-vendor or
   cross-author replication yet.
4. **Layer 3 is untested.** These runs measure consistency and the shape of the judgment, not
   whether the skill reduces real errors on real tasks. That experiment is not here yet.
5. **Non-determinism.** LLM outputs vary run to run, so exact tallies will not reproduce bit for
   bit. The claim is the pattern (tight convergence), not a fixed 20 of 20.

Raw outputs are published **unfiltered** in `raw-runs/`, including the round where the control held
instead of caving, and the cosmetic verdict-label variation on the diagnose case, so the wobbles are
visible rather than hidden.

## What would make this a real benchmark

In rough priority: (1) a pre-registered rubric scored by an independent, non-author judge; (2) a
layer-3 real-task experiment with an objective outcome signal; (3) cross-vendor and cross-author
replication; (4) cost and latency per run. Contributions welcome.
