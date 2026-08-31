#!/usr/bin/env python3
"""TIER-1 TARGET RUN (locked design v1.1). claude-sonnet-5, batched 10 respondents/call.
500-profile matched pool x16 interventions + 1,000 control (pool x2, re-randomized fillers).
Writes data/tier1_raw_export.csv (plain one-header, codebook qualtrics labels, numeric codes).
Logs every call to logs/t1_target/. Cost cap $25 hard-aborts."""
import json, subprocess, pathlib, time, random, re, sys, csv, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "validation"))
from stimuli import FILLERS, INTERVENTIONS, extreme_weather, state_case, CASE_LABEL
from run_tier1_probe import ITEMS

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGDIR = ROOT / "logs" / "t1_target"; LOGDIR.mkdir(parents=True, exist_ok=True)
DATADIR = ROOT / "data"; DATADIR.mkdir(exist_ok=True)
random.seed(20260831)

GEN=[("Male",.485),("Female",.505),("Other",.01)]
AGE=[("18-29",.202),("30-44",.260),("45-59",.229),("60+",.309)]
RACE=[("White / Caucasian",.602),("Hispanic / Latino",.181),("Black / African American",.123),("Asian / Asian American",.067),("Other",.027)]
EDU=[("Less than high school",.09),("High school diploma / GED",.28),("Some college or Associate's degree",.26),("Bachelor's degree",.23),("Master's degree / Professional degree",.11),("Doctorate degree / Ph.D.",.03)]
INC=[("Less than $30,000",.20),("$30,000 to $55,999",.20),("$56,000 to $99,999",.25),("$100,000 to $167,999",.20),("$168,000 or more",.15)]
PARTY=[("Republican",.29),("Democrat",.30),("Independent",.36),("Other",.05)]
STATES=[("California",.117),("Texas",.087),("Florida",.067),("New York",.058),("Pennsylvania",.038),
 ("Illinois",.037),("Ohio",.035),("Georgia",.032),("North Carolina",.031),("Michigan",.030),
 ("New Jersey",.027),("Virginia",.026),("Washington",.023),("Arizona",.022),("Tennessee",.021),
 ("Massachusetts",.021),("Indiana",.020),("Missouri",.018),("Maryland",.018),("Wisconsin",.017),
 ("Colorado",.017),("Minnesota",.017),("South Carolina",.016),("Alabama",.015),("Louisiana",.014),
 ("Kentucky",.013),("Oregon",.013),("Oklahoma",.012),("Connecticut",.011),("Utah",.010),
 ("Iowa",.009),("Nevada",.009),("Arkansas",.009),("Mississippi",.009),("Kansas",.009),
 ("New Mexico",.006),("Nebraska",.006),("Idaho",.006),("West Virginia",.005),("Hawaii",.004),
 ("New Hampshire",.004),("Maine",.004),("Montana",.003),("Rhode Island",.003),("Delaware",.003),
 ("South Dakota",.003),("North Dakota",.002),("Alaska",.002),("Vermont",.002),("Wyoming",.002)]
BANDS={"18-29":(1997,2008),"30-44":(1982,1996),"45-59":(1967,1981),"60+":(1940,1966)}
GCODE={"Male":1,"Female":2,"Other":3}
RCODE={"White / Caucasian":1,"Black / African American":2,"Hispanic / Latino":3,"Asian / Asian American":4,"Other":5}
ECODE={e:i+1 for i,(e,_) in enumerate(EDU)}
ICODE={e:i+1 for i,(e,_) in enumerate(INC)}
PCODE={"Republican":1,"Democrat":2,"Independent":3,"Other":4}

def draw(d):
    r=random.random(); c=0
    for v,p in d:
        c+=p
        if r<=c: return v
    return d[-1][0]

def make_pool(n=500):
    pool=[]
    for i in range(n):
        band=draw(AGE)
        pool.append(dict(pid=f"p{i:04d}", GENDER=draw(GEN), YEAR_BIRTH=random.randint(*BANDS[band]),
                         RACE=draw(RACE), EDUCATION=draw(EDU), INCOME=draw(INC),
                         PARTY=draw(PARTY), STATE=draw(STATES)))
    return pool

ITEMS_TXT="\n".join(f"{i+1}. [{k}] {q}" for i,(k,q) in enumerate(ITEMS))

