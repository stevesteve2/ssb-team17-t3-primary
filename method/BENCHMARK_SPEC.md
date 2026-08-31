# BENCHMARK_SPEC — Silicon Sample Benchmark (reconstructed 2026-08-30)

Authoritative sources: benchmark preregistration
(janpfander.github.io/llm_predictions_megastudy/preregistration_benchmark.html), call for
participation (site root), and the cloned submission repo (README.md, FAQ.md, codebook.csv,
survey/questionnaire.txt, survey/survey.json, survey/condition_codenames.csv,
scripts/lib/submission_spec.R, example prediction files). Where this document and those
sources ever disagree, the official materials win.

## Study
Behavioral megastudy on **trust in climate scientists**. U.S. adult opt-in panel, quota-matched
(census cross-quotas gender × age and gender × race). Human N ≈ 18,000: **1,000 per
intervention × 16 text interventions + 2,000 shared control**. Human data are already
collected and sealed; prediction lock **2026-08-31**; deposit window **2026-08-28 → 31**;
scoring + manuscript ~2026-09-30.

## Conditions (17 = control + 16 interventions; canonical labels from submission_spec.R)
control | Corporate reliance | Social justice | Interview Prof. Maraun | Funding |
Oil industry misinformation | Measurement & modeling (1) | Former skeptics |
High public trust | Measurement & modeling (2) | Peer-review | Scientist community helpers |
Consensus | Portrait Prof. Cherry | Model accuracy | Interview Prof. Sebille |
Extreme weather predictions

- Raw survey keys conditions by animal-pair code names (survey/condition_codenames.csv);
  4 code names are semicolon-joined multi-pair strings — join on the FULL string.
- **Control** = one of three neutral filler texts randomly assigned per respondent
  (neckties / baseball / dances); all map to the single label `control`.
- **Extreme weather predictions is STATE-ADAPTIVE**: respondent reports home state →
  mapped to Case 1 (flood risk: 26 states + DC), Case 2 (wildfire: 13 states),
  Case 3 (winter storms: 11 states), Case 4 (generic fallback, only for "Prefer not to
  say"). Respondent sees: state question → one intro paragraph ([STATE]/[CASE] filled, or
  generic IF branch for Case 4) → exactly ONE case text. Never present the whole block.
- The interactive chatbot arms and "Value similarity" quiz are NOT part of this
  simulation instrument (removed from survey.json/qsf; not among the 16).

## The 13 scored outcomes (exact submission labels; codebook.csv is canonical)
| outcome | scale | notes |
|---|---|---|
| trust_multidimensional | 0–100 | PRIMARY. Mean of 4 subscales (competence, integrity, benevolence, openness), each the mean of 3 items (12 items total, sliders 0–100). Scoring reads composites AS SUBMITTED (never recomputed) — must equal the item-implied value. |
| trust_post | 0–100 | single-item trust |
| distrust_post | 0–100 | single-item distrust (separate item, not reverse of trust) |
| funding_perceptions | 0–100 | = 100 − funding_5 (reverse-coded in cleaning); higher = supports more funding |
| policy_role_mean | 0–100 | mean of 4 items |
| inst_trust_mean | 0–100 | mean of 5 items (EPA, NASA, NOAA, universities, federal gov) |
| belief_post | 0–100 | "human activities are causing climate change" accuracy |
| concern_mean | 0–100 | mean of 3 items |
| policy_general | 0–100 | single item |
| policy_specific_mean | 0–100 | mean of 7 items |
| behavior_mean | 0–100 | mean of 6 behavioral-intention items |
| donation_ams | 0–10 | whole dollars of a $10 bonus to AMS; integers 0–10 |
| newsletter_signup | 0/1 | Tier 1: binary per respondent; Tier 2 cell mean: 0–1 proportion. Depends on the newsletter OFFER PAGE shown immediately before (verbatim in questionnaire.txt) — must be presented for the item to be answerable. |
All 0–100 slider responses are INTEGERS at Tier 1; composites are unrounded means.
The 12 trust items are shipped in Tier 1 but are sub-components, not among the 13.

## Survey flow (chronological; questionnaire.txt)
consent + 2 screening filters → demographics (gender, year_birth, race, education,
[education_climate], income, household, social_class, rural, zip, attention1, party
[+partisan_importance], religion[+bornagain, religiosity], epistemic-autonomy ×6,
attention2) → transition → PRE-treatment: belief_pre, trust_pre, alienation ×6+matrix →
transition → CONDITION (one stimulus) → transition → POST outcomes: trust battery
(12 items, always FIRST) then secondary/tertiary outcome BLOCKS in RANDOMIZED order
(funding, institutional trust, policy-role, trust_post, distrust, donation, newsletter
offer page + item, belief_post, concern, behaviors, policy_general, policy_specific) →
comments. Unscored items (attention checks, religion, alienation, pre-measures, etc.)
exist for flow fidelity only; simulating them is a design choice.
Age derivation: age = 2026 − year_birth; age_band ∈ {18-29, 30-44, 45-59, 60+}.

## Moderators (6; 27 levels total — exact strings)
gender: Male | Female | Other (3)
age_band: 18-29 | 30-44 | 45-59 | 60+ (4)
race: White / Caucasian | Black / African American | Hispanic / Latino |
      Asian / Asian American | Other (5)
