"""One calibration run: small GPT on the first D train tokens for E epochs, then eval.

  python pilot/train.py --tokens 2e6 --epochs 1 --seed 0
Writes results/<tag>.json with val loss (fixed 256k-token held-out slice) and BLiMP-fast accuracy.
The LR schedule spans the whole run, so every (D, E) gets its own full warmup + cosine decay.
"""
import argparse, json, math, time
from pathlib import Path
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from tokenizers import Tokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--tokens", type=float, required=True)
ap.add_argument("--epochs", type=int, default=1)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--layers", type=int, default=6)
ap.add_argument("--dim", type=int, default=256)
ap.add_argument("--ctx", type=int, default=256)
ap.add_argument("--batch", type=int, default=16)
ap.add_argument("--lr", type=float, default=2e-3)
ap.add_argument("--val_tokens", type=int, default=262144)
ap.add_argument("--tag", default=None)
args = ap.parse_args()

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "results"; OUT.mkdir(exist_ok=True)
dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(args.seed); np.random.seed(args.seed)

tok = Tokenizer.from_file(str(DATA / "tok.json")); V = tok.get_vocab_size(); EOS = tok.token_to_id("<eos>")
train = torch.from_numpy(np.load(DATA / "train.npy")[: int(args.tokens)].astype(np.int64))
val = torch.from_numpy(np.load(DATA / "val.npy")[: args.val_tokens].astype(np.int64))

class Block(nn.Module):
    def __init__(s, d, h):
        super().__init__(); s.h = h
        s.n1, s.n2 = nn.RMSNorm(d), nn.RMSNorm(d)
        s.qkv, s.o = nn.Linear(d, 3 * d, bias=False), nn.Linear(d, d, bias=False)
        s.up, s.down = nn.Linear(d, 4 * d, bias=False), nn.Linear(4 * d, d, bias=False)
    def forward(s, x):
        B, T, C = x.shape
        q, k, v = s.qkv(s.n1(x)).view(B, T, 3, s.h, C // s.h).permute(2, 0, 3, 1, 4)
        x = x + s.o(F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(B, T, C))
        return x + s.down(F.gelu(s.up(s.n2(x))))

class GPT(nn.Module):
    def __init__(s, V, d, L, ctx):
        super().__init__()
        s.emb, s.pos = nn.Embedding(V, d), nn.Embedding(ctx, d)
        s.blocks = nn.ModuleList(Block(d, d // 64) for _ in range(L)); s.nf = nn.RMSNorm(d)
        s.apply(lambda m: nn.init.normal_(m.weight, std=0.02) if isinstance(m, (nn.Linear, nn.Embedding)) else None)
    def forward(s, idx):
        x = s.emb(idx) + s.pos(torch.arange(idx.shape[1], device=idx.device))
        for b in s.blocks: x = b(x)
        return s.nf(x) @ s.emb.weight.T  # tied embeddings

model = GPT(V, args.dim, args.layers, args.ctx).to(dev)
n_params = sum(p.numel() for p in model.parameters())
opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.1)

# Epochs: each epoch visits every non-overlapping ctx window of the D-token prefix once, in a fresh order.
n_win = (len(train) - 1) // args.ctx
g = torch.Generator().manual_seed(args.seed)
order = torch.cat([torch.randperm(n_win, generator=g) for _ in range(args.epochs)])
steps = len(order) // args.batch; warm = max(10, steps // 20)
lr_at = lambda i: args.lr * (i + 1) / warm if i < warm else args.lr * 0.5 * (1 + math.cos(math.pi * (i - warm) / (steps - warm)))

t0 = time.time(); model.train()
for i in range(steps):
    w = order[i * args.batch:(i + 1) * args.batch] * args.ctx
    xy = torch.stack([train[j:j + args.ctx + 1] for j in w.tolist()]).to(dev)
    for pg in opt.param_groups: pg["lr"] = lr_at(i)
    loss = F.cross_entropy(model(xy[:, :-1]).reshape(-1, V), xy[:, 1:].reshape(-1))
    opt.zero_grad(set_to_none=True); loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
train_s = time.time() - t0

@torch.no_grad()
def val_loss():
    model.eval(); tot, n = 0.0, 0
    for j in range(0, len(val) - args.ctx - 1, args.ctx * 32):
        chunk = val[j:j + args.ctx * 32 + 1]; m = (len(chunk) - 1) // args.ctx
        x = chunk[: m * args.ctx].view(m, args.ctx).to(dev); y = chunk[1: m * args.ctx + 1].view(m, args.ctx).to(dev)
        tot += F.cross_entropy(model(x).reshape(-1, V), y.reshape(-1), reduction="sum").item(); n += y.numel()
    return tot / n

@torch.no_grad()
def blimp():
    model.eval(); pairs = json.load(open(DATA / "blimp_fast.json")); per = {}
    sents = [s for p in pairs for s in (p["good"], p["bad"])]
    seqs = [[EOS] + e.ids for e in tok.encode_batch(sents)]
    scores = []
    for b in range(0, len(seqs), 256):
        chunk = seqs[b:b + 256]; T = max(map(len, chunk))
        x = torch.full((len(chunk), T), EOS, dtype=torch.long)
        mask = torch.zeros(len(chunk), T - 1)
        for r, s in enumerate(chunk): x[r, :len(s)] = torch.tensor(s); mask[r, :len(s) - 1] = 1
        x = x.to(dev); lp = F.log_softmax(model(x[:, :-1]).float(), -1).gather(-1, x[:, 1:, None])[..., 0]
        scores.extend((lp.cpu() * mask).sum(1).tolist())
    for k, p in enumerate(pairs):
        per.setdefault(p["uid"], []).append(scores[2 * k] > scores[2 * k + 1])
    macro = float(np.mean([np.mean(v) for v in per.values()]))
    return macro, {u: float(np.mean(v)) for u, v in per.items()}

vl = val_loss(); bl, bl_per = blimp()
tag = args.tag or f"D{int(args.tokens/1e6*100)/100}M_E{args.epochs}_s{args.seed}"
res = dict(tag=tag, tokens=int(len(train)), epochs=args.epochs, seed=args.seed, params=n_params,
           tokens_seen=steps * args.batch * args.ctx, steps=steps, train_seconds=round(train_s, 1),
           tok_per_s=round(steps * args.batch * args.ctx / train_s), val_loss=vl, blimp=bl, blimp_per=bl_per, device=dev)
json.dump(res, open(OUT / f"{tag}.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "blimp_per"}))
