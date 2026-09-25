"""Download BabyLM-2026 strict-small + BLiMP-fast, train a BPE tokenizer, write token arrays.

Held-out split: every 50th block of 200 lines from each source file goes to validation,
so val covers every domain. Train stream is block-shuffled once (fixed seed) so that
budgets of D tokens are nested prefixes of the same stream.
"""
import json, random, urllib.request
from pathlib import Path
import numpy as np
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders

ROOT = Path(__file__).resolve().parent.parent / "data"
ROOT.mkdir(exist_ok=True)
HF = "https://huggingface.co/datasets/BabyLM-community"
FILES = ["bnc_spoken", "childes", "gutenberg", "open_subtitles", "simple_wiki", "switchboard"]
VOCAB = 8192

def fetch(url, dst):
    if not dst.exists():
        urllib.request.urlretrieve(url, dst)
    return dst

train_blocks, val_blocks = [], []
for f in FILES:
    p = fetch(f"{HF}/BabyLM-2026-Strict-Small/resolve/main/{f}.train.txt", ROOT / f"{f}.txt")
    lines = [l.strip() for l in p.read_text(errors="ignore").splitlines() if l.strip()]
    for i in range(0, len(lines), 200):
        (val_blocks if (i // 200) % 50 == 49 else train_blocks).append("\n".join(lines[i:i + 200]))
random.Random(0).shuffle(train_blocks)

tok = Tokenizer(models.BPE())
tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
tok.decoder = decoders.ByteLevel()
tok.train_from_iterator(train_blocks, trainers.BpeTrainer(
    vocab_size=VOCAB, special_tokens=["<eos>"], initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
tok.save(str(ROOT / "tok.json"))
EOS = tok.token_to_id("<eos>")

def encode(blocks):
    out = []
    for enc in tok.encode_batch(blocks):
        out.extend(enc.ids); out.append(EOS)
    return np.array(out, dtype=np.uint16)

tr, va = encode(train_blocks), encode(val_blocks)
np.save(ROOT / "train.npy", tr); np.save(ROOT / "val.npy", va)

# BLiMP fast (67 paradigms)
listing = json.load(urllib.request.urlopen(
    "https://huggingface.co/api/datasets/BabyLM-community/BabyLM-2026-Strict-Evals/tree/main/evaluation_data/fast_eval/blimp_fast"))
pairs = []
for item in listing:
    p = fetch(f"{HF}/BabyLM-2026-Strict-Evals/resolve/main/{item['path']}", ROOT / ("blimp_" + Path(item["path"]).name))
    for l in p.read_text().splitlines():
        d = json.loads(l)
        pairs.append({"uid": d["UID"], "good": d["sentence_good"], "bad": d["sentence_bad"]})
json.dump(pairs, open(ROOT / "blimp_fast.json", "w"))
print(f"train tokens {len(tr):,}  val tokens {len(va):,}  blimp pairs {len(pairs):,}  paradigms {len(listing)}")
