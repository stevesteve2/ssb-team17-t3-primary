#!/usr/bin/env python3
"""Tier-1 validation probe: 12 synthetic respondents, control condition (neckties filler),
whole-session single call, compressed CSV output. Measures cost/respondent, schema
validity, dispersion, baseline sanity. Logs to logs/probe_t1/."""
import json, subprocess, pathlib, time, statistics, csv, sys, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGDIR = ROOT / "logs" / "probe_t1"
LOGDIR.mkdir(parents=True, exist_ok=True)

NECKTIES = """Neckties date back hundreds of years, coming into existence as the direct result of a war. In 1660, in celebration of its hard-fought victory over the Ottoman Empire, a regiment from Croatia (then part of the Habsburg Monarchy) visited Paris. The soldiers were presented as heroes to Louis XIV, a monarch well known for his tendency toward personal adornment. The officers of this regiment were wearing brightly colored handkerchiefs fashioned of silk around their necks. These neck cloths - which probably descended from the Roman fascalia worn by orators to warm the vocal chords - struck the fancy of the king, and he soon made them an insignia of royalty as he created a regiment of Royal Cravattes. Vanity reigns supreme. The word "cravat," is derived from the word "Croat"."""

ITEMS = [
 ("trust_competent_1","How incompetent or competent are most climate scientists? (0=Very incompetent, 100=Very competent)"),
 ("trust_intelligent_1","How unintelligent or intelligent are most climate scientists? (0-100)"),
 ("trust_qualified_1","How unqualified or qualified are most climate scientists? (0-100)"),
 ("trust_honest_1","How dishonest or honest are most climate scientists? (0-100)"),
 ("trust_ethical_1","How unethical or ethical are most climate scientists? (0-100)"),
 ("trust_sincere_1","How insincere or sincere are most climate scientists? (0-100)"),
 ("trust_concerned_1","How unconcerned or concerned are most climate scientists about people's wellbeing? (0-100)"),
 ("trust_improve_1","How uneager or eager are most climate scientists to improve others' lives? (0-100)"),
 ("trust_considerate_1","How inconsiderate or considerate are most climate scientists of others' interests? (0-100)"),
 ("trust_feedback_1","How open are most climate scientists to feedback? (0=Not open at all, 100=Very open)"),
 ("trust_transparent_1","How unwilling or willing are most climate scientists to be transparent? (0-100)"),
 ("trust_attention_1","How much attention do climate scientists pay to other people's views? (0=Very little, 100=A great deal)"),
 ("funding_5","Is the federal government spending too much, too little or about right on climate change research? (0=far too little, 50=about right, 100=far too much)"),
 ("inst_trust_epa_1","How much do you trust the EPA? (0=not at all, 100=very strongly)"),
 ("inst_trust_nasa_1","How much do you trust NASA? (0-100)"),
 ("inst_trust_noaa_1","How much do you trust NOAA? (0-100)"),
 ("inst_trust_uni_1","How much do you trust universities and colleges? (0-100)"),
 ("inst_trust_gov_1","How much do you trust the federal government? (0-100)"),
 ("policy_1_1","Climate scientists should work closely with policy makers to integrate scientific results into policy-making. (0=Strongly disagree, 100=Strongly agree)"),
 ("policy_2_1","Climate scientists should actively advocate for specific policies. (0-100)"),
 ("policy_3_1","Climate scientists should communicate their findings to policy makers. (0-100)"),
 ("policy_4_1","Climate scientists should be more involved in the policy-making process. (0-100)"),
 ("trust_post_1","How much do you trust climate scientists? (0=not at all, 100=very strongly)"),
 ("distrust_1","How much do you distrust climate scientists? (0=not at all, 100=very strongly)"),
 ("donation","Of the $10 bonus, how much would you like to donate to the American Meteorological Society? (whole dollars 0-10)"),
 ("newsletter","[You just saw this offer: 'If you'd like to learn more about climate science and solutions, you can subscribe to the newsletter by climate scientist Katharine Hayhoe. Her newsletter Talking Climate provides short, accessible updates on climate science and climate solutions. Signing up takes less than a minute. Subscribing is optional.'] Did you subscribe to the Talking Climate newsletter? (1=Yes, 0=No)"),
 ("belief_post_1","How accurate is this statement: 'Human activities are causing climate change.' (0=not at all accurate, 100=extremely accurate)"),
 ("concern_1_1","How concerned are you about climate change? (0=Not at all, 100=Extremely)"),
 ("concern_2_1","How serious a problem is climate change? (0-100)"),
 ("concern_3_1","Relative to other issues facing the U.S., how important is climate change? (0=least important, 100=most important)"),
 ("individual_meat_1","Next 12 months, how likely: Eat less meat (0=Not likely at all, 100=Extremely likely)"),
 ("individual_transport_1","Next 12 months, how likely: Walk, bicycle, carpool, or take public transit instead of driving (0-100)"),
 ("individual_solar_1","Next 12 months, how likely: Install a solar panel (0-100)"),
 ("individual_fly_1","Next 12 months, how likely: Less personal air travel (0-100)"),
 ("individual_talk_1","Next 12 months, how likely: Talk to friends/family about importance of climate change (0-100)"),
 ("individual_donate_1","Next 12 months, how likely: Donate to an environmental NGO (0-100)"),
 ("policy_general_1","Oppose or support: 'The U.S. government should do more to reduce global warming' (0=Strongly oppose, 100=Strongly support)"),
 ("policy_specific_1_1","Support/oppose: Raising taxes on fossil fuels (0=Strongly oppose, 100=Strongly support)"),
 ("policy_specific_2_1","Support/oppose: Expanding public transportation infrastructure (0-100)"),
 ("policy_specific_3_1","Support/oppose: Increasing use of sustainable energy such as wind and solar (0-100)"),
 ("policy_specific_4_1","Support/oppose: Protecting forested and land areas (0-100)"),
 ("policy_specific_5_1","Support/oppose: Increasing taxes on carbon-intensive foods like beef and dairy (0-100)"),
 ("policy_specific_6_1","Support/oppose: Investing more in green jobs and businesses (0-100)"),
 ("policy_specific_7_1","Support/oppose: Laws to keep waterways and oceans clean (0-100)"),
]

