#!/usr/bin/env python3
"""Tier-3 validation probe: forecast Vlasceanu et al. 2024 megastudy ATEs blind.
Target protocol: per-condition call, k=2 forecasters, median aggregation.
Logs every call (prompt, raw output, cost) to logs/probe_t3/."""
import json, subprocess, pathlib, time, statistics, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGDIR = ROOT / "logs" / "probe_t3"
LOGDIR.mkdir(parents=True, exist_ok=True)

INTERVENTIONS = {
  "Scientific consensus": "A message stating that 97% (an overwhelming majority) of climate scientists have concluded that human-caused climate change is happening, emphasizing the strength of scientific agreement.",
  "Psychological distance": "A message showing that climate change impacts are not distant: they are already affecting people close to the reader in space and time (their own region, their own lifetime), with concrete local examples.",
  "Letter to future generation": "Participants write a short letter to a child they care about, describing what they are doing today so the child can look back on their climate efforts.",
  "Future self continuity": "Participants read/write a letter from their future self describing how today's climate actions affected their later life.",
  "Negative emotions (doom)": "A factual but alarming message about severe climate impacts designed to induce negative emotions (fear, worry) about inaction.",
  "Pluralistic ignorance correction": "A message correcting the common underestimate of how many fellow citizens are concerned about climate change and support action (most people are concerned).",
  "Binding moral foundations": "A message framing climate protection through purity/sanctity, loyalty, and authority moral values (protecting the natural order, one's community and country).",
  "System justification": "A patriotic framing: protecting the climate preserves the American way of life and national strength (system-affirming, not system-critical).",
  "Collective action efficacy": "A message with evidence that collective climate action works and that joining others produces real results.",
  "Dynamic social norms": "A message about changing norms: more and more Americans are adopting climate-friendly behaviors over recent years (trend information).",
  "Letter from an older adult": "A message/letter in which an older adult expresses regret and responsibility toward younger generations about climate inaction (intergenerational appeal)."
}

OUTCOME_TABLE = """belief | 0-100 slider, 'climate change is happening / human-caused' belief index | US baseline ~70
policy_support | 0-100 slider index over 9 climate policies | US baseline ~65
share_information | willingness/act of sharing climate info on social media, % of participants | baseline ~35%
tree_planting_behavior | effortful behavior task (work for tree planting), % participating | baseline ~50%"""

EVIDENCE_TABLE = """- Typical one-shot climate text interventions: pooled d~0.08 (~1-2 points on 0-100) (Rode et al. 2021 meta-analysis).
- History-of-climate-science paragraph raised belief +2.36 (0-100) in a US RCT (PNAS Nexus 2024).
- Best-in-class low-cost advocacy interventions reach up to ~10pp on low-cost actions (US megastudy 2026).
- Effortful climate behavior is very hard to move with text; null and negative effects occur."""

PROMPT_TMPL = """You are an expert forecaster of survey-experiment results, calibrated like a superforecaster: you produce posterior-mean estimates, not optimistic possibilities.

A preregistered megastudy (global online sample including a large U.S. arm; ~250-500 per condition per country cluster) tests short climate interventions. Each participant gets ONE intervention, then outcomes are measured. Control participants get no intervention. You are forecasting the AVERAGE TREATMENT EFFECT (intervention minus control) for ONE intervention on 4 outcomes.

THE INTERVENTION (summary):
{desc}

THE 4 OUTCOMES (name | scale | baseline):
{outcomes}

RELEVANT EXTERNAL EVIDENCE:
{evidence}

Forecasting guidance (follow strictly):
- One-shot text interventions typically move entrenched climate attitudes by ~0-3 points on 0-100 scales.
- Low-cost actions (sharing) can move more than attitudes; effortful behavior typically does not move at all and can go slightly negative.
- Null and small negative effects are plausible and must be forecast when evidence points there.
- Do NOT assume the intervention works because it is well-written.

For EACH of the 4 outcomes output one JSON object with: "outcome", "ate" (original units: points for 0-100; percentage points for the % outcomes), "low", "high" (plausible 90% interval), "reference" (<=10 words), "adjustment" (<=10 words), "confidence" (low/medium/high), "null_plausible" (true/false).
Output ONLY a JSON array of 4 objects, no other text."""

def call_model(prompt, tag):
    t0 = time.time()
    r = subprocess.run(
        ["claude", "-p", "--model", "claude-fable-5", "--output-format", "json",
         "--disallowed-tools", "*", "--no-session-persistence"],
        input=prompt, capture_output=True, text=True, timeout=300)
    dur = time.time() - t0
    out = json.loads(r.stdout)
    (LOGDIR / f"{tag}.json").write_text(json.dumps(
        {"tag": tag, "prompt": prompt, "raw": out, "wall_s": dur}, indent=1))
    txt = out["result"].strip()
    if txt.startswith("```"):
        txt = txt.strip("`").lstrip("json").strip()
    return json.loads(txt), out.get("total_cost_usd", 0.0), dur

def main():
    results, total_cost = {}, 0.0
    for name, desc in INTERVENTIONS.items():
        per_forecaster = []
        for k in range(2):
            tag = f"{name.replace(' ', '_').replace('/', '-')}_f{k}"
            try:
                arr, cost, dur = call_model(PROMPT_TMPL.format(
                    desc=desc, outcomes=OUTCOME_TABLE, evidence=EVIDENCE_TABLE), tag)
                total_cost += cost
                per_forecaster.append({o["outcome"]: float(o["ate"]) for o in arr})
                print(f"{tag}: ok cost=${cost:.3f} {dur:.0f}s", flush=True)
            except Exception as e:
                print(f"{tag}: FAIL {e}", flush=True)
        if per_forecaster:
            outs = set().union(*[set(d) for d in per_forecaster])
            results[name] = {o: statistics.median([d[o] for d in per_forecaster if o in d])
                             for o in outs}
    (ROOT / "validation" / "probe_t3_results.json").write_text(json.dumps(
        {"results": results, "total_cost_usd": total_cost}, indent=1))
    print(f"TOTAL COST ${total_cost:.2f}")

if __name__ == "__main__":
    main()
