import numpy as np, json
from scipy.integrate import quad
kc=np.pi/2; B=0.1; gmin=0.01*kc
kt=kc*(1+1j*B/2)
ymin=(kt*kt).imag+gmin*kt.real   # = 2 x y + gamma_min x
rng=np.random.default_rng(0)
w0=np.concatenate([rng.uniform(0,20*kc,200000),np.linspace(0,3*kc,20001)]); ga=np.concatenate([gmin*np.exp(rng.uniform(0,6,200000)),np.full(20001,gmin)])
chi=1/(w0**2-kt**2-1j*ga*kt)            # per unit oscillator strength
ratio=ymin*np.abs(chi)**2/chi.imag      # must be <= 1 (disk |chi|^2 <= Im chi / ymin)
print('y_min = %.5f (= %.4f kc^2); max ymin|chi|^2/Im chi over oscillators = %.8f; min Im chi = %.3e'%(ymin,ymin/kc**2,ratio.max(),chi.imag.min()))
# f-sum check: int_0^inf w Im eps dw = (pi/2) wp^2 for one oscillator
wp2,w00,g=1.3,2.0,0.05
f=lambda w: w*(wp2/(w00**2-w**2-1j*g*w)).imag
I=sum(quad(f,lo,hi,limit=500,epsrel=1e-10)[0] for lo,hi in [(0,1.5),(1.5,1.95),(1.95,2.05),(2.05,3),(3,50),(50,np.inf)])
print('f-sum: int w Im eps dw = %.6f vs (pi/2) wp^2 = %.6f'%(I,np.pi/2*wp2))
# budget implied inequality for the W=0.5 baseline design: (1/A) int ymin*|chi(kt)|^2/Im chi(kt) dA <= W kc^2
J=json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/lorentz_W0.5_L4_g0.01.json'))
r=np.array(J['radii']); A=np.pi*(r[1:]**2-r[:-1]**2); At=A.sum()
wp2=np.array(J['kp2_over_kc2'])*kc**2; w0=np.array(J['k0_over_kc'])*kc; g=J['gam_over_wc']*kc
chi=wp2/(w0**2-kt**2-1j*g*kt)
need=(A*ymin*np.abs(chi)**2/chi.imag).sum()/At
print('W=0.5 design: (1/A) int ymin|chi|^2/Im chi = %.4f kc^2  <=  budget used %.4f kc^2 ; chi(kt) per layer:'%(need/kc**2,(A*wp2).sum()/At/kc**2), np.round(chi,4))
print('Im xi per layer (xi=-1/chi):',np.round((-1/chi).imag,4))
