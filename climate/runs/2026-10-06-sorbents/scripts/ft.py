# usage: ft.py PMCID regex [context_chars]  -> prints sentences from full text matching regex
import sys, re, urllib.request, os, html
pmcid = sys.argv[1]; pat = sys.argv[2]; ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 220
fn = f"ft_{pmcid}.txt"
if not os.path.exists(fn):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    x = urllib.request.urlopen(url, timeout=60).read().decode("utf8", "ignore")
    x = re.sub(r"<ref-list.*?</ref-list>", " ", x, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", x)); t = re.sub(r"\s+", " ", t)
    open(fn, "w").write(t)
t = open(fn).read()
print("len", len(t))
seen = []
for m in re.finditer(pat, t, flags=re.I):
    s, e = max(0, m.start() - ctx), min(len(t), m.end() + ctx)
    if seen and s < seen[-1]: continue
    seen.append(e)
    print("...", t[s:e], "...\n")
    if len(seen) > 40: break
