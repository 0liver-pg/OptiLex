import sys, numpy as np, json
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
from scipy.integrate import quad
kc=np.pi/2; B=0.1; rho=kc*B/2
def load(f):
    J=json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/'+f)); return np.sqrt(np.array(J['eps'],complex)), J['radii']
designs={'bare':(np.array([],complex),[1.0]),'p1_L8':load('de_ext_B0.1_L8.json'),'sector_L8':load('lossless_sector_B0.1_L8.json')}
b=3.0
def G(k,m,r,phi=np.pi):
    n,bn=fastcyl.coeffs_pec(m,r,k,'TM',N=40); return np.sum(bn*np.exp(1j*n*phi))*np.exp(2j*k*b*abs(np.sin(phi/2)))
out={}
for t in [0.25,0.5]:
    w0=1j*t; z0=kc+rho*w0; zeta0=((1+w0)/(1-w0))**2
    P=lambda ze: (zeta0.imag/np.pi)/abs(ze-zeta0)**2
    dia=lambda s: P(((1+s)/(1-s))**2)*4*(1+s)/(1-s)**3
    arc=lambda th: P(-1/np.tan(th/2)**2)*(1/np.tan(th/2))/np.sin(th/2)**2
    wb=quad(dia,-1,1,limit=200)[0]; wa=quad(arc,0,np.pi,limit=200)[0]
    for name,(m,r) in designs.items():
        lhs=np.log(abs(G(z0,m,r)))
        rb=quad(lambda s: dia(s)*np.log(abs(G(kc+rho*s,m,r))),-1,1,limit=400)[0]
        ra=quad(lambda th: arc(th)*np.log(abs(G(kc+rho*np.exp(1j*th),m,r))),0,np.pi,limit=400)[0]
        out[f'{name}_t{t}']=dict(omega_band=wb,omega_arc=wa,lnG_z0=lhs,rhs=rb+ra,slack=rb+ra-lhs)
print(json.dumps(out,indent=0))
