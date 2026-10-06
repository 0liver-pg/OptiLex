import numpy as np, heapq, time, json, sys
from fastvp import lifted_phases
k=np.pi/2; ns=np.arange(10); g=np.where(ns==0,1.,2.); CH=5.0
M=int(sys.argv[1]) if len(sys.argv)>1 else 8; SUB=80//M
rg=np.linspace(1,3,M*SUB+1)
bare=4/k*np.sum(g*np.sin(lifted_phases(np.zeros(M*SUB),rg,k,ns))**2)
def minsin2(lo,hi):
    # min of sin^2 over [lo,hi] (lifted)
    m=np.ceil(lo/np.pi)*np.pi
    out=np.minimum(np.sin(lo)**2,np.sin(hi)**2)
    return np.where(m<=hi,0.0,out)
def node_bound(L,H):
    dlo=lifted_phases(np.repeat(L,SUB),rg,k,ns); dhi=lifted_phases(np.repeat(H,SUB),rg,k,ns)
    return 4/k*np.sum(g*minsin2(dlo,dhi)), dlo, dhi
L0=np.zeros(M);H0=np.full(M,CH)
b0,_,_=node_bound(L0,H0)
heap=[(b0,0,L0,H0)];cnt=1;t=time.time();hist=[]
budget=int(sys.argv[2]) if len(sys.argv)>2 else 1000
while cnt<budget:
    bnd,_,L,H=heapq.heappop(heap)
    w=H-L; j=int(np.argmax(w)); mid=0.5*(L[j]+H[j])
    for (l,h) in [(L[j],mid),(mid,H[j])]:
        L2=L.copy();H2=H.copy();L2[j]=l;H2[j]=h
        bb,_,_=node_bound(L2,H2); cnt+=1
        heapq.heappush(heap,(max(bb,bnd),cnt,L2,H2))
    if cnt%100<2: hist.append((cnt,heap[0][0]/bare)); print(cnt, round(heap[0][0],4), round(heap[0][0]/bare,4), round(time.time()-t,1), flush=True)
print('final global LB',heap[0][0],'ratio',heap[0][0]/bare,'open nodes',len(heap))
json.dump({'M':M,'nodes':cnt,'LB':heap[0][0],'ratio':heap[0][0]/bare,'hist':hist},open(f'bnb_M{M}.json','w'))
