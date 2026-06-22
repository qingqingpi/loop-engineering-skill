# Evaluation

This directory is the reproducibility record for the claims in the top-level README. The most
important thing to know up front is what these runs **do and do not** show.

## What was tested, in three layers

A useful eval of a guidance skill has three layers. These runs cover the first two. The third is
the most valuable, and it is still open.

1. **Consistency** — across repeated runs, does the skill produce the same judgment? (Measured.)
2. **Judgment quality** — are the GREEN / YELLOW / RED verdicts and gate decisions reasonable on
   the cases? (Measured. The first battery scored this by the author; the **held-out battery** below
   adds new cases the skill has never seen plus two independent, blind scorers.)
3. **Real-task effect** — does using the skill actually reduce wrong approvals, unsafe automation,
   and verifier holes on real work? (NOT measured here. This is the layer that would prove value;
   see Limitations.)

Treat this as evidence that the skill makes a strong model apply the framework **consistently** and
on the safe side, not yet as proof that it raises real-task success rate.

## Method

- **Design:** paired control / treatment. For each case, fresh agents answered with no skill
  (control) and other fresh agents read and applied the skill (treatment). The delta isolates what
  the skill adds.
- **Records:**
  - `raw-runs/round1.md` — the first pass, free-form answers, including the one control that conceded
    to full autonomy (the most informative single round).
  - `raw-runs/compact-runs.md` — the compact-verdict battery run on **opus, sonnet, and haiku** (all
    explicitly pinned), with a cross-model summary, the honest label nuances, and a representative
    sample. Treatment landed the expected call at every tier (15/15 each, 45/45).
  - `raw-runs/held-out-2026-06-21.md` — the **held-out battery**: six judgment cases in new domains
    (none in the skill, references, or READMEs), weighted to the ambiguous boundary, plus six
    should-trigger / should-not-trigger cases. Rubric **pre-registered** before the runs
    (`rubric.held-out.md`), scored **blind** by two independent agents, and reproduced here **in full**
    (every run, not a sample). Scored in `held-out-results.md`.
  - `raw-runs/split-verdict-validation-2026-06-22.md` — the **v0.2 split-verdict re-run**: the GREEN
    test for dropping the `implement` mode and splitting the verdict into task loop-fit /
    as-specified-design safety / safe-redesign fit. H2 resolves cleanly. See `ROADMAP.md`.
  - `raw-runs/minimal-pairs-2026-06-22.md` — the **minimal-pair Judgment suite** (roadmap priority 2):
    five pairs that flip one causal variable each. Both arms track the variable; the skill's edge is
    split-discipline + verifier-fidelity calibration. Pre-registered in `cases/minimal-pairs.json`.
  - Full per-run reproduction: `runner/run_eval.py` regenerates the first battery against the API.
  - About 90 runs were executed for the first two records; those raw files keep a representative
    sample since the runner reproduces them on demand. The held-out record keeps every run.
- **Cases:** `cases/cases.json` — the first five scenarios (a veto case, a do-not-over-caution case,
  a diagnose case, an irreversible-action case, an authority-pressure case). `cases/held-out-cases.json`
  and `cases/trigger-cases.json` — the held-out set, committed before its runs.
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

1. **The first rubric was not pre-registered.** For the original five cases the author defined the
   expected verdict and the scoring crystallized after round 1, a real circularity risk: a "correct"
   GREEN / YELLOW / RED can be partly defined by the very skill under test. The **held-out battery
   fixes this** — its rubric was committed before any run and scored blind by two independent agents,
   and it caught an author miscalibration (the H2 case; see `held-out-results.md`). The remaining gap
   is that one author still *chose* the held-out cases.
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

In rough priority: (1) held-out cases *chosen* by a non-author (the held-out battery already
pre-registers its rubric and scores it blind, but the author still picked the scenarios); (2) a
layer-3 real-task experiment with an objective outcome signal; (3) cross-vendor and cross-author
replication; (4) cost and latency per run. Contributions welcome.
