import sys, numpy as np, json
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
from scipy.integrate import quad
J=json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.1_L8.json'))
eps=np.array(J['eps']); radii=J['radii']; m=np.sqrt(eps.astype(complex)); b=radii[-1]
def T(phi,k,mm=m,rr=radii,N=None):
    n,bn=fastcyl.coeffs_pec(mm,rr,k,"TM",N=N or (fastcyl.nmax_like_cloak2d(mm,rr[-1],abs(k))+int(3*abs(k.imag if np.iscomplexobj(k) else 0)*rr[-1])+10)); return np.sum(bn*np.exp(1j*n*phi))
x=np.pi/2
print('growth along k = x + i y, backscatter phi=pi: |T|, |T e^{2ikb}|, |T e^{2ika}|')
for y in [0,0.25,0.5,1,1.5,2,3]:
    k=x+1j*y; t=T(np.pi,k)
    print(y, abs(t), abs(t*np.exp(2j*k*b)), abs(t*np.exp(2j*k*radii[0])))
print('bare PEC (radius a=1): |T e^{2ika}|')
for y in [0,1,2,3]:
    k=x+1j*y; t=T(np.pi,k,np.array([],complex),[1.0]); print(y,abs(t),abs(t*np.exp(2j*k*1.0)))
# Poisson sub-mean check for G(k)=T(pi,k)e^{2ikb}: |G(z0)|^2 <= int P_z0 |G|^2 over real line (even ext.)
z0=x+1j*0.3
G=lambda k: T(np.pi,k)*np.exp(2j*k*b)
P=lambda k: (z0.imag/np.pi)/((k-z0.real)**2+z0.imag**2)
f=lambda k: P(k)*abs(G(k))**2 + P(-k)*abs(G(k))**2
I=sum(quad(f,lo,hi,limit=400,epsrel=1e-7)[0] for lo,hi in [(1e-6,0.5),(0.5,1),(1,1.5),(1.5,2),(2,3),(3,6),(6,12),(12,20)])
print('|G(z0)|^2 =',abs(G(z0))**2,' Poisson avg of |G|^2 (k<60) =',I)
