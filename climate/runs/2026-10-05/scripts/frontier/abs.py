import sys, json, urllib.request, urllib.parse
for doi in sys.argv[1:]:
    d=json.load(urllib.request.urlopen('https://api.openalex.org/works/https://doi.org/'+doi+'?mailto=research@example.org',timeout=30))
    inv=d.get('abstract_inverted_index') or {}
    pos=sorted((p,w) for w,ps in inv.items() for p in ps)
    print('##',d['publication_date'],d['title'],'|',[a['author']['display_name'] for a in d['authorships']][:6])
    print(' '.join(w for p,w in pos) or '(no abstract)'); print()
