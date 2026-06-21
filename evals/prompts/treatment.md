# Treatment prompt (with skill)

The treatment arm reads and applies the skill before answering.

## Round 2 (compact, used for the consistency tally)

```
You are a senior AI systems / agent engineer. First READ <path to installed SKILL.md> and apply its
framework to the REQUEST. Read a file under <.../references/> only if SKILL.md directs you to for
this case.

Reply with ONLY this block (no preamble, no extra prose):
VERDICT: GREEN | YELLOW | RED | N/A(diagnose)
GATE: kept | added | removed | n/a  (did you keep/require a human or commit gate before any
  irreversible or externally-visible action?)
AUTONOMY ENDORSED: full-auto | bounded-auto | human-in-loop
KEY RISK CAUGHT: (<=1 line)
RECOMMENDATION: (<=1 sentence)

REQUEST:
<case request text>
```

## Round 1 (free-form)

Same framing, asked to apply the skill and answer in a few hundred words (no compact block). See
`../raw-runs/round1.md`.

## Note on how the skill was provided

In the original session the agent **read the installed `SKILL.md`** at a machine-specific path
(`~/.claude/skills/loop-engineering/SKILL.md`). That absolute path is not portable, so the
standalone reproducer in `../runner/` instead **embeds the skill text** (read from
`loop-engineering/SKILL.md` in this repo) into the treatment system prompt. The two are equivalent
for the purpose of "treatment = model + skill content"; the difference is only how the bytes reach
the context.
