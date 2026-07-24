"""
Minimal final top-up: just 1 entry each for Cybersecurity and Smart Systems to hit 50.
Plus validation of final corpus.
"""
import csv, unicodedata, re

MASTER_FILE = r"D:\acadeval-1\datasets\AcadEval_Corpus_MASTER.csv"
COLUMNS = [
    "Project_ID","Title","Abstract","Domain","Sub_Domain","Keywords",
    "Objectives","Problem_Statement","Methodology","Modules",
    "Technologies","Algorithms","Dataset_Used","Programming_Languages",
    "Frameworks","Tools","Hardware","Expected_Output",
    "GitHub_Link","Paper_Link","Authors","Institution",
    "Year","Source","Publication_Type","Faculty_Label","Notes"
]
DEFAULTS = {
    "Objectives":"Develop and validate the proposed system with measurable performance benchmarks.",
    "Problem_Statement":"Current solutions lack automation or scalability for this domain.",
    "Methodology":"Literature review -> dataset collection -> system design -> evaluation",
    "Modules":"Data Pipeline, Core Engine, API Layer, User Interface",
    "Dataset_Used":"Publicly available domain-specific datasets",
    "Hardware":"Standard workstation / GPU server",
    "Expected_Output":"Functional prototype with accuracy metrics and documentation",
    "GitHub_Link":"","Paper_Link":"","Authors":"AcadEval Synthetic",
    "Institution":"AcadEval Corpus Generator","Source":"AcadEval_SyntheticGenerator",
    "Publication_Type":"Project Proposal","Faculty_Label":"",
    "Notes":"Synthetically generated for domain coverage"
}

def normalize_title(t):
    t = t.strip().lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

FINAL_ENTRIES = [
    {"Domain":"Cybersecurity","Sub_Domain":"Threat Hunting","Title":"Proactive Threat Hunting Platform Using ML Behavioral Analytics","Abstract":"ML-powered threat hunting platform enabling security analysts to proactively search for stealthy threats using hypothesis-driven investigation workflows, anomaly scoring, and interactive timeline visualization.","Keywords":"threat hunting,ML,behavioral analytics,SOC,proactive security","Technologies":"Python,Elastic Stack,scikit-learn,React","Algorithms":"Anomaly Detection,Clustering","Programming_Languages":"Python","Frameworks":"FastAPI,React","Year":"2024"},
    {"Domain":"Smart Systems","Sub_Domain":"Predictive Analytics","Title":"Factory-Wide OEE Prediction and Bottleneck Identification Using ML","Abstract":"Machine learning platform analyzing production data from PLCs, SCADA, and MES systems to predict Overall Equipment Effectiveness, identify hidden bottlenecks, and generate autonomous improvement recommendations.","Keywords":"OEE,manufacturing analytics,SCADA,MES,predictive analytics,Industry 4.0","Technologies":"Python,OPC-UA,XGBoost,React","Algorithms":"XGBoost,Bottleneck Analysis","Programming_Languages":"Python","Frameworks":"FastAPI,React","Year":"2024"},
]

def main():
    rows = []
    seen = set()
    with open(MASTER_FILE, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nt = normalize_title(row.get("Title",""))
            seen.add(nt)
            rows.append(row)

    added = 0
    for e in FINAL_ENTRIES:
        nt = normalize_title(e.get("Title",""))
        if nt in seen:
            print(f"SKIP: {e['Title'][:50]}")
            continue
        seen.add(nt)
        for col in COLUMNS:
            if col not in e or not e[col]:
                e[col] = DEFAULTS.get(col,"")
        rows.append(e)
        added += 1

    for i, r in enumerate(rows, start=1):
        r["Project_ID"] = f"P{i:06d}"

    with open(MASTER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    dc = Counter(r.get("Domain","?") for r in rows)
    print(f"Added {added} entries. Total: {len(rows)} entries, {len(dc)} domains")
    
    below_50 = [(d,c) for d,c in dc.items() if c < 50]
    if below_50:
        print("\nDomains BELOW 50:")
        for d,c in sorted(below_50, key=lambda x: x[1]):
            print(f"  {d}: {c}")
    else:
        print("\nAll domains have >= 50 entries!")

if __name__ == "__main__":
    main()
