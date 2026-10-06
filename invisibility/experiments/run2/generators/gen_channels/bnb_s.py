# Covering B&B: branch on s_i = int_{I_i} chi dr (partitions function space). Enclosure per channel:
# delta(r_{i+1}) in [alpha + s_lo*wmin, beta + s_hi*wmax], wmin/wmax = range of w_n(r,delta) over r in I_i (sampled + pad) and delta in box.
import numpy as np, heapq, time, json, sys
from scipy.special import jv, yv
k=np.pi/2; ns=np.arange(10); g=np.where(ns==0,1.,2.); CH=5.0; a,b=1.,3.
M=int(sys.argv[1]); budget=int(sys.argv[2]); h=(b-a)/M
R=np.linspace(a,b,M*8+1)  # sample points
J=jv(ns[:,None],k*R); Y=yv(ns[:,None],k*R); AMP=0.5*np.pi*k**2*R*(J**2+Y**2); TH=np.arctan2(Y,J)  # w = AMP*cos^2(delta+TH)
d0=np.arctan2(jv(ns,k*a),yv(ns,k*a))
bare=4/k*np.sum(g*np.sin(d0)**2)
def cos2_range(x0,x1):
    # min/max of cos^2 on [x0,x1] elementwise
    lo=np.minimum(np.cos(x0)**2,np.cos(x1)**2); hi=np.maximum(np.cos(x0)**2,np.cos(x1)**2)
    has0=np.floor(x1/np.pi)>=np.ceil(x0/np.pi)          # cos^2=1 at multiples of pi
    hasz=np.floor((x1-np.pi/2)/np.pi)>=np.ceil((x0-np.pi/2)/np.pi)
    return np.where(hasz,0.0,lo), np.where(has0,1.0,hi)
PAD=1.05
def enclose(slo,shi):
    al=d0.copy(); be=d0.copy()
    for i in range(M):
        sl=slice(i*8,i*8+9)
        amp=AMP[:,sl]; th=TH[:,sl]
        # a-priori upper on delta range within segment
        bmax=be+shi[i]*amp.max(1)*PAD
        # w range over r samples and delta in [al,bmax]
        wl=np.full(len(ns),np.inf); wh=np.zeros(len(ns))
        for c in range(amp.shape[1]):
            lo,hi=cos2_range(al+th[:,c],bmax+th[:,c])
            wl=np.minimum(wl,amp[:,c]*lo); wh=np.maximum(wh,amp[:,c]*hi)
        al=al+slo[i]*wl/PAD; be=be+shi[i]*wh*PAD
    return al,be
def minsin2(lo,hi):
    m=np.ceil(lo/np.pi)*np.pi
    return np.where(m<=hi,0.0,np.minimum(np.sin(lo)**2,np.sin(hi)**2))
def bound(slo,shi):
    al,be=enclose(slo,shi); return 4/k*np.sum(g*minsin2(al,be))
S0l=np.zeros(M); S0h=np.full(M,CH*h)
heap=[(bound(S0l,S0h),0,S0l,S0h)]; cnt=1; t=time.time(); hist=[]
while cnt<budget:
    bnd,_,L,H=heapq.heappop(heap)
    j=int(np.argmax(H-L)); mid=0.5*(L[j]+H[j])
    for l,hh in [(L[j],mid),(mid,H[j])]:
        L2=L.copy();H2=H.copy();L2[j]=l;H2[j]=hh; cnt+=1
        heapq.heappush(heap,(max(bound(L2,H2),bnd),cnt,L2,H2))
    if cnt%2000<2: hist.append((cnt,heap[0][0]/bare)); print(cnt,round(heap[0][0]/bare,4),round(time.time()-t,1),flush=True)
print('M',M,'nodes',cnt,'LB',heap[0][0],'ratio',heap[0][0]/bare)
json.dump({'M':M,'nodes':cnt,'LB':heap[0][0],'ratio':heap[0][0]/bare,'hist':hist,'note':'prototype; sampled w-range with 5% pad, not yet validated numerics'},open(f'bnbs_M{M}.json','w'))
