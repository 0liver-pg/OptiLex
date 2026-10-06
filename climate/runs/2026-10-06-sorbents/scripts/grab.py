import sys,re,html,urllib.request
def grab(url,kws,width=220,maxhits=5,save=None):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'})
    try:
        raw=urllib.request.urlopen(req,timeout=40).read()
    except Exception as e:
        print('ERR',url,e);return ''
    t=raw.decode('utf8','ignore')
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t))
    t=re.sub(r'\s+',' ',t)
    print('LEN',len(t),url)
    if save: open(save,'w').write(t)
    for kw in kws:
        hits=list(re.finditer(kw,t))
        print('==',kw,len(hits))
        for m in hits[:maxhits]:
            print('  ..',t[max(0,m.start()-width):m.start()+width])
    return t
if __name__=='__main__':
    grab(sys.argv[1],sys.argv[2:],save=None)
