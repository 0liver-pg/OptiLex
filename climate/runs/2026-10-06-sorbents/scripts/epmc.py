import sys, json, urllib.parse, urllib.request, os
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
L = int(os.environ.get("ABS", "600"))
url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%s&format=json&pageSize=%d&resultType=core" % (urllib.parse.quote(q), n)
try:
    d = json.load(urllib.request.urlopen(url, timeout=40))
except Exception as e:
    print("ERR", e); sys.exit()
print("hits", d.get("hitCount"))
for r in d.get("resultList", {}).get("result", []):
    j = (r.get("journalInfo") or {}).get("journal", {}).get("isoabbreviation")
    print("-", r.get("pubYear"), "|", r.get("title"), "|", j, "| doi:", r.get("doi"), "| pmcid:", r.get("pmcid"), "| OA:", r.get("isOpenAccess"))
    a = r.get("abstractText") or ""
    print("   ", a[:L].replace("\n", " "))
