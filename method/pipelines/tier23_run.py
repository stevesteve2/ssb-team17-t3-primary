#!/usr/bin/env python3
"""TIER-2 + TIER-3 TARGET RUN (locked design). claude-fable-5, k=3, median aggregation.
Order: T2 control (3 calls) -> baselines -> T2 treatments (16x3) + T3 (16x3).
Post-processing per DESIGN_LOCK: recentering, clipping, moderator shrink x0.5,
identity ATE calibration. Writes data/t2_cells_main.csv, data/t2_cells_moderator.csv,
data/t3_ate.csv. Logs to logs/t23_target/."""
import json, subprocess, pathlib, time, statistics, sys, csv, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from stimuli import FILLERS, INTERVENTIONS, EW_FORECAST_DESC, CASE_TEXTS

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGDIR = ROOT/"logs"/"t23_target"; LOGDIR.mkdir(parents=True, exist_ok=True)
DATADIR = ROOT/"data"; DATADIR.mkdir(exist_ok=True)

OUTCOMES = ["trust_multidimensional","trust_post","distrust_post","funding_perceptions",
            "policy_role_mean","inst_trust_mean","belief_post","concern_mean","policy_general",
            "policy_specific_mean","behavior_mean","donation_ams","newsletter_signup"]
SCALES = {o:"0-100 slider mean" for o in OUTCOMES}
SCALES["donation_ams"]="mean dollars donated, 0-10"
SCALES["newsletter_signup"]="proportion subscribing, 0-1"
DESER = {"trust_multidimensional":"12-item trust in climate scientists composite (competence, integrity, benevolence, openness)",
 "trust_post":"single-item trust in climate scientists","distrust_post":"single-item DIStrust in climate scientists",
 "funding_perceptions":"support for federal climate research funding (100=far too little is being spent)",
 "policy_role_mean":"climate scientists should engage in policy-making (4 items)",
 "inst_trust_mean":"trust in EPA/NASA/NOAA/universities/federal government (5 items)",
 "belief_post":"accuracy of 'human activities are causing climate change'",
 "concern_mean":"climate concern/seriousness/importance (3 items)",
 "policy_general":"US government should do more to reduce global warming",
 "policy_specific_mean":"support for 7 specific climate policies","behavior_mean":"likelihood of 6 personal climate behaviors next 12 months",
 "donation_ams":"dollars of $10 bonus donated to American Meteorological Society","newsletter_signup":"subscribed to Katharine Hayhoe's Talking Climate newsletter after an offer page"}
ANCHORS = {"trust_multidimensional":"~63-70","trust_post":"~62-68 (Dem ~78, Rep ~48)","distrust_post":"~30-36",
 "funding_perceptions":"~60-66","policy_role_mean":"~62-68","inst_trust_mean":"~55-62 (NASA/NOAA high, fed gov ~40)",
 "belief_post":"~65-70 (58% of US adults say mostly human-caused)","concern_mean":"~55-62 (65% at least somewhat worried)",
 "policy_general":"~62-68 (74% support regulating CO2)","policy_specific_mean":"~62-68 (popular items 70-80; food/fuel taxes 45-55)",
 "behavior_mean":"~40-50","donation_ams":"~$3-4.5","newsletter_signup":"~0.05-0.15"}
MODS = {"gender":["Male","Female","Other"],"age_band":["18-29","30-44","45-59","60+"],
 "race":["White / Caucasian","Black / African American","Hispanic / Latino","Asian / Asian American","Other"],
 "education":["Less than high school","High school diploma / GED","Some college or Associate's degree","Bachelor's degree","Master's degree / Professional degree","Doctorate degree / Ph.D."],
 "income":["Less than $30,000","$30,000 to $55,999","$56,000 to $99,999","$100,000 to $167,999","$168,000 or more"],
 "party":["Republican","Democrat","Independent","Other"]}
WTS = {"gender":[.485,.505,.01],"age_band":[.202,.260,.229,.309],"race":[.602,.123,.181,.067,.027],
 "education":[.09,.28,.26,.23,.11,.03],"income":[.20,.20,.25,.20,.15],"party":[.29,.30,.36,.05]}
