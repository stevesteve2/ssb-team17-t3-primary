#!/usr/bin/env python3
"""Batched Tier-1 probe: 3 calls x 10 respondents, claude-sonnet-5, control condition.
Gates (DESIGN_LOCK v1.1): SD(trust_post) in [10,35]; no two identical rows; party
gradient (Dem mean - Rep mean trust_post >= 10); baselines within +/-15 of anchors."""
import json, subprocess, pathlib, time, statistics, random, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from run_tier1_probe import ITEMS, NECKTIES

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGDIR = ROOT / "logs" / "probe_t1_batch"; LOGDIR.mkdir(parents=True, exist_ok=True)
random.seed(20260830)

GEN = [("Male",.485),("Female",.505),("Other",.01)]
AGE = [("18-29",.202),("30-44",.260),("45-59",.229),("60+",.309)]
RACE = [("White / Caucasian",.602),("Hispanic / Latino",.181),("Black / African American",.123),("Asian / Asian American",.067),("Other",.027)]
EDU = [("Less than high school",.09),("High school diploma / GED",.28),("Some college or Associate's degree",.26),("Bachelor's degree",.23),("Master's degree / Professional degree",.11),("Doctorate degree / Ph.D.",.03)]
INC = [("Less than $30,000",.20),("$30,000 to $55,999",.20),("$56,000 to $99,999",.25),("$100,000 to $167,999",.20),("$168,000 or more",.15)]
PARTY = [("Republican",.29),("Democrat",.30),("Independent",.36),("Other",.05)]
STATES = ["California","Texas","Florida","New York","Pennsylvania","Illinois","Ohio","Georgia","North Carolina","Michigan","New Jersey","Virginia","Washington","Arizona","Tennessee","Massachusetts","Indiana","Missouri","Maryland","Wisconsin","Colorado","Minnesota","South Carolina","Alabama","Louisiana","Kentucky","Oregon","Oklahoma","Connecticut","Utah"]
BANDS = {"18-29":(1997,2008),"30-44":(1982,1996),"45-59":(1967,1981),"60+":(1940,1966)}

def draw(d):
    r=random.random(); c=0
    for v,p in d:
        c+=p
        if r<=c: return v
    return d[-1][0]

def make_profile():
    band = draw(AGE)
    return dict(GENDER=draw(GEN), YEAR_BIRTH=random.randint(*BANDS[band]), RACE=draw(RACE),
                EDUCATION=draw(EDU), INCOME=draw(INC), PARTY=draw(PARTY), STATE=random.choice(STATES))

def batch_prompt(profiles):
    items = "\n".join(f"{i+1}. [{k}] {q}" for i,(k,q) in enumerate(ITEMS))
    plist = "\n".join(
        f"R{j+1}: {p['GENDER']}, born {p['YEAR_BIRTH']}, {p['RACE']}, {p['EDUCATION']}, "
        f"income {p['INCOME']}, {p['PARTY']}, lives in {p['STATE']}" for j,p in enumerate(profiles))
    return f"""You are simulating TEN different ordinary American adults, each independently taking the same online survey for a small payment. They are DIFFERENT people who never interact; their answers must be independent and reflect each person's own politics, age, and life. They are not experts, activists, or unusually attentive. People answer quickly, with gut feelings, imperfect consistency, and round numbers often (0/25/50/75/100 attract answers). A single short text rarely changes anyone's mind much.

THE TEN PEOPLE:
{plist}

EACH person separately: (1) read the definition "Climate scientists study changes in the Earth's climate over time and how they might affect the planet in the future."; (2) read this text carefully:
--- TEXT SHOWN ---
{NECKTIES}
--- END TEXT ---
(3) answered ALL items below. Sliders are integers 0-100. Donation is whole dollars 0-10. Newsletter is 1=yes subscribed / 0=no.

ITEMS (in this exact order):
{items}

OUTPUT: exactly 10 lines. Line j = "Rj," followed by {len(ITEMS)} comma-separated values in item order for person j. No other text."""

def main():
    rows, cost, t0 = [], 0.0, time.time()
    for c in range(3):
        profiles = [make_profile() for _ in range(10)]
        r = subprocess.run(["claude","-p","--model","claude-sonnet-5","--output-format","json",
                            "--disallowed-tools","*","--no-session-persistence"],
                           input=batch_prompt(profiles), capture_output=True, text=True, timeout=600)
        out = json.loads(r.stdout); cost += out.get("total_cost_usd",0.0)
        (LOGDIR/f"call{c}.json").write_text(json.dumps({"profiles":profiles,"raw":out}, indent=1))
        for line in out["result"].strip().splitlines():
            line=line.strip()
            m=re.match(r"R(\d+)\s*,(.*)$", line)
            if not m: continue
            vals=[float(x) for x in m.group(2).split(",") if x.strip()!=""]
            if len(vals)==len(ITEMS):
                rows.append((profiles[int(m.group(1))-1], vals, c))
        print(f"call{c}: rows so far {len(rows)}, cost ${cost:.3f}", flush=True)
    idx={k:j for j,(k,_) in enumerate(ITEMS)}
    tp=[v[idx["trust_post_1"]] for _,v,_ in rows]
    dem=[v[idx["trust_post_1"]] for p,v,_ in rows if p["PARTY"]=="Democrat"]
    rep=[v[idx["trust_post_1"]] for p,v,_ in rows if p["PARTY"]=="Republican"]
    uniq=len({tuple(v) for _,v,_ in rows})
    rep_gap = (statistics.mean(dem)-statistics.mean(rep)) if dem and rep else None
    report={"n_rows":len(rows),"unique_rows":uniq,"cost_usd":round(cost,3),
            "wall_s":round(time.time()-t0,1),
            "trust_post_mean":round(statistics.mean(tp),1),"trust_post_sd":round(statistics.stdev(tp),1),
            "dem_minus_rep_trust":round(rep_gap,1) if rep_gap is not None else None,
            "belief_mean":round(statistics.mean([v[idx["belief_post_1"]] for _,v,_ in rows]),1),
            "policy_general_mean":round(statistics.mean([v[idx["policy_general_1"]] for _,v,_ in rows]),1),
            "donation_mean":round(statistics.mean([v[idx["donation"]] for _,v,_ in rows]),2),
            "newsletter_rate":round(statistics.mean([v[idx["newsletter"]] for _,v,_ in rows]),2),
            "range_violations":sum(1 for _,v,_ in rows for j,x in enumerate(v)
                                   if not (0<=x<=10 if ITEMS[j][0]=="donation" else 0<=x<=100)),
            "gates":{}}
    g=report["gates"]
    g["sd_in_10_35"]= 10<=report["trust_post_sd"]<=35
    g["all_rows_unique"]= uniq==len(rows)
    g["party_gradient_ge10"]= rep_gap is not None and rep_gap>=10
    g["parse_ge_27_of_30"]= len(rows)>=27
    g["PASS"]=all(g.values())
    (ROOT/"validation"/"probe_t1_batch_results.json").write_text(json.dumps(report,indent=1))
    print(json.dumps(report,indent=1))

if __name__=="__main__":
    main()
