import sys, json, urllib.request, urllib.parse
def q(s, frm='2025-01-01', n=8):
    url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':s,'filter':f'from_publication_date:{frm}','sort':'cited_by_count:desc','per_page':n,'mailto':'research@example.org'})
    d=json.load(urllib.request.urlopen(url,timeout=30))
    print('##',s)
    for w in d['results']:
        print(f" {w['publication_date']} c={w['cited_by_count']} {w['title'][:110]} | {(w.get('primary_location') or {}).get('source') and w['primary_location']['source']['display_name']} | {w['doi']}")
for s in sys.argv[1:]: q(s)
