import sys,re,html,subprocess
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"
for arg in sys.argv[1:]:
    name,url=arg.split('=',1)
    r=subprocess.run(['curl','-sL','-A',UA,'-m','45','-w','%{http_code}',url],capture_output=True)
    body=r.stdout[:-3].decode('utf8','ignore'); code=r.stdout[-3:].decode()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',body,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
    open(name+'.txt','w').write(t); print(code,name,len(t))
