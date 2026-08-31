#!/usr/bin/env python3
"""Extract verbatim stimulus texts from survey/questionnaire.txt.
Provides: FILLERS (3), INTERVENTIONS (15 static texts), extreme_weather(state) builder,
STATE_CASE mapping. Names = canonical condition labels."""
import pathlib, re

QTXT = (pathlib.Path(__file__).resolve().parent.parent /
        "silicon-sample-submission" / "survey" / "questionnaire.txt").read_text()

def _section(header):
    pat = re.compile(rf"^### {re.escape(header)}\s*$", re.M)
    m = pat.search(QTXT)
    start = m.end()
    nxt = re.compile(r"^### |^----------------------------------------------------------------------$", re.M)
    m2 = nxt.search(QTXT, start)
    return QTXT[start:m2.start() if m2 else len(QTXT)].strip()

FILLERS = {
    "neckties": _section("control — filler text 1 of 3: The History of Neckties"),
    "baseball": _section("control — filler text 2 of 3: The Rules of Baseball"),
    "dances":   _section("control — filler text 3 of 3: Different Types of Dances"),
}

STATIC = ["Corporate reliance", "Social justice", "Interview Prof. Maraun", "Funding",
          "Oil industry misinformation", "Measurement & modeling (1)", "Former skeptics",
          "High public trust", "Measurement & modeling (2)", "Peer-review",
          "Scientist community helpers", "Consensus", "Portrait Prof. Cherry",
          "Model accuracy", "Interview Prof. Sebille"]
INTERVENTIONS = {name: _section(name) for name in STATIC}

CASE1 = set("Alabama Arkansas Delaware Florida Georgia Illinois Indiana Iowa Kansas Kentucky Louisiana Maryland Mississippi Missouri Nebraska Ohio Oklahoma Pennsylvania Tennessee Texas Virginia".split()) | {"North Carolina","North Dakota","South Carolina","South Dakota","West Virginia","Washington D.C.","Washington, D.C."}
CASE2 = set("Alaska Arizona California Colorado Idaho Montana Nevada Oregon Utah Washington Wyoming Hawaii".split()) | {"New Mexico"}
CASE3 = set("Connecticut Maine Massachusetts Michigan Minnesota Vermont Wisconsin".split()) | {"New Hampshire","New Jersey","New York","Rhode Island"}
CASE_LABEL = {1: "states with high or recurrent flood risk",
              2: "states with high or increasing wildfire risk",
              3: "states with severe cold, snow, ice, or blizzards"}

_ew = _section("Extreme weather predictions")
def _case_text(n, title):
    m = re.search(rf"^Case {n}\n({re.escape(title)}.*?)(?=^Case \d|\Z|^References)", _ew, re.M | re.S)
    return m.group(1).strip()
CASE_TEXTS = {1: _case_text(1, "Predicting Floods Before They Strike"),
              2: _case_text(2, "Detecting Wildfires Before They Spread"),
              3: _case_text(3, "Forecasting Winter Storms Before They Strike"),
              4: _case_text(4, "Improving Warnings for Extreme Weather Before It Strikes")}

def state_case(state):
    if state in CASE1: return 1
    if state in CASE2: return 2
    if state in CASE3: return 3
    return 4

def extreme_weather(state):
    c = state_case(state)
    if c == 4:
        intro = ("You are living in the United States, a country facing risks by more and more "
                 "extreme weather events. Please read the text on the following page carefully. It "
                 "describes a real project in the U.S., working particularly on reducing the risks "
                 "from these hazards by helping communities prepare for extreme weather.")
    else:
        intro = (f"You reported that you are currently living in {state}, one of several "
                 f"{CASE_LABEL[c]}. Please read the text on the following page carefully. It "
                 "describes a real project in the U.S., working particularly on reducing the risks "
                 "from these hazards by helping communities prepare for extreme weather.")
    return intro + "\n\n" + CASE_TEXTS[c]

EW_FORECAST_DESC = ("STATE-ADAPTIVE ARM: each participant first reports their home U.S. state, then reads "
    "an intro naming their state and its dominant extreme-weather risk category, then ONE matching text: "
    "flood-prone states get 'Predicting Floods Before They Strike' (NOAA/NSSL flood forecasting helps "
    "communities prepare); wildfire states get 'Detecting Wildfires Before They Spread' (DHS/NASA early "
    "detection); winter-storm states get 'Forecasting Winter Storms Before They Strike' (NWS/university "
    "forecasting). All versions end: climate scientists working alongside forecasters improve forecasts "
    "and early-warning systems, protecting communities with earlier, more reliable warnings. "
    "Example (flood version, verbatim):\n\n" )

if __name__ == "__main__":
    assert len(INTERVENTIONS) == 15 and all(len(v) > 200 for v in INTERVENTIONS.values()), \
        {k: len(v) for k, v in INTERVENTIONS.items()}
    assert all(len(v) > 300 for v in FILLERS.values())
    assert len(CASE_TEXTS) == 4 and all(len(v) > 400 for v in CASE_TEXTS.values())
    print("stimuli OK:", {k: len(v) for k, v in list(INTERVENTIONS.items())[:3]},
          "| fillers", {k: len(v) for k, v in FILLERS.items()},
          "| EW cases", {k: len(v) for k, v in CASE_TEXTS.items()})
    print("state_case checks:", state_case("Texas"), state_case("California"),
          state_case("New York"), state_case("Prefer not to say"))
