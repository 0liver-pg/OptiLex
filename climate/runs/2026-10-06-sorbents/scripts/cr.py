import sys, json, urllib.parse, urllib.request, re
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12; frm = sys.argv[3] if len(sys.argv) > 3 else "2023-01-01"
url = "https://api.crossref.org/works?query.bibliographic=%s&rows=%d&filter=from-pub-date:%s,type:journal-article&select=title,DOI,issued,container-title,abstract&mailto=oliver@massengineering.ai" % (urllib.parse.quote(q), n, frm)
url = url.replace("&mailto=oliver@massengineering.ai", "")
d = json.load(urllib.request.urlopen(url, timeout=40))
for it in d["message"]["items"]:
    t = (it.get("title") or [""])[0]; y = it.get("issued", {}).get("date-parts", [[None]])[0][0]
    j = (it.get("container-title") or [""])[0]
    print("-", y, "|", t, "|", j, "|", it.get("DOI"))
    a = re.sub(r"<[^>]+>", "", it.get("abstract") or "")
    if a: print("    ", a[:int(sys.argv[4]) if len(sys.argv) > 4 else 500])
