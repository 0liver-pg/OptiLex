import re,sys
f=sys.argv[1]; ctx=int(sys.argv[2]); maxn=int(sys.argv[3]); pats=sys.argv[4:]
t=open(f,errors='ignore').read(); t=re.sub(r'\s+',' ',t)
for p in pats:
    hits=list(re.finditer(p,t)); print('==',f,p,len(hits))
    last=-9999; n=0
    for m in hits:
        if m.start()-last<ctx: continue
        last=m.start(); n+=1
        print('  ..',t[max(0,m.start()-ctx):m.start()+ctx])
        if n>=maxn: break