EVIDENCE = """- Typical one-shot climate text interventions: pooled d~0.08 (~1-2 points on 0-100) (Rode et al. 2021 meta-analysis).
- Best arms in a global climate megastudy: belief +2.3, policy +2.6, info-sharing +12 pp; NO arm moved effortful behavior (several backfired) (Vlasceanu et al. 2024).
- History-of-climate-science paragraph raised belief +2.36 and perceived scientist skill +2.08 (0-100), across parties, US RCT (PNAS Nexus 2024).
- Trust in climate scientists is the DIRECT target of these interventions: expect the largest shifts there (~+1-3), smaller distal shifts.
- Best-in-class low-cost advocacy interventions reach ~10pp only on low-cost actions (US megastudy 2026).
- Treatment effects are largely homogeneous across demographics; only party (and targeted-group relevance) shows reliable moderation."""

def outcome_table(base=None):
    rows=[]
    for o in OUTCOMES:
        b = f" | this study's forecast control mean: {base[o]}" if base else ""
        rows.append(f"{o} | {SCALES[o]} | {DESER[o]} | US baseline evidence: {ANCHORS[o]}{b}")
    return "\n".join(rows)

_lock=threading.Lock(); COST={"usd":0.0}

def call(prompt, tag):
    for a in range(3):
        try:
            r=subprocess.run(["claude","-p","--model","claude-fable-5","--output-format","json",
                              "--disallowed-tools","*","--no-session-persistence"],
                             input=prompt, capture_output=True, text=True, timeout=900)
            out=json.loads(r.stdout)
            with _lock: COST["usd"]+=out.get("total_cost_usd",0.0)
            (LOGDIR/f"{tag}_a{a}.json").write_text(json.dumps({"tag":tag,"prompt":prompt,"raw":out},indent=1))
            txt=out["result"].strip()
            if txt.startswith("```"): txt=txt.strip("`").lstrip("json").strip()
            return json.loads(txt)
        except Exception as e:
            (LOGDIR/f"{tag}_a{a}_err.txt").write_text(str(e)); time.sleep(2*(a+1))
    raise RuntimeError(f"{tag} failed 3x")

def t2_prompt(kind, stim, base=None):
    sub = """- Party is the dominant moderator on all climate outcomes: Democrats score far higher than Republicans on trust/belief/concern/policy (e.g., trust gaps of 25-40 points); Independents in between, "Other" near Independents.
- Education raises trust/belief modestly (5-15 points across the range); age effects small (older slightly lower on policy support, higher on trust in institutions varies); race: Black and Hispanic Americans express somewhat higher climate concern than White Americans on average but slightly lower institutional trust; income effects weak.
- Treatment effects are usually HOMOGENEOUS; keep subgroup deviations from this condition's mean close to the documented BASELINE gaps."""
    tmpl=open(ROOT/"pipelines"/"tier2_cells_prompt_v1.txt").read().split("---BEGIN PROMPT---")[1].split("---END PROMPT---")[0].strip()
    return (tmpl.replace("{CONDITION_KIND}", kind).replace("{STIMULUS_TEXT}", stim)
            .replace("{OUTCOME_TABLE_WITH_BASELINES}", outcome_table(base))
            .replace("{SUBGROUP_EVIDENCE}", sub))

def t3_prompt(stim, base):
    tmpl=open(ROOT/"pipelines"/"tier3_forecast_prompt_v1.txt").read().split("---BEGIN PROMPT---")[1].split("---END PROMPT---")[0].strip()
    return (tmpl.replace("{INTERVENTION_TEXT}", stim)
            .replace("{OUTCOME_TABLE}", outcome_table(base)).replace("{EVIDENCE_TABLE}", EVIDENCE))

def med(dicts, path):
    vals=[]
    for d in dicts:
        try:
            x=d
            for k in path: x=x[k]
            vals.append(float(x))
        except Exception: pass
    return statistics.median(vals) if vals else None

def clip(o,v):
    lo,hi=(0,10) if o=="donation_ams" else ((0,1) if o=="newsletter_signup" else (0,100))
    return max(lo,min(hi,v))

