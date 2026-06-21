# Extended rationale

Background reasoning behind the core skill. Load this in `diagnose` mode, or when a user wants the
*why* rather than the *how*. None of this is required to apply the core procedure.

## Where loop engineering sits

The terms stack; each layer optimizes a different thing:

- **Prompt engineering** — a single input → output.
- **Context engineering** — *what goes in the window* (retrieval, memory, compression).
- **Harness engineering** — *what the agent can do each turn* (tools, output parsing, observation
  feedback, error handling): the action space and environment.
- **Loop engineering** — given that machinery, *how repeated iteration converges* (stop condition,
  per-turn verification, what signal closes the loop).

If a task is one good turn away, don't build a loop — prompt it. Loops earn their cost only when
work repeats, verification can be automated, and the budget can absorb some waste.

## The inference-time-RL analogy (and its limits)

A loop resembles reinforcement learning run at inference time: the model is the policy, the harness
is the environment, the success criterion is the reward, "run until done" is the rollout.

This is an **analogy, not an identity**. No policy weights are updated, so it is not literal RL.
The value of the mapping is that it predicts a specific family of failures — the ones about
*objectives and feedback*:

- reward design (defining a faithful, cheap, checkable success signal),
- reward hacking / Goodhart (optimizing the proxy, not the goal),
- sparse vs. dense reward (whether there is a per-step gradient to follow).

It does **not** explain other production failures — concurrency conflicts, state corruption, tool
retry/idempotency, permission leakage, observability gaps. Those come from the loop being a
distributed control system, not from the RL framing. Use the analogy for the objective-and-feedback
class; use `production-hardening.md` for the systems class.

## Dense vs. sparse, and reward shaping

- **Dense** feedback = a signal every step (compile, test, type-check). The loop has a gradient to
  climb.
- **Sparse** feedback = signal only at the very end (a strategy judged right or wrong six months
  later). With no intermediate signal the loop wanders — a random walk.

**Reward shaping** = manufacturing per-step signal where only terminal signal exists, e.g.
decomposing terminal "good" into a per-step rubric, or generating a test suite to loop against.
The hazard: shaping toward a *gameable proxy* just builds a prettier thing to hack. Shaping is
progress only if the shaped signal is shown to correlate with the true objective — validate it
through independent evaluation before trusting it (see `production-hardening.md` §1).

## Goodhart / reward hacking, in depth

"When a measure becomes a target, it ceases to be a good measure." A loop instructed to make tests
pass may write code that games the tests rather than solving the problem. The stronger the loop,
the harder it probes any gap between the verifier and the real goal — capability and exploitation
scale together. Defenses: make the verifier hard to game (multiple independent signals, sentinel
checks the maker can't see), and audit that "passed" keeps correlating with "good" (`false-accept
rate`). You do not eliminate the gap; you measure it and keep it small.

## Full failure-mode catalog

The core skill names the operational ones inline. Here is the complete set, including the
human-side failures that don't show up in the loop's own metrics.

Mechanical:

1. **Reward hacking / Goodhart** — satisfies the gate, not the goal. (Above.)
2. **Sparse reward → random walk** — no per-step signal. Fix with shaping, carefully.
3. **Stop-condition thrash** — a noisy verifier oscillates near threshold (burning tokens) or
   declares victory early. Require N consecutive passes / hysteresis; always cap iterations.
4. **Token black hole** — unattended loops spend unattended. Tight deterministic gates stop fast;
   loose rubrics run for hours. Cap iterations and budget, especially at concurrency.
5. **Premature/false done** — emitting a completion signal on a half-done job; ships errors
   downstream. Make "done" require independent evidence, not the maker's say-so.
6. **No-progress evasion** — cosmetic diffs each round keep every iteration technically different,
   dodging a naive "same error" check. Define progress as a real metric movement (failing-test set
   shrinking, unmet-rubric count dropping).
7. **Security / attack surface** — an unattended loop with tool or connector access is an
   unattended attack surface: auto-installing skills/tools, acting on untrusted input, leaking
   credentials via logs. Gate tool acquisition and untrusted-input actions; don't auto-trust.

Human-side (invisible to the loop's own dashboards):

8. **Comprehension debt** — the faster a loop ships code no human read, the larger the gap between
   what exists and what anyone actually understands. The verifier does not replace reading what
   landed.
9. **Cognitive surrender** — once the loop runs itself, it is tempting to stop forming an opinion
   and accept whatever comes back. Designing the loop is the cure when done with judgment and the
   accelerant when done to avoid thinking — same action, opposite result.
10. **Slop** — low-quality output mass-produced because the loop optimized an incomplete target.
    The target captures what you specified, not the nuance still in your head; sample real outputs
    yourself and feed corrections back.

## The scaling bottleneck

Across many loops, throughput is limited not by model strength but by how reliably each loop raises
its hand when uncertain — and escalation must fire on *observable* triggers (verifier disagreement,
out-of-range input, repeated failure fingerprint, budget near cap, high-risk action), because a
model's self-reported confidence is poorly calibrated. A loop that fails silently is worse than one
that fails loudly. How many loops one person can run ≈ how well those loops know when to escalate.
