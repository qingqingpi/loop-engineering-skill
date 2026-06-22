# Changelog

## 0.2.0 — 2026-06-22

Identity and verdict cleanup, plus an eval roadmap.

### Changed
- **Pure design advisor.** Dropped the `implement` mode; the skill now has four modes (assess,
  design, diagnose, harden) and an explicit identity line: it **designs** loops and outputs a design;
  it does not run them. Executing the loop is a runner's or the built-in `/loop`'s job. This removes
  an over-promise — the skill shipped no implementation assets to back "a working implementation".
  `design` still emits an implementation *sketch* (pseudocode / structure, or concrete code when the
  platform is given) as a design artifact.
- **Split verdict.** The single GREEN/YELLOW/RED color conflated two questions. The skill and the
  eval contract now report three separate calls — **task loop-fit**, **as-specified-design safety**
  (SAFE/UNSAFE/CONDITIONAL), and **safe-redesign fit** — plus verifier fidelity, feedback
  diagnosticity, irreversible actions + gateability, hard-veto, and the required gate. A new
  "Two verdicts, not one" section in SKILL.md explains it. This resolves the H2 case (a task-fit
  GREEN lint loop whose as-specified merge-to-main is UNSAFE), which the old contract could only
  express as an ambiguous RED/YELLOW.
- Eval runner (`evals/runner/run_eval.py`) emits and parses the split-verdict block.

### Added
- `evals/raw-runs/split-verdict-validation-2026-06-22.md` — the GREEN test for the above: H2 now
  resolves cleanly and stably (TASK GREEN / AS-SPECIFIED UNSAFE / SAFE-REDESIGN GREEN), with all six
  held-out cases re-run on the new contract.
- `evals/ROADMAP.md` — the eval plan (trigger / judgment / design-quality / executable-outcome
  suites, commit–reveal isolation, three-layer scoring, statistics, V1 scale), with done / v0.2 /
  planned status. Incorporates an external eval-design review.

### Notes
- Layer 3 (real-task outcome) is still unmeasured; it is the highest-value open item (roadmap step 6).

## 0.1.0 — 2026-06-21

Initial public release: the skill (SKILL.md + references), MIT license, English and Chinese READMEs,
machine-readable JSON schemas, and the open-sourced eval (cases, prompts, rubric, raw outputs, a
standalone API runner, and a pre-registered held-out battery scored blind by two independent agents).
