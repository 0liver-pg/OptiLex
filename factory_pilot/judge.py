"""Blind scoring of ideas.jsonl.

1. Clustering judge: sees all ideas shuffled under random IDs (no condition labels) and groups them into
   mechanism families. Diversity = distinct families per condition (and a rarefied count at equal n).
2. Per-idea judge (same blind IDs): novelty 0/1/2, soundness 1-5, nearest known work.
Both judges run twice with different shuffles; agreement between the two passes is reported, since an
LLM judge's reliability is itself one of the open questions.
3. A non-LLM check: mean pairwise lexical distance (1 - Jaccard over content words) within each condition.
"""
import json, random, re, subprocess, itertools, statistics as st
from pathlib import Path

D = Path(__file__).parent
ideas = [json.loads(l) for l in (D / "ideas.jsonl").read_text().splitlines()]

def claude(p, effort="high"):
    r = subprocess.run(["claude", "-p", "--model", "opus", "--system-prompt",
                        "You are a meticulous senior ML researcher with encyclopedic knowledge of the efficient-training literature. Output only valid JSON.",
                        "--tools", "", "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
                        "--effort", effort, "--output-format", "json"], input=p, capture_output=True, text=True, timeout=1800)
    txt = json.loads(r.stdout)["result"]
    return json.loads(txt[txt.find("{") if txt.find("{") >= 0 and (txt.find("[") < 0 or txt.find("{") < txt.find("[")) else txt.find("["):
                          max(txt.rfind("}"), txt.rfind("]")) + 1])

def run_pass(seed):
    rng = random.Random(seed); order = list(range(len(ideas))); rng.shuffle(order)
    ids = {k: f"I{n:03d}" for n, k in enumerate(order)}
    body = "\n\n".join(f"[{ids[k]}]\n{ideas[k]['text']}" for k in order)
    clus = claude("Group these research ideas into families that share the SAME core mechanism (two ideas are in "
                  "the same family if a researcher would call them variants of one approach). Use as many families as "
                  "needed. Return JSON {\"families\": [{\"name\": str, \"ids\": [str]}]} covering every id exactly once.\n\n" + body)
    score = claude("For EACH idea give: novelty (0 = a standard, well-known technique or a light rename of one; "
                   "1 = a recombination or new application of known techniques; 2 = no close precedent you know of), "
                   "soundness (1-5: would it plausibly improve data, compute AND energy efficiency together at matched "
                   "compute, given how LM training actually works), and nearest (the closest known method or paper, "
                   "short). Be harsh and specific. Return JSON {\"scores\": [{\"id\": str, \"novelty\": int, "
                   "\"soundness\": int, \"nearest\": str}]}.\n\n" + body)
    inv = {v: k for k, v in ids.items()}
    fam = {inv[i]: f["name"] for f in clus["families"] for i in f["ids"] if i in inv}
    sc = {inv[s["id"]]: s for s in score["scores"] if s["id"] in inv}
    return fam, sc

def words(t): return set(w for w in re.findall(r"[a-z]{4,}", t.lower()))

passes = [run_pass(s) for s in (1, 2)]
json.dump([[{str(k): v for k, v in fam.items()}, {str(k): v for k, v in sc.items()}] for fam, sc in passes],
          open(D / "judgements.json", "w"), indent=1)

conds = ["clean", "ask", "noisy"]; rng = random.Random(0)
report = {}
for c in conds:
    idx = [k for k, x in enumerate(ideas) if x["cond"] == c]
    r = {"n": len(idx)}
    for p, (fam, sc) in enumerate(passes, 1):
        fams = [fam.get(k) for k in idx if k in fam]
        r[f"families_p{p}"] = len(set(fams))
        # rarefied: expected distinct families in a random subsample of 15
        r[f"families_at15_p{p}"] = round(st.mean(len(set(rng.sample(fams, 15))) for _ in range(500)), 1) if len(fams) >= 15 else None
        r[f"novelty_mean_p{p}"] = round(st.mean(sc[k]["novelty"] for k in idx if k in sc), 2)
        r[f"novelty2_frac_p{p}"] = round(sum(sc[k]["novelty"] == 2 for k in idx if k in sc) / len(idx), 2)
        r[f"soundness_mean_p{p}"] = round(st.mean(sc[k]["soundness"] for k in idx if k in sc), 2)
        r[f"sound4plus_frac_p{p}"] = round(sum(sc[k]["soundness"] >= 4 for k in idx if k in sc) / len(idx), 2)
        r[f"novel_and_sound_p{p}"] = sum(sc[k]["novelty"] >= 1 and sc[k]["soundness"] >= 4 for k in idx if k in sc)
    ws = [words(ideas[k]["text"]) for k in idx]
    r["lexical_distance"] = round(st.mean(1 - len(a & b) / len(a | b) for a, b in itertools.combinations(ws, 2)), 3)
    report[c] = r

# judge reliability across the two blind passes
common = [k for k in range(len(ideas)) if k in passes[0][1] and k in passes[1][1]]
report["judge_agreement"] = {
    "novelty_exact": round(sum(passes[0][1][k]["novelty"] == passes[1][1][k]["novelty"] for k in common) / len(common), 2),
    "soundness_within1": round(sum(abs(passes[0][1][k]["soundness"] - passes[1][1][k]["soundness"]) <= 1 for k in common) / len(common), 2),
    "soundness_spearman": round(st.correlation([passes[0][1][k]["soundness"] for k in common],
                                               [passes[1][1][k]["soundness"] for k in common], method="ranked"), 2)}
report["gen_cost_usd"] = round(sum(x["cost"] or 0 for x in ideas), 2)
report["models"] = sorted({m for x in ideas for m in x["model"]})
json.dump(report, open(D / "report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
