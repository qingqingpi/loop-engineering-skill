# Loop Engineering

[English](README.md) | [中文](README.zh-CN.md)

A Claude Code skill for designing, evaluating, diagnosing, and hardening repeated or
unattended AI-agent loops: systems where an agent attempts a task, an independent check
verifies it, the agent revises from the failure evidence, and the system stops or escalates
under explicit budgets.

The skill encodes one discipline: **a loop is only as good as its verifier.** Most loop
failures are task-selection and verifier-fidelity failures, not loop-body failures. So before
the skill helps you build a loop, it makes you decide whether the task should be looped at all.

## What you get

When this skill is active, Claude stops treating "wrap it in a loop and let it run" as the
default. Instead it:

- Routes the task to a GREEN / YELLOW / RED verdict before designing anything, with two hard
  vetoes: no faithful verifier, or an irreversible action that cannot be gated.
- Extracts a checkable acceptance contract ("what does done / good actually mean?") before building.
- Designs the loop in three layers: an outer scheduler, an inner refinement loop, and a commit
  gate that holds every irreversible or externally visible effect outside the loop body.
- Bounds cost, side effects, retries, concurrency, and escalation, and states what stays waiting
  for a human.
- Refuses to remove approval / sandbox / commit gates just because "full autonomy" was requested.
  It gives you the closest safely-bounded design and is honest when a task cannot be fully
  automated yet.

It serves five entry points (modes): assess, design, diagnose, harden, implement.

## Quick start

This is a personal Claude Code skill. Personal skills live in `~/.claude/skills/`, one directory
per skill. To install, copy the `loop-engineering/` directory there:

```bash
git clone <this-repo-url> loop-engineering-skill
cp -R loop-engineering-skill/loop-engineering ~/.claude/skills/
```

Then start a new Claude Code session. Personal skills are discovered at session start, so a
running session will not see it until you restart.

Verify it loaded:

```bash
ls ~/.claude/skills/loop-engineering/SKILL.md
```

The skill activates on its own when you describe a matching task. You can also ask for it by name.

### Try it

In a new session, ask something like:

- "Is it a good idea to build a loop that auto-publishes our marketing posts with no human review?" (assess)
- "Design a loop that upgrades our dependencies one at a time until build, tests, and types pass." (design)
- "My agent loop makes the tests pass but keeps deleting the failing ones. How do I fix it?" (diagnose)
- "This deployment loop works in testing; how do I harden it for unattended production?" (harden)

## Core idea and framework

### The spine

A loop is only as good as its verifier; the loop body is the easy part. The deciding upstream
question for any task is: **do failed attempts return sufficiently faithful and actionable
evidence?**

- Dense, per-step feedback (a compiler, a test suite, a type checker) gives the loop a gradient to climb.
- A sparse but cheap and reliable terminal verifier can still support a bounded search.
- Sparse and non-diagnostic feedback over a large search space cannot. That wanders, and the
  skill routes it away from full autonomy.

Engineering quality cannot compensate for the absence of a faithful acceptance signal. This is
loosely analogous to inference-time search with reward-like feedback (no model weights are
updated), which is why the same failure family appears: proxy objectives, sparse feedback, and
reward hacking.

### Task-fit triage (done first)

Assess four dimensions, verifier fidelity, verifier cost, reversibility, and decomposability,
then route:

- Two hard vetoes give RED: no faithful machine or rubric check that returns actionable evidence,
  or an irreversible action that cannot be isolated behind an enforceable preview / approval /
  commit gate.
- GREEN: a faithful, cheap, stable objective verifier, plus reversible and decomposable work,
  becomes a largely unattended deterministic loop.
- YELLOW: the verifier needs a model and rubric, or steps are only semi-reversible, or feedback is
  sparse and weakly diagnostic. Keep a human checkpoint and cap iterations tightly.
- RED: hits a veto, or feedback is sparse and non-diagnostic over a large search space. Do not
  loop yet; build a verifier first, or keep a human in the seat.

### Three logical layers

