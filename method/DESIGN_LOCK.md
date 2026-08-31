# DESIGN_LOCK — frozen before any target prediction
Timestamp: 2026-08-30T17:30:00-04:00 (America/New_York)
Scope: everything below is fixed. After this lock: no method changes based on target
forecasts, no manual edits of target numbers, no selection among generations by their
predictions, reruns only under the frozen retry rules. (Execution of target runs is
additionally gated on operator approval per the milestone stop.)

## Model & invocation (RUN_CONFIG.md)
- FORECAST_MODEL: claude-fable-5, all tiers. Interface: `claude -p --model claude-fable-5
  --output-format json --disallowed-tools "*" --no-session-persistence`, stdin prompt.
- Sampling: provider defaults (temperature/top-p/seed not exposed — disclosed).
- Retry rule: ≤2 retries on parse failure/empty output; then one from-scratch
  regeneration; residual failures logged, never silently dropped. Backoff on API errors.
- Logging: every call's prompt, raw JSON (incl. total_cost_usd), and timestamp到 logs/.

## Frozen pipeline designs
- TIER 3 (per validation R1/R2 outcomes): per-condition batched call (1 intervention ×
  13 outcomes), k=3 independent forecasters, aggregation = per-cell MEDIAN.
  Calibration: IDENTITY (no 0.56 shrinkage) — probe measured magnitude-bias ≈0.67
  (under-, not over-shooting), so rule R1 selects no shrinkage; never inflate.
  NO rank-reconciliation pass (R2: no demonstrated improvement). Prompt:
  pipelines/tier3_forecast_prompt_v1.txt with OUTCOME_TABLE baselines from Tier-2
  control forecast and EVIDENCE_TABLE from EVIDENCE_MEMO §3 (frozen text).
- TIER 2: per-condition call (13 main + 27×13 moderator means), k=3, median; control
  condition forecast first and its medians fed to treatment calls as anchors.
  Post-processing (deterministic): population-weight recentering of moderator levels
  to the main mean; range clipping; moderator deviations ×0.5 toward condition mean;
  treatment−control differences calibrated per R1 (= identity). Prompt:
  pipelines/tier2_cells_prompt_v1.txt.
- TIER 1 (if approved): whole-session single-call respondents, demographics-only
  personas + home state, matched profile pool replicated across all 17 conditions
  (9,000 minimum: 500×16 + 1,000 control, subject to operator budget decision),
  control fillers randomized 1/3 each, Extreme-weather arm state-adaptive per
  BENCHMARK_SPEC, fixed block order (disclosed), compressed CSV output, integer
  enforcement, composites computed in cleaning (exact codebook formulas), no post-hoc
  dispersion manipulation, no respondent-level shrinkage. Prompt:
  pipelines/tier1_respondent_prompt_v1.txt. Profile sampling: census cross-quotas
  (gender×age, gender×race) + CPS/ANES-consistent education/income/party conditional
  draws + population-proportional state.
- Tier-2/Tier-3 ensembling with Tier-1-implied ATEs: NOT used (no externally validated
  weights; timeline forbids building them). Each entry stands alone.

## Frozen selection & designation
- Primary entry: Tier 1 if executed; else Tier 3 (probe showed target-protocol Tier-3
  best-arm identification 3/3 top-3). Secondary entries: the others. Exactly one
  primary across tiers, per benchmark rules.
- Internal headline metric: pooled Pearson r; guardrails RMSE, within-outcome r,
  Spearman, directional agreement, calibration slope.

## Validation outcomes binding this lock (validation/ probe artifacts)
- Probe T3 (Vlasceanu, 22 calls, $1.20): sign/null pattern reproduced; best-arm top-3
  hits 3/3; magnitude bias 0.58–0.76 (mean ≈0.67) → R1 ⇒ identity calibration; R2 ⇒
  no rank pass; R3 stability adequate ⇒ k=3 affordable and fixed.
- Probe T1 (12 sessions, $1.34): 12/12 parse, 0 violations, SD(trust_post)=17,
  party gradient realistic, baselines within ±15pp of anchors (donation low side,
  newsletter 0/12 noted); $0.112/respondent, 11.6s/respondent measured.

## Leakage / blinding attestations
No access to target human outcomes or pilots; no other teams' predictions; no new
human data; published datasets only, documented in EVIDENCE_LIBRARY.csv. Validation
study (Vlasceanu 2024) is disjoint at study level from the calibration evidence
(Nature archive); its presence in model training data is disclosed as a limitation.

