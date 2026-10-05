import sys, json, urllib.request, urllib.parse
frm=sys.argv[1]
for s in sys.argv[2:]:
    url='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f'title_and_abstract.search:{s},from_publication_date:{frm}','sort':'cited_by_count:desc','per_page':10,'mailto':'research@example.org'})
    d=json.load(urllib.request.urlopen(url,timeout=30))
    print('##',s, d['meta']['count'])
    for w in d['results']:
        src=(w.get('primary_location') or {}).get('source') or {}
        print(f" {w['publication_date']} c={w['cited_by_count']} {w['title'][:120]} | {src.get('display_name')} | {w['doi']}")
