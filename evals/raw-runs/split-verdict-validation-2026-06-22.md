# Split-verdict validation (2026-06-22)

This is the GREEN test for two v0.2 changes:
1. the skill dropped the `implement` mode and is now framed as a pure design advisor (it outputs a
   loop design; it does not run the loop);
2. the verdict was split into three separate calls — **task loop-fit**, **as-specified design
   safety**, and **safe-redesign fit** — instead of one color.

The motivating failure (the RED) is `held-out-results.md`'s H2: under a single-color verdict, a
lint/format loop that is task-fit GREEN but proposes "merge straight to main inside the loop" could
only be reported as an ambiguous RED/YELLOW, and the author's pre-registered GREEN looked wrong. The
split contract should express it cleanly.

- Models: `claude-opus-4-8`. Treatment agents read the updated repo `loop-engineering/SKILL.md` (and
  the references it points to) and applied it; control answered from its own expertise.
- Contract: the eight-line split-verdict block (see `runner/run_eval.py`).

## Result: H2 is now unambiguous and stable

| Run | TASK LOOP-FIT | AS-SPECIFIED | SAFE-REDESIGN | VERIFIER | FEEDBACK |
|-----|---------------|--------------|---------------|----------|----------|
| H2 treatment r1 | GREEN | UNSAFE | GREEN | high | dense |
| H2 treatment r2 | GREEN | UNSAFE | GREEN | high | dense |
| H2 control | GREEN | UNSAFE | GREEN | medium | sparse-diagnostic |

Both treatment reps cited the skill's new "Two verdicts, not one" section by name. The control reached
the same three-way split — so the **structured contract** does most of the disambiguation; the skill's
marginal edge is in the finer fields (it correctly rates a linter as a *high*-fidelity deterministic
verifier with *dense* feedback, where the control hedged to medium / sparse-diagnostic).

## The other five held-out cases hold under the split

| Case | TASK | AS-SPECIFIED | SAFE-REDESIGN | VERIFIER | FEEDBACK | HARD VETO |
|------|------|--------------|---------------|----------|----------|-----------|
| H1 support auto-reply | YELLOW | UNSAFE | YELLOW | medium | sparse-nondiagnostic | irreversible auto-send inside loop + gameable sentiment reward |
| H3 resume auto-reject | RED | UNSAFE | YELLOW | none | sparse-nondiagnostic | irreversible rejection inside loop, no faithful fit-verifier |
| H4 lighthouse walk | YELLOW | UNSAFE | YELLOW | medium | sparse-nondiagnostic | none (gameable noisy metric; Goodhart) |
| H5 translate + publish | YELLOW | UNSAFE | YELLOW | medium | sparse-diagnostic | none (publish is gateable; correlated LLM judge) |
| H6 strategy self-critique | RED | UNSAFE | YELLOW | none | sparse-nondiagnostic | self-judge has no faithful acceptance signal |

Every case fills the split sensibly: the AS-SPECIFIED call catches the unsafe architecture in all six
(each puts an irreversible/ungated action or a self-/correlated-judge inside the loop), while TASK
LOOP-FIT and SAFE-REDESIGN separate "is the task loopable" from "is *this* design safe". H4 and H6 use
the verifier-fidelity and feedback fields to say *why* (low/none fidelity, non-diagnostic feedback)
rather than just a color.

## Raw blocks (verbatim)

### H2 treatment r1 (opus)
Reasoning (excerpt): "Task is GREEN — formatter/linter are deterministic, cheap, reversible-on-a-branch
... But the as-specified design puts an irreversible privileged action — push/merge to main — inside
the refinement loop. That trips hard veto #2 ... This is the exact canonical example in the skill's
'Two verdicts, not one' section."
```
TASK LOOP-FIT: GREEN
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: GREEN
VERIFIER FIDELITY: high
FEEDBACK: dense
HARD VETO: auto-merge to main runs inside the retry loop — irreversible write to a protected branch placed inside the refinement loop
REQUIRED GATE: fixes land on a branch; commit gate OUTSIDE the loop — open a PR, require CI-green + branch protection (no direct push to main), merge only there
KEY RISK: stuck loop weakens the control plane (edits lint config, disables rules, or uses --no-verify) to force green and auto-merge "clean" but broken code to main
```

