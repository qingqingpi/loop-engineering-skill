# Runner

A standalone reproducer for the eval battery. It reads the five cases (`../cases/cases.json`) and the
skill (`../../loop-engineering/SKILL.md`), runs each case through a control arm (no skill) and a
treatment arm (skill embedded in the system prompt), and writes raw outputs plus a verdict tally.

## Run it

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install -r requirements.txt
python run_eval.py --model claude-opus-4-8 --treatment-reps 3 --control-reps 1
```

Flags: `--model`, `--treatment-reps`, `--control-reps`, `--temperature` (default 1.0),
`--max-tokens` (default 1024). Output lands in `results/<timestamp>/` (git-ignored): one `.txt` per
run, `all_runs.json`, and `tally.json`.

## Honest notes

- **Not bit-for-bit reproducible.** LLM outputs are non-deterministic; your tally will differ from
  the published one. The claim is the pattern (tight convergence on the expected call), not a fixed
  number. Raise `--treatment-reps` to see the distribution.
- **This differs from the original runs.** The published `../raw-runs/` came from Claude Code
  subagents that *read* the installed `SKILL.md`. This script *embeds* the skill text into the
  treatment system prompt instead. Equivalent for "treatment = model + skill content"; only the
  delivery differs.
- **The tally is mechanical.** It just counts the `VERDICT:` line. Real scoring ("on the expected
  call") needs a human reading the raw files against `../rubric.md` — template echoes and quoted
  counter-examples can fool an automated count.
- **The rubric is not pre-registered and the model is a single family.** See `../README.md`,
  "Limitations". This script lets you swap `--model` to start cross-model replication.
