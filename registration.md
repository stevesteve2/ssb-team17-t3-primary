# Silicon Sample Benchmark — method registration form (completed, T3_primary)

## 0 · Approach identity and output
- **0.1 Team ★** — team_17 — Steve Rathje (Carnegie Mellon University, srathje@andrew.cmu.edu, ORCID 0000-0001-6727-571X) and Dan-Mircea Mirea (University of Pennsylvania, danmirea@sas.upenn.edu, ORCID 0000-0002-4349-7059). This entry's pipeline was built and run by S. Rathje via an automated Claude Code agent; the team's secondary-3/-4/-5 entries use a separate Codex/OpenAI pipeline by D.-M. Mirea, developed in parallel from a shared project brief (the pipelines were not fully independent of each other).
- **0.2 Plain-language summary ★** — We ask a frontier LLM, three independent times per intervention, to forecast each intervention's average treatment effect on all 13 outcomes directly, conditioned on the verbatim stimulus, published baselines, and a curated table of the most comparable human experimental results, with explicit conservative-forecasting instructions; per-cell medians are submitted.
- **0.3 Submission tier & approach family ★** — Tier 3; direct evidence-conditioned effect forecast; single model (claude-fable-5), k=3 ensemble; literature-conditioned.
- **0.4 Pipeline diagram** — benchmark materials + published-evidence library -> frozen prompt template (tier3_forecast_prompt_v1.txt) -> k=3 forecasts/intervention -> per-cell median (identity calibration per frozen rule) -> deterministic post-processing -> prediction file(s). Full code: method/pipelines/.
- **0.5 Coverage ★** — 208 ATEs (16 interventions x 13 outcomes) vs the shared control. Full coverage confirmed: all 16 interventions and all 13 outcomes (+ control where required).

## A · Scope of LLM use
- **A.1 Purpose** — LLM produces effect-level forecasts; deterministic aggregation; agent session orchestrated code and docs.
- **A.2 Degree of automation ★** — Fully automated at prediction time: scripted pipeline (method/pipelines/), no human selection, editing, or review of any predicted value. Human input limited to pre-registered design and budget decisions before generation.

## B · Model / system details
- **B.1 Model name(s)** — claude-fable-5 (Anthropic hosted, 2026; provider does not publish size). Orchestration agent: same model / Claude Code v2.1.214.
- **B.2 Access & context mode** — Claude Code CLI v2.1.214 headless mode (`claude -p --output-format json --disallowed-tools "*" --no-session-persistence`), stateless single-turn calls, tools disabled; calls on 2026-08-30/31 (timestamps in raw logs).
- **B.3 Configuration** — Provider-default sampling; temperature/top-p/seeds NOT exposed by this interface (disclosed limitation). Max tokens: interface default. Completions per item: see F.
- **B.4 Customization** — None: no fine-tuning, no retrieval index, no web access at prediction time, no agentic scaffold (tools disabled).
- **B.5 Persistent memory** — None; every call stateless (`--no-session-persistence`).
- **B.6 Inference stack** — N/A (hosted models).
- **B.7 Ensembles** — k=3 same-model independent calls per intervention; per-outcome median of ATEs.

## C · Prompts
- **C.1 Exact prompts** — Verbatim frozen templates in method/pipelines/ (tier3_forecast_prompt_v1.txt); per-call filled prompts archived verbatim in the raw logs (K.2). Pre-specified before target prediction (hashed in method/DESIGN_LOCK.sha256); not refined in response to target outputs.
- **C.2 System-wide instructions** — None beyond the template (no system prompt injected; CLI defaults).
- **C.3 Prompt-design rationale** — Follows Hewitt et al. (Nature 2024) demographics-conditioned simulation evidence and conservative-forecasting literature; ordinary-respondent framing to counter over-attentiveness; explicit permission for null/negative effects to counter optimism bias; details in method/EVIDENCE_MEMO.md.

## D · Persona / profile construction (Tiers 1–2)
- **D.1 Profile source** — N/A (direct effect forecasts, no personas or subgroup cells).
- **D.2 Profile verbalization** — N/A.
- **D.3 Assignment & weighting** — N/A.

