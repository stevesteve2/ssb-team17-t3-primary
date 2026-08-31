#!/usr/bin/env python3
"""Package three entries into template-repo copies under entries/.
- entries/T1_primary        (tier 1, claude-sonnet-5 simulation)      -> team_17_T1_primary_v1.csv (via make clean)
- entries/T2_secondary-1    (tier 2, fable cell forecasts)            -> team_17_T2_secondary-1_v1_cells_{main,moderator}.csv
- entries/T3_secondary-2    (tier 3, fable evidence-conditioned ATEs) -> team_17_T3_secondary-2_v1.csv
Then: delete examples, write metadata.json, copy transparency artifacts + logs archive,
run make manifest + make check per entry. Nothing is released/deposited."""
import json, shutil, subprocess, pathlib, csv, sys, tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT/"silicon-sample-submission"
ENT = ROOT/"entries"

COMMON = dict(team_id="team_17", team_name="team_17 (Rathje)",
              contact="srathje@alumni.stanford.edu",
              creators=[{"name":"Rathje, Steve","affiliation":"","orcid":""}],
              abstract="", license="CC-BY-4.0",
              code_repository="(this deposit)", code_doi=None,
              disclosure_class="A", escrow_doi=None, zenodo_doi=None,
              coverage={"interventions":16,"outcomes":13}, blinding_attestation=True)

ENTRIES = [
 dict(dir="T1_secondary-1", tier=1, entry="secondary-1",
      approach_family="per-respondent simulation (batched generation), single model",
      models=["claude-haiku-4-5"]),
 dict(dir="T2_secondary-2", tier=2, entry="secondary-2",
      approach_family="direct cell-level forecast, literature-conditioned, single model, k=3 ensemble",
      models=["claude-fable-5"]),
 dict(dir="T3_primary", tier=3, entry="primary",
      approach_family="direct effect forecast, literature-conditioned, single model, k=3 ensemble",
      models=["claude-fable-5"]),
]

ARTIFACTS = ["RUN_CONFIG.md","DESIGN_LOCK.md","DESIGN_LOCK.sha256","BENCHMARK_SPEC.md",
             "EVIDENCE_MEMO.md","EVIDENCE_LIBRARY.csv","TARGET_EVIDENCE_MAP.csv"]
LOGMAP = {"T1_secondary-1":["probe_t1","probe_t1_batch","t1_target"],
          "T2_secondary-2":["probe_t3","t23_target"],
          "T3_primary":["probe_t3","t23_target"]}

def sh(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)[-3500:]

def make_entry(e):
    d = ENT/e["dir"]
    if d.exists(): shutil.rmtree(d)
    shutil.copytree(TPL, d, ignore=shutil.ignore_patterns(".git"))
    for f in (d/"predictions").glob("example_*"): f.unlink()
    ex = d/"raw_data_deposit"/"example_raw_export.csv"
    if ex.exists(): ex.unlink()
    meta = dict(COMMON); meta.update(tier=e["tier"], entry=e["entry"],
                                     approach_family=e["approach_family"], models=e["models"],
                                     prediction_files=[])
    (d/"metadata.json").write_text(json.dumps(meta, indent=2)+"\n")
    # transparency artifacts
    (d/"method").mkdir(exist_ok=True)
    for a in ARTIFACTS: shutil.copy(ROOT/a, d/"method"/a)
    shutil.copytree(ROOT/"pipelines", d/"method"/"pipelines",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT/"validation", d/"method"/"validation",
                    ignore=shutil.ignore_patterns("__pycache__"))
    # raw logs archive
    with tarfile.open(d/"method"/"raw_model_logs.tar.gz","w:gz") as tar:
        for sub in LOGMAP[e["dir"]]:
            p = ROOT/"logs"/sub
            if p.exists(): tar.add(p, arcname=f"logs/{sub}")
    # predictions
    if e["tier"]==1:
        shutil.copy(ROOT/"data"/"tier1_raw_export.csv", d/"raw_data_deposit"/"raw_export.csv")
        rc,out = sh("make clean", d); print(e["dir"], "make clean rc:", rc); print(out[-1200:])
    elif e["tier"]==2:
        shutil.copy(ROOT/"data"/"t2_cells_main.csv",
                    d/"predictions"/"team_17_T2_secondary-2_v1_cells_main.csv")
        shutil.copy(ROOT/"data"/"t2_cells_moderator.csv",
                    d/"predictions"/"team_17_T2_secondary-2_v1_cells_moderator.csv")
    else:
        shutil.copy(ROOT/"data"/"t3_ate.csv", d/"predictions"/"team_17_T3_primary_v1.csv")
    rc,out = sh("make manifest", d); print(e["dir"], "make manifest rc:", rc)
    rc,out = sh("make check", d);    print(e["dir"], "make check rc:", rc); print(out)

if __name__=="__main__":
    ENT.mkdir(exist_ok=True)
    which = sys.argv[1:] or [e["dir"] for e in ENTRIES]
    for e in ENTRIES:
        if e["dir"] in which: make_entry(e)
