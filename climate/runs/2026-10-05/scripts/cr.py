import sys, json, urllib.parse, urllib.request
def q(s, n=8):
    url = "https://api.crossref.org/works?rows=%d&select=title,issued,DOI,container-title,is-referenced-by-count&query.bibliographic=%s&mailto=research@example.org" % (n, urllib.parse.quote(s))
    try:
        d = json.load(urllib.request.urlopen(url, timeout=25))
    except Exception as e:
        print("ERR", e); return
    print("##", s)
    for it in d["message"]["items"]:
        y = it.get("issued",{}).get("date-parts",[[None]])[0][0]
        print(y, it.get("is-referenced-by-count"), (it.get("title") or [""])[0][:140], "|", (it.get("container-title") or [""])[0][:40], "|", it.get("DOI"))
import time
for s in sys.argv[1:]:
    time.sleep(3)
    q(s)
