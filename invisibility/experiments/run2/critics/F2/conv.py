import numpy as np, json
from scipy.special import jv, hankel1
from numpy.polynomial.legendre import leggauss
def chan(k,b,m,nq):
    x,w=leggauss(nq); r=1+(b-1)*(x+1)/2; w=w*(b-1)/2; s=np.sqrt(2*np.pi*r*w)
    am=abs(m); c=jv(am,k)/hankel1(am,k); psi=jv(am,k*r)-c*hankel1(am,k*r)
    R1,R2=np.meshgrid(r,r,indexing='ij'); rl=np.minimum(R1,R2); rg=np.maximum(R1,R2)
    G=0.25j*(jv(am,k*rl)-c*hankel1(am,k*rl))*hankel1(am,k*rg); K=k**2*s[:,None]*G*s[None,:]
    return (K+K.conj().T)/2,(K-K.conj().T)/2j,(1j)**m*psi*s,(1j*k**2/4)*(1j)**(-m)*psi*s,-c
def lb(k,b,em,t,nq,mmax=25):
    chi=em-1; th=np.arctan(t); Tb=0; lin=qg=qe=0
    for m in range(-mmax,mmax+1):
        H,A,e,g,tb=chan(k,b,m,nq); Tb+=tb
        Q=np.eye(nq)/chi-(H-t*A); assert np.linalg.eigvalsh(Q).min()>0
        et=e*np.exp(1j*th)/np.cos(th); Qi=np.linalg.inv(Q); gc=np.conj(g)
        lin+=np.real(g@(Qi@et/2)); qg+=np.real(np.conj(gc)@Qi@gc); qe+=np.real(np.conj(et)@Qi@et)
    sb=-(4/k)*np.real(Tb); return (-(4/k)*(np.real(Tb)+lin+np.sqrt(qg*qe)/2))/sb
res={}
for nq in (30,60,120,240):
    res[nq]=dict(p1=lb(np.pi/2,1.5,2,0.25,nq), p2=lb(0.5,1.5,6,0.25,nq))
    print(nq,res[nq],flush=True)
json.dump(res,open('conv.json','w'),indent=1)
