import sys, json, urllib.parse, urllib.request
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10; absn = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%s&format=json&pageSize=%d&resultType=core" % (urllib.parse.quote(q), n)
d = json.load(urllib.request.urlopen(u, timeout=40))
print("hits", d.get("hitCount"))
for r in d.get("resultList", {}).get("result", []):
    print("-", r.get("pubYear"), "|", r.get("title"), "|", (r.get("journalInfo") or {}).get("journal", {}).get("isoabbreviation"), "| doi:", r.get("doi"), "| pmcid:", r.get("pmcid"), "| OA:", r.get("isOpenAccess"), "| id:", r.get("id"), r.get("source"))
    print("    ", (r.get("abstractText") or "")[:absn].replace("\n", " "))
