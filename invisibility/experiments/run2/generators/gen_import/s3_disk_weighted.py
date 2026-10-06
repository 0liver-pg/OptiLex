# Check the passivity-weighted locus h = k~ chi / wp^2 also lies in one disk tangent at 0 (diameter |k~|/y_min)
import numpy as np
kc=np.pi/2; gmin=0.01*kc
for B in [0.1,0.03]:
    kt=kc*(1+1j*B/2); ymin=(kt*kt).imag+gmin*kt.real
    rng=np.random.default_rng(1)
    w0=np.concatenate([rng.uniform(0,20*kc,300000),np.linspace(0,3*kc,30001)]); ga=np.concatenate([gmin*np.exp(rng.uniform(0,7,300000)),np.full(30001,gmin)])
    h=kt/(w0**2-kt**2-1j*ga*kt)
    # line D/kt = t/kt - kt - i g ; inversion -> circle through 0; center c0 = i*conj(nhat)/(2 d) type; fit numerically: diameter = max|h|
    j=np.argmax(np.abs(h)); c=h[j]/2; R=abs(c)
    print('B=%.2f: max|h| = %.5f vs |k~|/y_min = %.5f ; max(|h-c|/R) over samples = %.8f'%(B,abs(h[j]),abs(kt)/ymin,(np.abs(h-c)/R).max()))
