# RUN_CONFIG — Silicon Sample Benchmark entries
Created: 2026-08-30 (local, America/New_York)

## Execution agent
- EXECUTION_AGENT: Claude Code CLI v2.1.214 (interactive session driving the build)
- Working directory: /Users/steverathje/Desktop/SiliconSampleBenchmark
- Submission template cloned from https://github.com/janpfander/silicon-sample-submission (2026-08-30)

## Forecast model
- FORECAST_MODEL: claude-fable-5 ("Claude Fable 5", Anthropic)
  - Session default set by the operator via /model on 2026-08-30 ("Set model to Fable 5").
  - The same model is to be used for all three tiers (no cross-model ensemble unless
    externally validated and approved — none is planned given timeline).
- MODEL_INTERFACE (two supported, auditable routes; both bill the operator's Claude
  subscription, not a metered API key — no ANTHROPIC_API_KEY is set in this environment):
  1. PRIMARY: headless CLI — `claude -p --model claude-fable-5 [--output-format json]`,
     invoked from scripted pipelines; every call's prompt and raw response is written to
     logs/ before parsing. Supports scripted batching, retries, and structured output
     requests via prompt contract.
  2. ALTERNATIVE: in-session Agent tool (subagent spawn with model pinned to "fable"),
     used only for exploratory probes, with prompts/outputs also logged to files.
- Exact model identifier: claude-fable-5 (as exposed by Claude Code's model selector).
  Provider: Anthropic. Version timestamp: not exposed by the interface; recorded as the
  identifier string above plus invocation timestamps in per-call logs.
- Sampling settings: the Claude Code CLI does not expose temperature/top-p/seed control
  for either route. UNSUPPORTED SETTINGS: temperature, top_p, seed. Consequence:
  provider-default sampling; run-to-run stochasticity is handled by design (multiple
  independent generations + fixed aggregation rule) rather than by seed pinning.
  This limitation is disclosed in registration.md.
- Structured output: no native JSON schema enforcement; the pipeline requests JSON in
  the prompt and validates/parses with a frozen retry rule (see DESIGN_LOCK).
- Retry/timeout: frozen rule = up to 2 retries per call on parse failure or empty
  output, then the call is logged as failed and the respondent/forecast is regenerated
  once from scratch; remaining failures are logged and counted (never silently dropped).
  Rate limiting: sequential or low-parallelism execution; exponential backoff on errors.

## Credentials
- No credentials or secrets are recorded anywhere in this repository. Calls run under
  the operator's existing local Claude Code login.

## Cost policy (operator-set)
- Ask before exceeding: $2 exploratory/validation step; $25 any tier; $50 total.
- NOTE: subscription-plan usage is not metered in dollars by the interface. Cost
  estimates below are therefore reported two ways: (a) token-volume estimates, and
  (b) dollar-equivalents at public API list prices for the closest Anthropic tier,
  as a conservative upper bound. Plan-usage exhaustion is an additional practical
  constraint flagged in the milestone risk list.

## Call/token/runtime/cost estimates (planning numbers; finalized in milestone doc)
- Tier 1 (per README budgeting note): whole-session respondent ≈ 5–15k input + 1–3k
  output tokens. 9,000 respondents ≈ 50–130M input tokens. THIS IS THE DOMINANT COST
  and is at/over practical limits for a 1-day subscription-based run; the milestone
  recommends the minimum floor (9,000) and a block-batched session design.
- Tier 2: ~17 batched calls (1 condition × 13 outcomes + 27 moderator levels per call)
  × k independent forecasters (k=3–5) ≈ 51–85 calls, ~2–6k tokens each ≈ <1M tokens.
- Tier 3: 208 pairs × k independent forecasts (k=3–5), batched per condition (16 × 13
  outcomes per call) ≈ 48–80 calls ≈ <1M tokens; plus one comparative ranking pass per
  outcome (13 × m orders, m=3) ≈ 39 calls.
- External validation runs add roughly one Tier-2/Tier-3-sized pass per validation study.

## Deadline context (dominant constraint)
- Prediction lock / deposit window: 2026-08-28 → 2026-08-31 (hard). Today is 2026-08-30.
- team_id: assigned by organizers by email 2026-08-15 — NOT invented here; must be
  supplied by the operator before packaging. Same for creators/ORCID/contact fields.
