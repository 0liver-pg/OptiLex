"""Does prompt noise make an LLM's research ideas more diverse or more novel?

Three conditions, N independent one-idea calls each (fresh context per call):
  clean   - plain task prompt
  ask     - plain prompt + an explicit instruction to avoid obvious ideas (controls for "just ask for novelty")
  noisy   - plain prompt + a random distant-domain concept and a random reasoning lens (the "noisy prompt" idea)
Ideas go to ideas.jsonl. judge.py scores them blind.
"""
import json, random, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OUT = Path(__file__).parent / "ideas.jsonl"

TASK = ("Propose ONE concrete research idea for training language models that improves the joint frontier of "
        "data efficiency, compute efficiency and energy efficiency at once (not trading one for another). "
        "Answer in this exact format and nothing else:\n"
        "TITLE: <max 12 words>\nMECHANISM: <3-4 sentences: what changes in training/architecture and why it "
        "should help all three axes>\nTEST: <1 sentence: the cheapest experiment that would falsify it>")
ASK = "\n\nAvoid the obvious or well-known approaches; aim for something genuinely unusual."
CONCEPTS = ["mycelial nutrient networks", "double-entry bookkeeping", "jazz improvisation", "the adaptive immune system",
            "origami crease patterns", "river delta formation", "ant colony pheromone trails", "tax law loopholes",
            "sourdough starter cultures", "orbital mechanics and gravity assists", "Byzantine fault tolerance",
            "bird murmurations", "coral reef symbiosis", "the Dewey decimal system", "glacier crevasse dynamics",
            "medieval guild apprenticeships", "sleep spindles and memory replay", "compressed sensing in MRI",
            "supply-chain just-in-time inventory", "the Japanese game of Go", "enzyme allosteric regulation",
            "crystal annealing in metallurgy", "language creolization", "epidemic contact tracing",
            "auction theory", "kintsugi pottery repair", "phase transitions in magnets", "bee waggle dances",
            "stock-market circuit breakers", "the evolution of the eye"]
LENSES = ["Invert a standard assumption of LM training.", "Borrow the concept's core mechanism literally, then make it work.",
          "Think about what the concept wastes and what it never wastes.", "Start from a failure mode of the concept.",
          "Combine the concept with a known ML technique that seems unrelated.", "Argue from energy and physics first."]

def prompt(cond, rng):
    if cond == "clean": return TASK, {}
    if cond == "ask": return TASK + ASK, {}
    c, l = rng.choice(CONCEPTS), rng.choice(LENSES)
    return TASK + f"\n\nBefore answering, let this unrelated concept seed your thinking: {c}. {l} " \
                  "Do not mention the concept by name in the answer; translate it fully into ML terms.", {"concept": c, "lens": l}

def call(job):
    cond, i, p, meta = job
    r = subprocess.run(["claude", "-p", "--model", "opus", "--system-prompt", "You are an expert ML researcher.",
                        "--tools", "", "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
                        "--effort", "medium", "--output-format", "json"], input=p, capture_output=True, text=True, timeout=600)
    d = json.loads(r.stdout)
    return dict(cond=cond, i=i, text=d["result"].strip(), cost=d.get("total_cost_usd"),
                model=list(d.get("modelUsage", {}).keys()), **meta)

rng = random.Random(7)
jobs = [(c, i, *prompt(c, rng)) for i in range(N) for c in ("clean", "ask", "noisy")]
done = {(d["cond"], d["i"]) for d in map(json.loads, OUT.read_text().splitlines())} if OUT.exists() else set()
jobs = [j for j in jobs if (j[0], j[1]) not in done]
with ThreadPoolExecutor(6) as ex, OUT.open("a") as f:
    for res in ex.map(call, jobs):
        f.write(json.dumps(res) + "\n"); f.flush()
        print(res["cond"], res["i"], res["text"].splitlines()[0][:90], flush=True)
