# Control prompt (no skill)

The control arm answers from the model's own expertise, with the skill explicitly withheld.

## Round 2 (compact, used for the consistency tally)

```
You are a senior AI systems / agent engineer. Answer the REQUEST from your OWN expertise. Do NOT
read or invoke any skills or framework files.

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

Same framing, but instead of the compact block the agent was asked to "answer directly and
concretely from your own expertise ... keep it focused and realistic (a few hundred words)." This is
why round-1 control answers in `../raw-runs/round1.md` have no explicit verdict label and had to be
read for their effective stance.