PROFILES = [
 dict(GENDER="Male", YEAR_BIRTH=1958, RACE="White / Caucasian", EDUCATION="High school diploma / GED", INCOME="$30,000 to $55,999", PARTY="Republican", STATE="Ohio"),
 dict(GENDER="Female", YEAR_BIRTH=1995, RACE="Hispanic / Latino", EDUCATION="Some college or Associate's degree", INCOME="Less than $30,000", PARTY="Democrat", STATE="California"),
 dict(GENDER="Male", YEAR_BIRTH=1979, RACE="Black / African American", EDUCATION="Bachelor's degree", INCOME="$56,000 to $99,999", PARTY="Democrat", STATE="Georgia"),
 dict(GENDER="Female", YEAR_BIRTH=1949, RACE="White / Caucasian", EDUCATION="Some college or Associate's degree", INCOME="$30,000 to $55,999", PARTY="Republican", STATE="Florida"),
 dict(GENDER="Male", YEAR_BIRTH=2002, RACE="Asian / Asian American", EDUCATION="Bachelor's degree", INCOME="$56,000 to $99,999", PARTY="Independent", STATE="Washington"),
 dict(GENDER="Female", YEAR_BIRTH=1988, RACE="White / Caucasian", EDUCATION="Master's degree / Professional degree", INCOME="$100,000 to $167,999", PARTY="Democrat", STATE="New York"),
 dict(GENDER="Male", YEAR_BIRTH=1969, RACE="White / Caucasian", EDUCATION="Less than high school", INCOME="Less than $30,000", PARTY="Independent", STATE="Kentucky"),
 dict(GENDER="Female", YEAR_BIRTH=1975, RACE="Black / African American", EDUCATION="High school diploma / GED", INCOME="$30,000 to $55,999", PARTY="Democrat", STATE="Texas"),
 dict(GENDER="Male", YEAR_BIRTH=1990, RACE="Hispanic / Latino", EDUCATION="Bachelor's degree", INCOME="$100,000 to $167,999", PARTY="Republican", STATE="Arizona"),
 dict(GENDER="Female", YEAR_BIRTH=1962, RACE="White / Caucasian", EDUCATION="Doctorate degree / Ph.D.", INCOME="$168,000 or more", PARTY="Democrat", STATE="Massachusetts"),
 dict(GENDER="Other", YEAR_BIRTH=1998, RACE="Other", EDUCATION="Some college or Associate's degree", INCOME="Less than $30,000", PARTY="Other", STATE="Oregon"),
 dict(GENDER="Female", YEAR_BIRTH=1984, RACE="White / Caucasian", EDUCATION="Bachelor's degree", INCOME="$56,000 to $99,999", PARTY="Independent", STATE="Wisconsin"),
]

