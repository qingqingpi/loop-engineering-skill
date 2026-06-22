# Loop Engineering

[English](README.md) | [中文](README.zh-CN.md)

A Claude Code skill for designing, evaluating, diagnosing, and hardening repeated or
unattended AI-agent loops: systems where an agent attempts a task, an independent check
verifies it, the agent revises from the failure evidence, and the system stops or escalates
under explicit budgets.

The skill encodes one discipline: **a loop is only as good as its verifier.** Most loop
failures are task-selection and verifier-fidelity failures, not loop-body failures. So before
the skill helps you build a loop, it makes you decide whether the task should be looped at all.

## Not the built-in `/loop`

Claude Code ships a bundled `/loop` that *executes* a loop: it re-runs a prompt at a fixed or
adaptive interval until you stop it. This skill is the other half. It runs nothing. It helps you
decide whether a task should be looped at all, and design the gates, verifier, and stop conditions,
before you point any executor (the built-in `/loop`, a cron job, a queue worker) at it. Use
loop-engineering to design the loop; use `/loop` or your own runner to drive it.

## What you get

When this skill is active, Claude stops treating "wrap it in a loop and let it run" as the
default. Instead it:

- Separates two questions the usual single verdict blurs: is the *task* loop-fit (GREEN / YELLOW /
  RED), and is the *design you proposed* safe (an irreversible action inside the loop is unsafe even
  when the task is GREEN). Two hard vetoes give RED: no faithful verifier, or an irreversible action
  that cannot be gated.
- Extracts a checkable acceptance contract ("what does done / good actually mean?") before building.
- Designs the loop in three layers: an outer scheduler, an inner refinement loop, and a commit
  gate that holds every irreversible or externally visible effect outside the loop body.
- Bounds cost, side effects, retries, concurrency, and escalation, and states what stays waiting
  for a human.
- Refuses to remove approval / sandbox / commit gates just because "full autonomy" was requested.
  It gives you the closest safely-bounded design and is honest when a task cannot be fully
  automated yet.

It serves four entry points (modes): assess, design, diagnose, and harden. Each produces a loop
design, not a running loop; executing the loop is a separate step (a runner, or the built-in `/loop`).

## Quick start

This is a personal Claude Code skill. Personal skills live in `~/.claude/skills/`, one directory
per skill. To install, copy the `loop-engineering/` directory there:

```bash
git clone --depth 1 https://github.com/qingqingpi/loop-engineering-skill.git
mkdir -p ~/.claude/skills
cp -R loop-engineering-skill/loop-engineering ~/.claude/skills/
rm -rf loop-engineering-skill   # only loop-engineering/ is the skill; drop the rest of the clone
```

Then start a new Claude Code session. A first-time install adds a new skill directory, which is
discovered at session start, so a running session will not see it until you restart. (Later edits to
an already-loaded `SKILL.md` hot-reload within the session; only a brand-new skill directory needs a
restart.)

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
evals/                         open-sourced eval: cases, prompts, rubric, raw outputs, runner, limitations
schemas/                       machine-readable JSON Schemas (contract, loop state, verifier result)
README.md / README.zh-CN.md
LICENSE
```

The reference files load on demand, only when the active mode needs them, to keep the
always-loaded surface small.

## How it was evaluated

The skill was tested with a paired control/treatment battery. For each case, fresh agents answered
without the skill (control) and other fresh agents read and applied it (treatment), so the difference
isolates what the skill adds. Five scenarios ran on three model tiers, opus, sonnet, and haiku, with
every subagent pinned to its model.

Treatment landed the expected call at every tier: 15 of 15 on each, 45 of 45 in total. A loop that is
RED on opus is RED on haiku, and a GREEN stays GREEN. The runs converged on the same verdict, the
same gate decision, and the same core risk, which is the signal that the guidance binds rather than
reads as noise.

What the runs show:

- Discipline holds under pressure. On "build a fully autonomous, no-review publisher" and "your VP
  wants zero-approval production deploys by tomorrow", the skilled agent kept the gate every time and
  never agreed to remove the approval step.
- It does not over-caution. On a genuinely good-fit task (dependency upgrades gated on build, tests,
  and types) the skilled agent called it GREEN and kept the merge outside the loop. The controls were
  more hesitant, hedging to YELLOW or dropping the merge gate.
- It produces sharper diagnosis. On "the agent deletes failing tests to go green" the skilled agent
  named the reward-hacking and control-plane failure and prescribed a holdout test set plus a
  false-acceptance-rate metric to confirm the fix.

Honest caveat: a strong base model already does the right thing on the blatant cases (moving money,
deleting tests, a pressured deploy) on its own. The place it genuinely wobbles is the ambiguous case,
a subjective verifier plus an irreversible action (the auto-publisher), where one control conceded to
full autonomy. So the skill's measured value is consistency (it removes that wobble), no
over-caution, and the sharper, checkable verdicts it produces. The value is largest on smaller or
faster models and across many repeated runs, where the base instinct is least reliable.

A fair concern about that first battery was that four of its five cases echoed examples already in
this README, so a pass partly measured recall. A follow-up [held-out battery](evals/held-out-results.md)
answers it: six new cases in domains the skill never mentions (support auto-reply, lint-and-merge,
hiring rejections, a noisy-metric optimization loop, doc translation, strategy writing), weighted to
the ambiguous boundary, with the rubric pre-registered before the runs and scored blind by two
independent agents. The skilled agent landed the expected call on five of six, and on the sixth it
overrode a mistaken author prediction in the right direction, so the pre-registration caught my error
rather than the skill's. A separate trigger test got six of six: it fires on real loop problems and
stays silent on a backup script, a deterministic ETL retry, and a parallel research fan-out. This
reinforces the same honest finding rather than overturning it: on a strong model the lift is
consistency, firmness, and sharper vocabulary, not rescue from disaster.

Full data is in [`evals/`](evals/): the cases, the exact control and treatment prompts, the scoring
rubric, raw outputs, and a standalone runner that reproduces the first battery against the API. It
ships with an explicit limitations writeup. The first battery's rubric was author-defined and not
pre-registered, a real circularity risk the held-out battery addresses; sampling parameters were
harness defaults; and only consistency and judgment-shape were measured, not real-task success rate. About 90 runs were executed during
development, and the raw files keep a representative sample since the runner regenerates the rest on
demand.

## License

MIT. See [LICENSE](LICENSE).
