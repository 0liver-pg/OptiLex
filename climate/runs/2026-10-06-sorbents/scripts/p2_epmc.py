import sys, json, urllib.parse, urllib.request
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 12; L = int(sys.argv[3]) if len(sys.argv) > 3 else 350
url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" + urllib.parse.quote(q) + f"&format=json&pageSize={n}&resultType=core"
d = json.load(urllib.request.urlopen(url, timeout=40))
print('hits', d.get('hitCount'))
for r in d.get('resultList', {}).get('result', []):
    print('-', r.get('pubYear'), '|', r.get('title'), '|', r.get('journalInfo', {}).get('journal', {}).get('isoabbreviation'), '| doi:', r.get('doi'), '| pmcid:', r.get('pmcid'))
    a = (r.get('abstractText') or '').replace('\n', ' ')
    if L: print('    ', a[:L])
