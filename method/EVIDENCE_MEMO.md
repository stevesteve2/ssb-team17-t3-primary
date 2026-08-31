# EVIDENCE_MEMO — what the literature says, and what it implies for our three entries
2026-08-30. Sources: EVIDENCE_LIBRARY.csv (E-numbers cited below). Established findings are
labeled [F]; our own inferences [I].

## 1. The main methodological precedent (Tier 1 design)
[F] Hewitt/Ashokkumar/Ghezae/Willer (Nature; E1–E8) is the canonical validation of
participant simulation: GPT-4 prompted with (a) a brief study-setting intro, (b) a
**specific demographic profile** (gender, age, race, education, ideology, partisanship)
drawn from a nationally representative distribution, (c) the verbatim stimulus, (d) the
outcome question with scale labels; responses averaged per condition. Accuracy across 70
US survey experiments: r=0.85 (r_adj=0.91); unpublished-only r=0.90 — not memorization.
[F] Their prompts used *demographics-only* personas (no rich biographies), *per-outcome*
elicitation, and an ensemble over prompt phrasings; accuracy rose with more prompts.
[I] → Tier 1 adopts demographics-conditioned minimal personas, whole-session block
prompting (see §5), no hand-crafted biographies (also avoids encoding expected effects,
which 2509.13397 [E27] warns inflates apparent accuracy through design freedom).

## 2. The regime we are actually in (expectations + Tier 2/3 design)
[F] Within-megastudy prediction is much harder than across-study prediction: the same
Nature pipeline drops to r=0.47 / r_adj=0.61 (79% directional) on survey megastudies
(E5), because same-direction treatments compress true between-condition variance. Their
megastudy set includes Vlasceanu et al.'s climate megastudy — our nearest neighbor.
[F] Experiments "targeting existing attitudes" show reduced accuracy (r_adj≈0.57, E8);
climate attitudes are the canonical entrenched attitude.
[F] Experts do WORSE in this regime (r=0.25/r_adj=0.27, 66% directional; E6); LLM
predictions beat experts within megastudies.
[I] → Realistic goal for pooled Pearson here is ~0.3–0.6, driven mostly by
*between-outcome* structure (which outcomes move at all), less by fine intervention
ranking. Within-outcome Pearson will be the hardest metric. Do not chase implausible
dispersion to game pooled r: calibration slope is scored and β<1 flags exaggeration.

## 3. Magnitude priors for climate one-shot text interventions
[F] Vlasceanu megastudy (E9–E13): best belief effect +2.3pp; best policy +2.6pp; sharing
+12.1pp; **no intervention moved effortful behavior; several backfired**. Consensus
messaging moved action only for liberals.
[F] Rode et al. meta-analysis (E18): pooled climate-attitude intervention effect d≈0.08
(≈1–2pp on a 0–100 slider given SD≈20–25).
[F] pgae485 (E14–E16): a history-of-climate-science paragraph (closely analogous to our
Measurement & modeling / Model accuracy / Peer-review stimuli) raised belief +2.36 and
perceived pro-consensus scientist skill +2.08 (0–100), across parties.
[F] pgaf400 advocacy megastudy (E17): best-in-class interventions reach ~10pp only on
low-cost advocacy actions; moral-foundations framing works for Republicans.
[I] → Priors by outcome family for OUR benchmark (pp on 0–100 unless noted):
  - trust_multidimensional & trust_post: typical +0.5 to +3; best conditions +2–4.
    (Interventions here are purpose-built for trust; pgae485 shows ~+2 is achievable.)
  - distrust_post: mirror-negative, smaller magnitude (−0.5 to −2).
  - belief_post / concern_mean: +0 to +2 (entrenched; most stimuli don't argue the
    science is real, they humanize scientists).
  - policy outcomes (role/general/specific), funding, inst_trust: +0 to +2; distal.
  - behavior_mean: ~0 (null prior; Vlasceanu backfires legitimize small negatives).
  - donation_ams ($0–10): ~0 to +0.2$ (≈0–2pp of range).
  - newsletter_signup: 0 to +2pp probability (low-cost behavior CAN move; E11/E17).