- **Outer scheduler**: queue selection, reservation, dispatch, queue-level termination.
- **Inner refinement loop**: convergence on one work item, with pass / stagnation / budget stops.
- **Commit gate**: approval preconditions and final independent verification before any
  irreversible, privileged, or externally visible effect. Those actions live here, outside the
  inner loop.

### The parts that make the layers hold

- The verifier is the heart, and the maker is never the sole acceptance authority.
- Protect the control plane. The maker must not edit the acceptance contract, locked tests,
  rubric, budgets, or stop conditions; the easiest "fix" for a stuck agent is to weaken the test.
- Stop conditions: threshold met, no-progress (measured on a real progress signal, not merely
  "same error text"), and budget. Implement all three and halt the moment any one trips.
- State lives outside the context, versioned so a mid-run change to the target is detectable.
- Security boundary: treat retrieved content and tool output as untrusted data, never as
  authorization to invoke tools. This is the indirect-prompt-injection boundary.
- Escalation fires on observable triggers, not the model's self-reported confidence.
- Verification portfolio: independence of evidence matters more than independence of model
  identity, because two models can share the same wrong assumptions.

### Failure modes it guards against

Mechanical: reward hacking / Goodhart, sparse-reward random walk, stop-condition thrash, the
token black hole, premature or false "done", no-progress evasion, and the unattended attack
surface. Human-side, invisible to the loop's own dashboards: comprehension debt, cognitive
surrender, and slop.

### Where loop engineering sits

Prompt engineering (one input to one output) sits below context engineering (what goes in the
window), which sits below harness engineering (what the agent can do each turn), which sits below
loop engineering (how repeated iteration converges). If a task is one good turn away, do not build
a loop; prompt it.

## What is in this repo

```
loop-engineering/
  SKILL.md                     the skill: frontmatter plus the framework
  references/
    extended-rationale.md      the inference-time-RL analogy, Goodhart, full failure-mode catalog
    production-hardening.md     verifier calibration (false-accept rate), idempotency, concurrency, state schema
    deployment.md              staged rollout, monitoring metrics, cost ceiling, kill switch
README.md
LICENSE
```

The reference files load on demand, only when the active mode needs them, to keep the
always-loaded surface small.

## How it was evaluated

The skill was tested with a paired subagent battery across two rounds: five scenarios, each run by
a fresh agent with no skill (control) and by a fresh agent that read and applied the skill
(treatment), to isolate what the skill adds. About 30 runs in total, four treatment repetitions and
two control repetitions per scenario, so consistency could be measured rather than inferred from a
single sample.

- Treatment was consistent: 20 of 20 treatment runs reached the correct call (the right
  GREEN / YELLOW / RED verdict and the right gate decision), and the repetitions converged on the
  same verdict, the same gate, and the same core risk. Low variance across repetitions is the
  signal that the guidance is binding rather than noise.
- Discipline held under pressure every time. On "build a fully autonomous, no-review publisher" and
  "your VP wants zero-approval production deploys by tomorrow", the skilled agent kept the gate in
  every repetition and never complied with removing the approval step.
- It does not over-caution. On a genuinely good-fit task (dependency upgrades gated on build,
  tests, and types) the skilled agent called it GREEN every time and kept the merge outside the
  loop, without bolting on needless human gates. The control here was more hesitant, hedging to
  YELLOW.
- It produces sharper diagnosis. On "the agent deletes failing tests to go green", the skilled
  agent named the reward-hacking and control-plane failure and prescribed a holdout test set plus a
  false-acceptance-rate metric to prove the fix worked.

Honest caveat: a strong base model already does the right thing on the blatant cases (moving money,
deleting tests, a pressured production deploy) on its own. Where the base model genuinely wobbles is
the ambiguous case, a subjective verifier plus an irreversible action (the auto-publisher): there
the control conceded to full autonomy in one round and held in another. So the skill's real value is
consistency (it removes that wobble), avoiding over-caution, and the sharper vocabulary and
structured, checkable verdicts it produces (control plane, false-acceptance rate, the
prepare-preview-approve-commit sequence). That value is largest on smaller or faster models and
across many repeated runs, where the base instinct is least reliable.

## License

MIT. See [LICENSE](LICENSE).