## Hashes (SHA-256 at lock time; recomputed in MANIFEST at packaging)
See DESIGN_LOCK.sha256 alongside this file: hashes of this file, the three prompt
templates, EVIDENCE_MEMO.md, EVIDENCE_LIBRARY.csv, TARGET_EVIDENCE_MAP.csv,
VALIDATION_SPEC.md, probe results JSONs, and RUN_CONFIG.md.

## AMENDMENT v1.1 — 2026-08-30 evening (operator-directed, PRE-target-prediction)
Operator supplied team_id=team_17 and directed Tier-1 cost < $50. Fable-5 output
pricing makes 9,000 respondents ≥ ~$90 irrespective of batching; sub-floor N would
draw validator warnings and reference-noise mismatch. AMENDED Tier-1 design:
- TIER-1 FORECAST_MODEL: claude-sonnet-5 (Tiers 2-3 unchanged on claude-fable-5).
  Disclosed in metadata.json models[] and registration.md as a budget-driven,
  operator-approved substitution.
- Generation: batched 10 respondents per call (same session prompt; 10 distinct
  profiles listed; output = 10 independent CSV rows). Gated on a ≤$2 probe testing
  dispersion vs the per-respondent Fable probe (SD trust_post in [10,35]; within-call
  row diversity: no two identical rows; party gradient present; baselines within
  anchors). If probe fails → Tier 1 not executed (reverts to milestone option a).
- N = 9,000 exactly (500×16 + 1,000 control); matched 500-profile pool replicated
  across interventions; 1,000 control = pool ×2 with re-randomized fillers.
All other locked decisions unchanged. Amendment made before any target forecast.

## AMENDMENT v1.2 — 2026-08-31 (operator budget directive "<$50 Tier 1", cost telemetry)
Measured cost $0.010/respondent (not the probe-projected $0.004) made 9,000 rows exceed
the operator's $50 Tier-1 budget. PRE-completion amendment (no target ATE has been
computed from Tier-1 data; generation is condition-by-condition raw rows only):
- Tier-1 target N: 250/intervention + 500 control (4,500). Surplus rows already
  generated above 250 in early conditions are KEPT (paid, valid, no selection applied).
  Below the benchmark floor of 9,000 → `make check` WARNING, disclosed in
  registration.md D/G with this rationale.
- Batch size 20 respondents/call (was 10), gated on a 1-call probe: >=18/20 rows parse,
  all unique, party gradient present. Fail -> stay at 10/call, same N target.
- Runner cap for the resume run: $22 (total T1 <= ~$45).
All other v1.1 decisions unchanged.

## AMENDMENT v1.3 — 2026-08-31 (operator: "just do all rows at cheapest model under 50")
Supersedes v1.2's reduced-N plan. Tier-1 final design:
- FULL N=9,000 (500x16 + 1,000 control), single model claude-haiku-4-5 (cheapest
  available tier), batch 20 respondents/call, cap $45 for the run.
- The 1,720 claude-sonnet-5 rows are EXCLUDED from the submission file (model-condition
  confound: only 4 conditions had Sonnet rows) and retained in raw logs for
  transparency. Exclusion is by generation-model, decided before any ATE computation —
  not by looking at predicted values.
- Gate: 1-call probe (>=18/20 parse, unique rows, Dem-Rep trust gradient >=10). If the
  Haiku probe fails the gate -> fall back to v1.2 (Sonnet, 250/int + 500 ctrl).
- metadata models[] for T1 = ["claude-haiku-4-5"]; registration.md discloses the model
  change, its budget rationale, and the capability-gradient risk (Nature E1: accuracy
  rises with model capability — Haiku is a weaker simulator; disclosed tradeoff).

## AMENDMENT v1.4 — 2026-08-31 (primary designation, PRE any Tier-1 aggregate result)
v1.1 set "primary = Tier 1 if executed" when Tier 1 was planned on a frontier model.
v1.3 moved Tier-1 generation to claude-haiku-4-5 (budget directive). External evidence
(Nature E1/Fig2B: simulation accuracy rises monotonically with model capability) implies
a Haiku-simulated Tier 1 is expectedly weaker than the Fable-5 Tier 3 forecaster.
AMENDED: primary = Tier 3 (Fable). Tier 1 = secondary-1, Tier 2 = secondary-2.
Decided before computing any Tier-1 condition mean or ATE; based only on external
capability evidence, not on any target prediction.