## E · Stimulus and survey administration
- **E.1 Stimulus presentation** — Same as Tier 2 (verbatim texts; extreme-weather summarized + one verbatim case).
- **E.2 Survey walk-through** — N/A (ATE forecasting; outcome wordings, scales, and forecast control baselines provided).
- **E.3 Response elicitation** — Structured JSON array of 13 ATE objects (estimate, interval, reference, adjustment, confidence, null-plausibility).

## F · Stochasticity and aggregation
- **F.1 Runs & seeds** — k=3 independent calls per intervention; no seed control (B.3).
- **F.2 Aggregation rule** — Per-outcome median of the 3 forecast ATEs; identity calibration (G.3).

## G · Validation & post-processing
- **G.1 Human validation** — None.
- **G.2 Post-processing** — Median aggregation; JSON schema validation with frozen retry rule; no manual edits.
- **G.3 Calibration corrections** — IDENTITY per frozen rule R1 (see Tier-2 wording; same rule, same probe).

## H · Learning and conditioning components
- **H.1 Fine-tuning data** — N/A (no fine-tuning).
- **H.2 Context & retrieval corpora** — In-context evidence limited to the frozen baseline/evidence tables inside the prompt templates (derived from method/EVIDENCE_LIBRARY.csv; all published sources).

## I · Data inputs, blinding, and competing interests
- **I.1 Competing interests ★** — No funding for this project; model access via the member's paid Claude subscription (Anthropic). No other relationships with LLM-interested entities.
- **I.2 External human data †** — Published aggregate estimates only (no microdata): Hewitt et al. 2024 Nature archive results; Vlasceanu et al. 2024 Sci Adv; Rode et al. 2021 meta-analysis; PNAS Nexus pgae485 (2024) & pgaf400 (2026); CCAM 2025 (Yale/GMU); PLOS Climate trust review; full list with roles in method/EVIDENCE_LIBRARY.csv.
- **I.3 Blinding attestation ★** — I attest that no team member accessed, solicited, or was shown any human outcome data from this study, including pilots or preliminary results presented at talks, before the prediction lock. The pipeline used only the public benchmark materials and previously published external studies (see I.2). — team_17, 2026-08-31
- **I.4 Contamination note †** — claude-fable-5 and claude-haiku-4-5 (Anthropic, 2026; exact training cutoffs not disclosed by provider) postdate this benchmark's public call (July 2026); the survey instrument and intervention texts are public in the template repo and may be in training data, but the human outcomes are sealed and cannot be. The external validation study (Vlasceanu et al. 2024) is published and presumably in training data — disclosed as a limitation of the validation probe (method/validation/VALIDATION_SPEC.md).

## J · Internal selection procedure
- **J.1 Design-space search †** — One frozen configuration per tier; no hyperparameter sweep. Design chosen from external literature (method/EVIDENCE_MEMO.md), then a single pre-registered validation probe per pipeline (method/validation/VALIDATION_SPEC.md): Tier-3 protocol run blind on the Vlasceanu 2024 megastudy (11x4 ATEs; checked sign/null pattern, best-arm top-3, magnitude bias -> selected identity calibration per frozen rule R1); Tier-1 protocol checked on 12-30-respondent probes for schema validity, dispersion, and party gradient. Design frozen in hashed DESIGN_LOCK.md (+4 pre-prediction amendments, all documented with rationale and timestamps) before target forecasts. Budget-driven amendments changed Tier-1 model (sonnet->haiku) and primary designation (T1->T3), both decided before any target prediction existed.

## K · Reproducibility & frozen artifacts
- **K.1 Code & materials** — All code, prompts, evidence files, and design lock in this deposit (method/); no secrets; stochastic (no seed control — see B.3), profile construction seeded and deterministic.
- **K.2 Raw output logs †** — Complete raw model responses (prompt + full JSON incl. cost + timestamp per call): method/raw_model_logs.tar.gz (public, in-deposit).
- **K.3 Computational resources** — 48 calls (claude-fable-5, k=3 x 16 conditions); ≈$2; ~20 min (shared run with Tier 2).

## L · Disclosure class
Class **A · Open** — every item above public; nothing escrowed or withheld.
