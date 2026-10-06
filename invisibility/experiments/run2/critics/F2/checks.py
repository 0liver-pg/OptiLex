import numpy as np, json
from scipy.special import jv, hankel1
from numpy.polynomial.legendre import leggauss
def chan(k,b,m,nq=160):
    x,w=leggauss(nq); r=1+(b-1)*(x+1)/2; w=w*(b-1)/2; s=np.sqrt(2*np.pi*r*w)
    am=abs(m); c=jv(am,k)/hankel1(am,k); psi=jv(am,k*r)-c*hankel1(am,k*r)
    R1,R2=np.meshgrid(r,r,indexing='ij'); rl=np.minimum(R1,R2); rg=np.maximum(R1,R2)
    G=0.25j*(jv(am,k*rl)-c*hankel1(am,k*rl))*hankel1(am,k*rg); K=k**2*s[:,None]*G*s[None,:]
    return (K+K.conj().T)/2,(K-K.conj().T)/2j,(1j)**m*psi*s,(1j*k**2/4)*(1j)**(-m)*psi*s,-c
out={}
# 1) per-harmonic top eigenvalue of Herm(k^2 G_n) at canonical size, vs Schur bounds
k,b=np.pi/2,3.0
rows=[]
for n in [0,1,2,4,6,7,8,9,10,11,12,15,20,25,30]:
    H,A,_,_,_=chan(k,b,n); lm=np.linalg.eigvalsh(H).max(); la=np.linalg.eigvalsh(A).max()
    rows.append(dict(n=n,lam_max_HermK=lm,lam_max_A=la,chi5_times=5*lm,
        schur_stated=k**2*(b**2-1)/(2*max(n,1)),schur_quarter=k**2*(b**2-1)/(4*max(n,1)),static_b2_over_n2=k**2*b**2/max(n,1)**2))
out['tail']=rows
# 2) rotated Layer-1 sigma_ext floor at canonical size, eps_max 1.5 and 2 (prototype point)
def rot(k,b,em,ts=(0,0.1,0.25,0.5,1,2,4,8,16,32),mmax=25):
    P=[chan(k,b,m,120) for m in range(-mmax,mmax+1)]; chi=em-1; Tb=sum(p[4] for p in P); sb=-(4/k)*np.real(Tb); best=-np.inf;bt=None
    for t in ts:
        th=np.arctan(t); lin=qg=qe=0; ok=True
        for H,A,e,g,_ in P:
            Q=np.eye(len(e))/chi-(H-t*A)
            if np.linalg.eigvalsh(Q).min()<=0: ok=False;break
            et=e*np.exp(1j*th)/np.cos(th); Qi=np.linalg.inv(Q); gc=np.conj(g)
            lin+=np.real(g@(Qi@et/2)); qg+=np.real(np.conj(gc)@Qi@gc); qe+=np.real(np.conj(et)@Qi@et)
        if not ok: continue
        lb=-(4/k)*(np.real(Tb)+lin+np.sqrt(qg*qe)/2)
        if lb>best: best,bt=lb,t
    return dict(bare=sb,lb=best,ratio=best/sb,tan=bt)
out['layer1_canon_eps1.5']=rot(np.pi/2,3.0,1.5)
out['layer1_canon_eps1.25']=rot(np.pi/2,3.0,1.25)
print(json.dumps(out,indent=1,default=float))
json.dump(out,open('checks.json','w'),indent=1,default=float)
