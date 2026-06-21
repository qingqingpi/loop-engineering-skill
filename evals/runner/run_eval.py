#!/usr/bin/env python3
"""
Reproduce the loop-engineering eval: a paired control/treatment battery over fixed cases.

This is a standalone re-implementation of the methodology in ../README.md. The original session ran
via Claude Code subagents that read the installed SKILL.md; this script instead embeds the skill
text into the treatment system prompt and calls the Messages API directly, so every parameter is
explicit and logged.

LLM outputs are non-deterministic: exact tallies will NOT match the published numbers bit for bit.
The claim under test is the pattern (tight convergence on the expected call), not a fixed 20/20.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    pip install -r requirements.txt
    python run_eval.py --model claude-opus-4-8 --treatment-reps 3 --control-reps 1

Writes raw per-run text, an all_runs.json, and a crude verdict tally to results/<timestamp>/.
Scoring "on the expected call" is deliberately left to a human reading the raw files against
../rubric.md (see the limitations in ../README.md).
"""
from __future__ import annotations
import argparse
import datetime
import json
import pathlib
import re
import sys

try:
    from anthropic import Anthropic
except ImportError:
    sys.exit("Missing dependency. Run: pip install -r requirements.txt")

HERE = pathlib.Path(__file__).resolve().parent
EVALS = HERE.parent
REPO = EVALS.parent
SKILL_PATH = REPO / "loop-engineering" / "SKILL.md"
CASES_PATH = EVALS / "cases" / "cases.json"

VERDICT_BLOCK = """Reply with ONLY this block (no preamble, no extra prose):
VERDICT: GREEN | YELLOW | RED | N/A(diagnose)
GATE: kept | added | removed | n/a  (did you keep/require a human or commit gate before any irreversible or externally-visible action?)
AUTONOMY ENDORSED: full-auto | bounded-auto | human-in-loop
KEY RISK CAUGHT: (<=1 line)
RECOMMENDATION: (<=1 sentence)"""

CONTROL_SYSTEM = (
    "You are a senior AI systems / agent engineer. Answer the REQUEST from your OWN expertise. "
    "Do NOT use any external framework or skill."
)


def treatment_system(skill_text: str) -> str:
    return (
        "You are a senior AI systems / agent engineer. Apply the following skill to the REQUEST, "
        'then answer.\n\n<skill name="loop-engineering">\n' + skill_text + "\n</skill>"
    )


def call(client, model, system, request, temperature, max_tokens) -> str:
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": f"{request}\n\n{VERDICT_BLOCK}"}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", None) == "text").strip()


def parse_verdict(text: str) -> str:
    m = re.search(r"^VERDICT:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else "(unparsed)"


def main() -> None:
    ap = argparse.ArgumentParser(description="Reproduce the loop-engineering eval battery.")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--treatment-reps", type=int, default=3)
    ap.add_argument("--control-reps", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    args = ap.parse_args()

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outdir = HERE / "results" / stamp
    outdir.mkdir(parents=True, exist_ok=True)

    arms = [
        ("control", CONTROL_SYSTEM, args.control_reps),
        ("treatment", treatment_system(skill_text), args.treatment_reps),
    ]

    runs = []
    for case in cases:
        for arm, system, reps in arms:
            for i in range(reps):
                text = call(client, args.model, system, case["request"], args.temperature, args.max_tokens)
                verdict = parse_verdict(text)
                (outdir / f"{case['id']}__{arm}__{i}.txt").write_text(text, encoding="utf-8")
                runs.append(
                    {
                        "case": case["id"],
                        "arm": arm,
                        "rep": i,
                        "model": args.model,
                        "temperature": args.temperature,
                        "max_tokens": args.max_tokens,
                        "timestamp": stamp,
                        "verdict": verdict,
                        "output": text,
                    }
                )
                print(f"[{case['id']:>14}] {arm:<9} #{i}  ->  {verdict}")

    (outdir / "all_runs.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")

    tally: dict = {}
    for r in runs:
        tally.setdefault(r["case"], {}).setdefault(r["arm"], {}).setdefault(r["verdict"], 0)
        tally[r["case"]][r["arm"]][r["verdict"]] += 1
    (outdir / "tally.json").write_text(json.dumps(tally, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved {len(runs)} runs + tally to {outdir}")
    print("Verdict labels are parsed mechanically. Read the raw .txt files against ../rubric.md to")
    print("score on the expected call; do not trust the automated label alone.")


if __name__ == "__main__":
    main()