education: Less than high school | High school diploma / GED | Some college or
      Associate's degree | Bachelor's degree | Master's degree / Professional degree |
      Doctorate degree / Ph.D. (6)
income: Less than $30,000 | $30,000 to $55,999 | $56,000 to $99,999 |
      $100,000 to $167,999 | $168,000 or more (5)
party: Republican | Democrat | Independent | Other (4)
Party Qualtrics EXPORT codes: 1=Rep, 2=Dem, 3=Ind, 4=Other (on-screen order differs).

## Human quotas (census-based, N≈18,000)
age: 18-29 20.2% | 30-44 26.0% | 45-59 22.9% | 60+ 30.9%
race: White 60.2% | Hispanic 18.1% | Black 12.3% | Asian 6.7% | Other 2.7%
Cross-quotas on gender × age and gender × race (2024 Census PEP).

## Submission formats (enforced by scripts/check.R via submission_spec.R)
- Tier 1: one row per respondent; columns = profile_id, condition, gender, age_band,
  race, education, income, party, trust_multidimensional, 12 trust items, trust_post,
  distrust_post, funding_perceptions, policy_role_mean, inst_trust_mean, belief_post,
  concern_mean, policy_general, policy_specific_mean, behavior_mean, donation_ams,
  newsletter_signup. Floor: ≥500/intervention, ≥1,000 control (= 9,000 minimum).
  Raw Qualtrics-format export goes in raw_data_deposit/ (part of the deposit);
  `make clean` maps it to the analysis file, or build the analysis file directly.
- Tier 2 main: condition, outcome, mean — 17 × 13 = 221 rows.
- Tier 2 moderator: condition, moderator, moderator_level, outcome, mean —
  17 × 27 × 13 = 5,967 rows. No-moderation = repeat the condition main mean (honest,
  always-valid prediction).
- Tier 3: condition, outcome, ate — 16 × 13 = 208 rows (no control row; ATE vs control).
- Completeness enforced: full grid exactly once, NO NA anywhere, no duplicates; ranges
  checked (0–100; donation 0–10; newsletter cell means 0–1). Tier 3 ATEs unbounded.
- Point predictions only — no uncertainty intervals anywhere.
- File naming: <team_id>_T<tier>_<primary|secondary-k>_v<n>.csv (T2: ..._cells_main /
  ..._cells_moderator). team_id assigned by organizers (emailed 2026-08-15) — never invented.
- One entry = one repo = one Zenodo deposit; ≤3 entries/tier; exactly ONE primary
  across all tiers. Tier-1 entries automatically receive Tier-2/3 analyses — do NOT
  restack the same method at lower tiers.

## Scoring (preregistration)
- Human sample split in half by preregistered seed (42). **Human 1** = scoring
  reference; **Human 2** = human-replication reference scored like a submission.
- ATEs: OLS, HC2 robust SEs, control as reference level, NO covariate adjustment.
  newsletter_signup: logistic regression → marginal effects on probability scale.
- Attrition rule: if heterogeneous differential attrition is detected, human reference
  models use inverse-probability weights (submissions are then compared against the
  weighted human estimates).
- Unit conversion before pooling: percentage points of outcome range —
  0–100 outcomes unchanged; donation ×10; newsletter probability effects ×100.
- ATE metrics: directional agreement (exact-zero predictions = half credit, 0.5);
  Spearman ρ; pooled Pearson r (across all 208 pairs, in pp); within-outcome Pearson
  (mean-centered per outcome); RMSE (pp); noise-corrected r_adj and RMSE_adj (flagged
  0 if below reference precision); calibration regression human~predicted pooled over
  208 pairs → intercept α and slope β (β<1 = predictions too dispersed / exaggerated;
  β_adj Tier 1 only).
- Extra analyses: Tier 1 = distributions (variance ratio, OVL, KS-D, Wasserstein-1),
  subgroup heterogeneity, demographic-baseline calibration, demographic predictability,
  stereotyping/parity-gap diagnostics. Tier 2 = subgroup + demographic baselines.
  Tier 3 = ATE + calibration only.
- No single composite winner is defined; the metric family is ordered "least to most
  strict" (directional → Spearman → Pearson → RMSE) plus calibration. OUR internal
  primary-selection metric (operator decision): pooled Pearson r, with RMSE,
  within-outcome r, Spearman, directional agreement, calibration as guardrails.

## Deposit & disclosure
GitHub release → Zenodo DOI within 2026-08-28→31; email DOI + SHA-256 fingerprints +
primary designation + signed exposure declaration to janlukas.pfaender@gmail.com.
Disclosure classes: A open / B escrowed / C sealed (raw model logs required for Tiers
1–2 — withholding ⇒ Class C; Tier 3 logs where intermediate generations exist).
metadata.json: team_id, creators (real ORCID or empty), tier, entry, models,
approach_family, code_repository, coverage {16,13}, blinding_attestation true,
prediction_files + sha256. `make manifest` fingerprints; `make check` validates;
`make zenodo_citation` builds .zenodo.json (derived — never hand-edit).
Helper scripts require R ≥4.2 + tidyverse, jsonlite, digest (present in this repo).

## Blinding attestation constraints (binding on this project)
No access to human outcomes/pilots of THIS study; no new human data; no manual
prediction edits; no discarding generations for looking "wrong"; no post-hoc tuning
after seeing the full target set; fully automated AI pipeline; previously published
human studies/datasets ARE permitted with documentation.