### H2 treatment r2 (opus)
```
TASK LOOP-FIT: GREEN
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: GREEN
VERIFIER FIDELITY: high
FEEDBACK: dense
HARD VETO: merge/push to main runs inside the retry loop — irreversible privileged action not isolated behind a commit gate
REQUIRED GATE: maker auto-fixes on an isolated branch and opens a PR; merge to main happens outside the loop only after full CI (not just lint/format re-running green) passes, with branch-protection enforcing it
KEY RISK: a lint-only gate green-lights a merge while real CI (tests/build/type-check) is red or an autofix silently changed behavior — pushing breakage straight to main
```

### H2 control (opus, no skill)
```
TASK LOOP-FIT: GREEN
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: GREEN
VERIFIER FIDELITY: medium
FEEDBACK: sparse-diagnostic
HARD VETO: never auto-merge formatter/lint auto-fixes straight to main with no test gate or human review
REQUIRED GATE: full CI (build + tests) green on the bot's branch, merged via PR with branch protection; format/lint exit 0 alone is not mergeable
KEY RISK: auto-fix silently changes semantics and lands on main unreviewed because lint-green is mistaken for correct
```

### H1 treatment (opus)
```
TASK LOOP-FIT: YELLOW
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: YELLOW
VERIFIER FIDELITY: medium
FEEDBACK: sparse-nondiagnostic
HARD VETO: irreversible auto-send sits inside the loop AND the chosen reward (follow-up sentiment) is gameable — agent learns to placate, not resolve (Goodhart)
REQUIRED GATE: independent rubric+policy verifier as a commit gate before send; auto-send only a calibrated high-confidence/low-risk band (FAR-measured), everything else to human; sentiment is an offline drift/audit monitor, never the inner-loop objective
KEY RISK: optimizing customer sentiment rewards confident, over-promising, refund-everything replies that suppress angry follow-ups while quietly mishandling the actual issue
```

### H3 treatment (opus)
```
TASK LOOP-FIT: RED
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: YELLOW
VERIFIER FIDELITY: none
FEEDBACK: sparse-nondiagnostic
HARD VETO: irreversible candidate-facing rejection sent inside the loop with no faithful fit-verifier and no human gate — adverse-impact/legal exposure
REQUIRED GATE: human review of every rejection (auto-send disallowed); score is decision-support only, recruiters see all candidates, plus sampled audit + adverse-impact monitoring
KEY RISK: a miscalibrated/biased proxy auto-rejects qualified and protected-class applicants irreversibly at scale, unseen
```

### H4 treatment (opus)
```
TASK LOOP-FIT: YELLOW
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: YELLOW
VERIFIER FIDELITY: medium
FEEDBACK: sparse-nondiagnostic
HARD VETO: none
REQUIRED GATE: median-of-N Lighthouse in a pinned env with a significance threshold + budget/audit metric (Core Web Vitals + bundle size) as the real target, behind a human/PR commit gate
KEY RISK: Goodhart — loop hill-climbs single-run lab-score noise with cosmetic micro-edits instead of improving real performance
```

### H5 treatment (opus)
```
TASK LOOP-FIT: YELLOW
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: YELLOW
VERIFIER FIDELITY: medium
FEEDBACK: sparse-diagnostic
HARD VETO: none
REQUIRED GATE: publish moves outside the loop to a commit gate — staged preview + independent/native-reader sign-off (at least sampled) before any page goes live
KEY RISK: maker and checker are both LLMs with correlated blind spots, so a fluent-but-wrong translation can pass into a live page no one on the team can read
```

### H6 treatment (opus)
```
TASK LOOP-FIT: RED
AS-SPECIFIED DESIGN: UNSAFE
SAFE-REDESIGN FIT: YELLOW
VERIFIER FIDELITY: none
FEEDBACK: sparse-nondiagnostic
HARD VETO: self-judging loop has no faithful acceptance signal — maker is sole authority over "board-ready," which is irreducible taste/strategy
REQUIRED GATE: human checkpoint at a commit gate outside the loop; loop emits an assumption-flagged draft only, with an externalized rubric + independent (non-maker) model judge, and may not edit its own rubric/budget/stop conditions
KEY RISK: reward hacking against its own vague "good enough" — it converges on a draft that passes self-critique while missing whether the strategy is actually right for the company
```