TMPL = open(ROOT/"pipelines"/"tier1_respondent_prompt_v1.txt").read()
TMPL = TMPL.split("---BEGIN PROMPT---")[1].split("---END PROMPT---")[0].strip()

def build_prompt(p):
    items = "\n".join(f"{i+1}. [{k}] {q}" for i,(k,q) in enumerate(ITEMS))
    return (TMPL.replace("{GENDER}", str(p["GENDER"])).replace("{YEAR_BIRTH}", str(p["YEAR_BIRTH"]))
            .replace("{RACE}", p["RACE"]).replace("{EDUCATION}", p["EDUCATION"])
            .replace("{INCOME}", p["INCOME"]).replace("{PARTY}", p["PARTY"])
            .replace("{STATE}", p["STATE"]).replace("{STIMULUS_TEXT}", NECKTIES)
            .replace("{ITEM_LIST}", items).replace("{N_ITEMS}", str(len(ITEMS))))

def main():
    rows, total_cost, times, fails = [], 0.0, [], 0
    for i, p in enumerate(PROFILES):
        tag = f"resp{i:02d}"
        t0 = time.time()
        try:
            r = subprocess.run(["claude","-p","--model","claude-fable-5","--output-format","json",
                                "--disallowed-tools","*","--no-session-persistence"],
                               input=build_prompt(p), capture_output=True, text=True, timeout=300)
            out = json.loads(r.stdout); dur = time.time()-t0
            (LOGDIR/f"{tag}.json").write_text(json.dumps({"profile":p,"raw":out,"wall_s":dur}, indent=1))
            total_cost += out.get("total_cost_usd",0.0); times.append(dur)
            line = out["result"].strip().splitlines()[-1]
            vals = [float(x) for x in re.split(r"[,\s]+", line.strip()) if x!=""]
            assert len(vals)==len(ITEMS), f"got {len(vals)} values"
            rows.append((p, vals))
            print(f"{tag}: ok {dur:.0f}s cost so far ${total_cost:.2f}", flush=True)
        except Exception as e:
            fails += 1; print(f"{tag}: FAIL {e}", flush=True)
    # analysis
    idx = {k:j for j,(k,_) in enumerate(ITEMS)}
    def col(k): return [v[idx[k]] for _,v in rows]
    report = {
      "n_ok": len(rows), "n_fail": fails, "total_cost_usd": round(total_cost,3),
      "mean_wall_s": round(statistics.mean(times),1) if times else None,
      "trust_post_mean": round(statistics.mean(col("trust_post_1")),1) if rows else None,
      "trust_post_sd": round(statistics.stdev(col("trust_post_1")),1) if len(rows)>1 else None,
      "belief_mean": round(statistics.mean(col("belief_post_1")),1) if rows else None,
      "policy_general_mean": round(statistics.mean(col("policy_general_1")),1) if rows else None,
      "donation_mean": round(statistics.mean(col("donation")),2) if rows else None,
      "newsletter_rate": round(statistics.mean(col("newsletter")),2) if rows else None,
      "integer_violations": sum(1 for _,v in rows for x in v if x!=int(x)),
      "range_violations": sum(1 for _,v in rows for j,x in enumerate(v)
                              if not (0<=x<=10 if ITEMS[j][0]=="donation" else 0<=x<=100)),
    }
    with open(ROOT/"validation"/"probe_t1_results.json","w") as f:
        json.dump({"report":report,
                   "rows":[{"profile":p,"values":v} for p,v in rows]}, f, indent=1)
    print(json.dumps(report, indent=1))

if __name__ == "__main__":
    main()