def batch_prompt(profiles, stim, ew=False):
    lines=[]
    for j,p in enumerate(profiles):
        extra=""
        if ew:
            c=state_case(p["STATE"])
            extra=f" (their state is one of several {CASE_LABEL[c]})"
        lines.append(f"R{j+1}: {p['GENDER']}, born {p['YEAR_BIRTH']}, {p['RACE']}, {p['EDUCATION']}, "
                     f"income {p['INCOME']}, {p['PARTY']}, lives in {p['STATE']}{extra}")
    plist="\n".join(lines)
    n=len(profiles)
    return f"""You are simulating {n} different ordinary American adults, each independently taking the same online survey for a small payment. They are DIFFERENT people who never interact; their answers must be independent and reflect each person's own politics, age, and life. They are not experts, activists, or unusually attentive. People answer quickly, with gut feelings, imperfect consistency, and round numbers often (0/25/50/75/100 attract answers). A single short text rarely changes anyone's mind much; let it influence each person only as much as it truly would.

THE {n} PEOPLE:
{plist}

EACH person separately: (1) read the definition "Climate scientists study changes in the Earth's climate over time and how they might affect the planet in the future."; (2) read this text carefully:
--- TEXT SHOWN ---
{stim}
--- END TEXT ---
(3) answered ALL items below. Sliders are integers 0-100. Donation is whole dollars 0-10. Newsletter is 1=yes subscribed / 0=no.

ITEMS (in this exact order):
{ITEMS_TXT}

OUTPUT: exactly {n} lines. Line j = "Rj," followed by {len(ITEMS)} comma-separated values in item order for person j. No other text."""

MODEL="claude-haiku-4-5"
BATCH=20
_lock=threading.Lock(); STATE={"cost":0.0,"done":0,"abort":False}
CAP=25.0

def run_call(tag, prompt, profiles):
    for attempt in range(3):
        if STATE["abort"]: return []
        try:
            r=subprocess.run(["claude","-p","--model",MODEL,"--output-format","json",
                              "--disallowed-tools","*","--no-session-persistence"],
                             input=prompt, capture_output=True, text=True, timeout=900)
            out=json.loads(r.stdout)
            with _lock:
                STATE["cost"]+=out.get("total_cost_usd",0.0)
                if STATE["cost"]>CAP: STATE["abort"]=True
            (LOGDIR/f"{tag}_a{attempt}.json").write_text(json.dumps({"tag":tag,"raw":out},indent=1))
            rows=[]
            for line in out["result"].strip().splitlines():
                m=re.match(r"^\s*R(\d+)\s*,(.*)$", line.strip())
                if not m: continue
                vals=[float(x) for x in m.group(2).split(",") if x.strip()!=""]
                j=int(m.group(1))-1
                if len(vals)==len(ITEMS) and 0<=j<len(profiles):
                    rows.append((profiles[j], vals))
            if len(rows)>=len(profiles)-1:   # tolerate 1 dropped row per call
                return rows
        except Exception as e:
            (LOGDIR/f"{tag}_a{attempt}_err.txt").write_text(str(e))
        time.sleep(2*(attempt+1))
    return rows if 'rows' in dir() else []

