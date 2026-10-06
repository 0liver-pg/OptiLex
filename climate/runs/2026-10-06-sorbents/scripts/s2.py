import sys, json, urllib.request, urllib.parse, time
def search(q, n=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search?limit=%d&fields=title,year,abstract,externalIds,venue,openAccessPdf,tldr&query=%s" % (n, urllib.parse.quote(q))
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=60)); break
        except Exception as e:
            print("retry", e); time.sleep(4*(attempt+1)); d = {}
    for r in d.get("data", []) or []:
        print("##", r.get("year"), "|", r.get("title"), "|", r.get("venue"), "| doi:", (r.get("externalIds") or {}).get("DOI"), "| pdf:", (r.get("openAccessPdf") or {}).get("url"))
        print((r.get("abstract") or "")[:1800] or ("TLDR: " + ((r.get("tldr") or {}).get("text") or ""))); print()
for q in sys.argv[1:]:
    print("=== QUERY:", q); search(q); time.sleep(2)