def agg_t2(dicts):
    main={o: med(dicts,["main",o]) for o in OUTCOMES}
    mods={m:{lvl:{o: med(dicts,["moderators",m,lvl,o]) for o in OUTCOMES} for lvl in MODS[m]} for m in MODS}
    return main,mods

def postprocess(main,mods):
    out={}
    for m,levels in mods.items():
        w=WTS[m]
        for o in OUTCOMES:
            lv=[levels[l][o] if levels[l][o] is not None else main[o] for l in MODS[m]]
            lv=[main[o]+0.5*(x-main[o]) for x in lv]                # moderator shrink x0.5
            avg=sum(wi*xi for wi,xi in zip(w,lv))
            lv=[clip(o, x + (main[o]-avg)) for x in lv]            # recenter to main mean
            for l,x in zip(MODS[m],lv): out[(m,l,o)]=x
    return out

def main():
    stims=dict(INTERVENTIONS)
    stims["Extreme weather predictions"]=EW_FORECAST_DESC+CASE_TEXTS[1]
    # --- T2 control ---
    ctrl_stim="Participants read ONE of three neutral off-topic filler texts (the history of neckties, the rules of baseball, or types of dances). Example (neckties):\n\n"+FILLERS["neckties"]
    ctrl=[call(t2_prompt("CONTROL (neutral filler)", ctrl_stim), f"t2_control_f{k}") for k in range(3)]
    cmain,cmods=agg_t2(ctrl)
    cmain={o:clip(o,v) for o,v in cmain.items()}
    print("control means:", json.dumps({k:round(v,2) for k,v in cmain.items()}), flush=True)
    base={o:round(cmain[o],2) for o in OUTCOMES}
    # --- T2 treatments + T3, parallel ---
    jobs=[]
    for cond,stim in stims.items():
        for k in range(3):
            jobs.append(("t2",cond,k,t2_prompt("INTERVENTION", stim, base)))
            jobs.append(("t3",cond,k,t3_prompt(stim, base)))
    res={}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(call,p,f"{t}_{cond[:12].replace(' ','_').replace('/','-')}_f{k}"):(t,cond,k)
              for (t,cond,k,p) in jobs}
        for f in as_completed(futs):
            t,cond,k=futs[f]
            try: res[(t,cond,k)]=f.result()
            except Exception as e: print("FAIL",t,cond,k,e, flush=True)
    # --- assemble T2 ---
    t2main_rows=[("control",o,round(cmain[o],3)) for o in OUTCOMES]
    t2mod_rows=[]
    cpost=postprocess(cmain,cmods)
    for (m,l,o),v in cpost.items(): t2mod_rows.append(("control",m,l,o,round(v,3)))
    t3_rows=[]
    for cond in stims:
        d2=[res[k] for k in [("t2",cond,i) for i in range(3)] if k in res]
        m2,md2=agg_t2(d2)
        m2={o:clip(o, m2[o] if m2[o] is not None else cmain[o]) for o in OUTCOMES}
        for o in OUTCOMES: t2main_rows.append((cond,o,round(m2[o],3)))
        for (m,l,o),v in postprocess(m2,md2).items(): t2mod_rows.append((cond,m,l,o,round(v,3)))
        d3=[res[k] for k in [("t3",cond,i) for i in range(3)] if k in res]
        for o in OUTCOMES:
            ates=[]
            for d in d3:
                try:
                    arr=d if isinstance(d,list) else d.get("forecasts",[])
                    for it in arr:
                        if it["outcome"]==o: ates.append(float(it["ate"]))
                except Exception: pass
            t3_rows.append((cond,o,round(statistics.median(ates),4) if ates else 0.0))
    with open(DATADIR/"t2_cells_main.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["condition","outcome","mean"]); w.writerows(t2main_rows)
    with open(DATADIR/"t2_cells_moderator.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["condition","moderator","moderator_level","outcome","mean"]); w.writerows(t2mod_rows)
    with open(DATADIR/"t3_ate.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["condition","outcome","ate"]); w.writerows(t3_rows)
    print(json.dumps({"t2_main":len(t2main_rows),"t2_mod":len(t2mod_rows),"t3":len(t3_rows),
                      "cost_usd":round(COST["usd"],2)},indent=1))

if __name__=="__main__":
    main()