## 4. Calibration policy (frozen rule, external evidence only)
[F] Raw LLM-simulated magnitudes are systematically exaggerated: RMSE 10.9pp; a linear
shrink of **0.56** (estimated on their archive) cut RMSE to 5.3pp, better than human
forecasters (E3–E4).
[I] → FROZEN RULE: Tier-3-style ATE outputs (and Tier-2 implied treatment−control
differences) are shrunk toward 0 by ×0.56 before submission, applied uniformly (no
per-cell tuning). Tier 1 is NOT post-hoc shrunk at the respondent level (that would
corrupt distributions/composites and the scored calibration slope β_adj already
accounts for reliability); instead Tier 1's conservatism comes from prompting ordinary,
inattentive-ish respondents and matched-profile assignment across conditions. This uses
a published coefficient — not an invented one — exactly as the operator required.
Fallback if validation probe contradicts it: no shrinkage (identity), never a fitted
coefficient from our own target predictions.

## 5. Under-dispersion, stereotyping, moderators
[F] LLM respondents understate human variance and can produce unstable marginals
(Bisbee et al., E25); statistical realism ≠ causal accuracy (E26).
[F] Subgroup CATE *levels* are predicted about as well as overall effects (r_adj
.85–.90), but treatment×demographic *interactions* are poorly predicted (r_adj .17–.55,
raw r≈0; E7); real US treatment effects are largely homogeneous (6–15% of archive
effects significantly moderated).
[I] → Tier 2 moderator file: predict moderator-level *baseline* differences (which are
real and well documented — e.g., party gaps in trust) but keep *treatment-effect*
deviations near zero except the handful with direct evidence (consensus × ideology,
E13; moral-foundations × party, E17; state-relevance for Extreme weather). This is the
"no-moderation is honest" guidance in the FAQ plus a small evidence-based overlay.
[I] → Tier 1 dispersion: prompt for integer slider answers with realistic spread
(explicitly permit extreme and neutral responses), one respondent per call-session;
no post-hoc noise injection (unvalidated).

## 6. Baselines (Tier 2 control cells; anchors for everything)
[F] CCAM Fall/Spring 2025 (E19–E23): 72% GW happening; 58% mostly human-caused; 65%
somewhat+ worried; 77% fund renewables; 74% regulate CO2. PLOS Climate review (E24):
trust in climate scientists shows a large partisan gradient (Dem ≈ 2× Rep confidence).
[I] → Slider-mean anchors (0–100): belief_post ~65–70; concern_mean ~55–62;
policy_general ~62–68; policy_specific_mean ~62–68 (popular items 70–80, food/fuel
taxes 45–55); trust_post ~62–68 (Dem ~78, Rep ~48, Ind ~60); trust_multidimensional
~63–70 (benevolence/openness lower than competence); distrust ~30–36; funding_perceptions
~60–66; inst_trust_mean ~55–62 (NASA/NOAA high, fed gov ~40); policy_role_mean ~62–68;
behavior_mean ~40–50; donation ~$3–4.5; newsletter signup ~5–15%. Final numbers are set
by the Tier-2 baseline forecasting step with these anchors in-prompt (frozen), not ad hoc.

## 7. Model adequacy
[F] Claude-family frontier models matched GPT-4 on the one head-to-head selection task
in the Nature paper (E28); accuracy rose monotonically with model capability (GPT-3→4).
[I] → claude-fable-5 (frontier, 2026) is a reasonable FORECAST_MODEL; no cross-model
ensemble (no external validation available for one, and timeline forbids building it).

## 8. What we will NOT do (evidence-driven exclusions)
- No rich narrative personas (E27 researcher-df risk; E25 instability).
- No mechanism-score ontologies for Tier 3 (unvalidated latent coefficients).
- No per-cell calibration tuning; single frozen global rule (E4).
- No attempts to widen dispersion of ATE predictions to chase pooled r (β is scored).
- No conversion of attitude shifts into behavior shifts (E12: behavior stays ~null).
