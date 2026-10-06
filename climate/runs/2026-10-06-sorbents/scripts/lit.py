import json, sys, time, urllib.parse, urllib.request
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8"}), timeout=40) as r:
        return json.load(r)
def crossref(q, n=6):
    url = "https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) + f"&rows={n}&select=title,issued,DOI,is-referenced-by-count,container-title"
    try: d = get(url)
    except Exception as e: print("  crossref ERROR", e); return
    print(f"## crossref: {q}")
    for w in d["message"]["items"]:
        y = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
        print(f"   {y} | {str((w.get('title') or ['?'])[0])[:120]} | {(w.get('container-title') or ['?'])[0][:30]} | {w['DOI']} | cited {w.get('is-referenced-by-count')}")
def epmc(q, n=6):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=%d&query=%s" % (n, urllib.parse.quote(q))
    try: d = get(url)
    except Exception as e: print("  epmc ERROR", e); return
    print(f"## europepmc: {q}  [hits {d.get('hitCount')}]")
    for w in d.get("resultList", {}).get("result", []):
        print(f"   {w.get('pubYear')} | {str(w.get('title'))[:120]} | {w.get('journalTitle','')[:25]} | {w.get('doi')} | cited {w.get('citedByCount')}")
mode = sys.argv[1]
for q in sys.argv[2:]:
    (crossref if mode == "c" else epmc)(q); time.sleep(1.0)