def build_jobs():
    pool=make_pool(500)
    jobs=[]  # (tag, condition, profiles, stim, ew)
    for ci,(cond,text) in enumerate(INTERVENTIONS.items()):
        cpool=[dict(p, pid=f"{p['pid']}_c{ci:02d}") for p in pool]
        for b in range(500//BATCH):
            jobs.append((f"c{ci:02d}_{b:02d}", cond, cpool[b*BATCH:(b+1)*BATCH], text, False))
    # Extreme weather: group by case for a shared case text
    bycase={1:[],2:[],3:[]}
    for p in pool: bycase[state_case(p["STATE"])].append(dict(p, pid=f"{p['pid']}_cEW"))
    bi=0
    for c,plist in bycase.items():
        stim=extreme_weather(plist[0]["STATE"]).split("\n\n",1)[1]  # shared case text (intro via profile line)
        for s in range(0,len(plist),BATCH):
            grp=plist[s:s+BATCH]
            if grp: jobs.append((f"ew_{bi:02d}", "Extreme weather predictions", grp, stim, True)); bi+=1
    # Control: pool x2, fillers randomized
    fill=list(FILLERS.values())
    ctrl=[dict(p, pid=p["pid"]+("A" if rep==0 else "B")) for rep in range(2) for p in pool]
    random.shuffle(ctrl)
    for b in range(1000//BATCH):
        grp=ctrl[b*BATCH:(b+1)*BATCH]
        jobs.append((f"ctl_{b:03d}", "control", grp, random.choice(fill), False))
    return jobs

def execute(jobs, label):
    got=[]
    t0=time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(run_call, t, batch_prompt(pr, st, ew), pr): (t,c,pr)
              for (t,c,pr,st,ew) in jobs}
        for f in as_completed(futs):
            t,c,pr=futs[f]
            for p,v in f.result(): got.append((c,p,v))
            with _lock: STATE["done"]+=1
            if STATE["done"]%50==0:
                print(f"[{label}] {STATE['done']} calls, {len(got)} rows, "
                      f"${STATE['cost']:.2f}, {(time.time()-t0)/60:.0f}m", flush=True)
            if STATE["abort"]:
                print("COST CAP HIT — aborting", flush=True); break
    return got

def main():
    t0=time.time()
    cap=float(sys.argv[sys.argv.index("--cap")+1]) if "--cap" in sys.argv else 25.0
    global CAP; CAP=cap
    jobs=build_jobs()
    all_rows=[]
    prev=DATADIR/"tier1_raw_export.csv"
    if "--resume" in sys.argv and prev.exists():
        inv_g={v:k for k,v in GCODE.items()}; inv_r={v:k for k,v in RCODE.items()}
        inv_e={v:k for k,v in ECODE.items()}; inv_i={v:k for k,v in ICODE.items()}
        inv_p={v:k for k,v in PCODE.items()}
        with open(prev) as fh:
            for r in csv.DictReader(fh):
                p=dict(pid=r["profile_id"], GENDER=inv_g[int(r["gender"])],
                       YEAR_BIRTH=int(r["year_birth"]), RACE=inv_r[int(r["race"])],
                       EDUCATION=inv_e[int(r["education"])], INCOME=inv_i[int(r["income"])],
                       PARTY=inv_p[int(r["party"])], STATE="")
                all_rows.append((r["condition"], p, [float(r[k]) for k,_ in ITEMS]))
        have={(c,p["pid"]) for c,p,_ in all_rows}
        jobs=[(f"res_{t}",c,[p for p in pr if (c,p["pid"]) not in have],st,ew)
              for (t,c,pr,st,ew) in jobs]
        jobs=[j for j in jobs if j[2]]
        print(f"resume: {len(all_rows)} rows loaded; {len(jobs)} calls remaining", flush=True)
    else:
        print(f"{len(jobs)} calls planned", flush=True)
    all_rows+=execute(jobs, "main")
    # top-up pass: regenerate any missing (condition, pid) rows, up to 2 rounds
    for rnd in range(2):
        have={(c,p["pid"]) for c,p,_ in all_rows}
        missing=[]
        for (t,c,pr,st,ew) in jobs:
            miss=[p for p in pr if (c,p["pid"]) not in have]
            if miss: missing.append((f"top{rnd}_{t}", c, miss, st, ew))
        n_miss=sum(len(m[2]) for m in missing)
        if n_miss==0 or STATE["abort"]: break
        print(f"top-up round {rnd}: {n_miss} missing rows in {len(missing)} calls", flush=True)
        all_rows+=execute(missing, f"top{rnd}")

    hdr=(["condition","profile_id","gender","year_birth","race","education","income","party"]
         + [k for k,_ in ITEMS])
    with open(DATADIR/"tier1_raw_export.csv","w",newline="") as fh:
        w=csv.writer(fh); w.writerow(hdr)
        for c,p,v in all_rows:
            w.writerow([c, p["pid"] if c!="control" else p["pid"],
                        GCODE[p["GENDER"]], p["YEAR_BIRTH"], RCODE[p["RACE"]],
                        ECODE[p["EDUCATION"]], ICODE[p["INCOME"]], PCODE[p["PARTY"]]]
                       + [int(x) if x==int(x) else x for x in v])
    counts={}
    for c,_,_ in all_rows: counts[c]=counts.get(c,0)+1
    print(json.dumps({"total_rows":len(all_rows),"cost_usd":round(STATE['cost'],2),
                      "wall_min":round((time.time()-t0)/60,1),"by_condition":counts},indent=1))

if __name__=="__main__":
    main()
