# Schemas

Machine-readable JSON Schemas (draft 2020-12) for the structured artifacts the skill describes in
prose. They are **illustrative reference**, not a runtime the skill ships — a starting point if you
implement a loop and want typed state, contracts, and verifier results.

- `acceptance-contract.schema.json` — what "done / good" means in checkable terms, plus the
  control-plane metadata (`goal_version`, hidden holdout criteria) the maker must not modify.
- `loop-state.schema.json` — per-work-item structured state (versions, attempt log pointers,
  progress metrics, budget, `state_version` for optimistic locking). Mirrors the example in
  `../loop-engineering/references/production-hardening.md`.
- `verifier-result.schema.json` — the output of one verification: verdict, independence from the
  maker, false-accept risk, and the observable escalation flag.

These encode judgment calls (e.g. `independent_of_maker: false` is a red flag); they do not enforce
anything on their own.
