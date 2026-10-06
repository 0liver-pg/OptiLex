import sys, json, numpy as np
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
from fastcyl import coeffs_pec
kc=np.pi/2; B=0.1
d=json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/lossless_sector_B0.1_L8.json'))
designs={'bare':([],[1.0]), 'p2opt':(np.sqrt(d['eps']),d['radii'])}
def T(m,r,z,phis,N=None):
    b=coeffs_pec(m,r,z,N=N); NN=(len(b)-1)//2; n=np.arange(-NN,NN+1)
    return np.exp(1j*np.outer(phis,n))@b
bR=3.0
# (a) growth of compensated T along z = kc + i eta
print('(a) |T(phi;z) e^{2 i z b|sin(phi/2)|}| with b=3, z=kc+i*eta')
for name,(m,r) in designs.items():
    for phi in [np.pi/2,3*np.pi/4,np.pi]:
        row=[]
        for eta in [0,0.5,1,2,4]:
            z=kc+1j*eta; N=int(abs(z)*3*2.5+25)
            v=T(m,r,z,np.array([phi]),N=N)[0]*np.exp(2j*z*bR*abs(np.sin(phi/2)))
            row.append(abs(v))
        print(name,'phi=%.3f'%phi,' '.join('%.3e'%x for x in row))
# (b) Szego-Pick inequality: int_R |w G_j|^2 dk >= v^H K^{-1} v
m_=6; D=0.8*kc*B/2
zl=kc+D*np.exp(1j*np.pi*(2*np.arange(2*m_)+1)/(2*m_)); zl=zl[zl.imag<0]
w=lambda z: D**m_/np.prod(z[...,None]-zl,axis=-1)
xx=np.linspace(-3,3,7); assert np.allclose(abs(w(kc+xx*D))**2,1/(1+xx**(2*m_)))
Delta=np.pi/2; phis=np.linspace(np.pi-Delta,np.pi+Delta,401); wq=np.full(phis.size,phis[1]-phis[0]); wq[[0,-1]]/=2
J=3
basis=[np.exp(1j*j*(phis-np.pi))/np.sqrt(2*Delta) for j in range(-(J//2),J//2+1)]  # orthonormal on Theta
def G(m,r,z):
    t=T(m,r,z,phis,N=int(abs(z)*3*2.5+25))*np.exp(2j*z*bR*abs(np.sin(phis/2)))
    return np.array([np.sum(wq*np.conj(bj)*t) for bj in basis])
zs=kc+np.array([-0.04,-0.02,0,0.02,0.04])+1j*0.02
Kmat=1j/(2*np.pi*(zs[:,None]-np.conj(zs)[None,:]))
for name,(m,r) in designs.items():
    V=np.array([w(np.array(z))*G(m,r,z) for z in zs])  # K x J
    lb=sum(np.real(np.conj(V[:,j])@np.linalg.solve(Kmat,V[:,j])) for j in range(V.shape[1]))
    ks=np.linspace(kc-1.2,kc+1.2,24001); f2=np.array([np.sum(abs(G(m,r,k))**2) for k in ks])*abs(w(ks))**2
    full=np.trapz(f2,ks)
    # sector bound side: sum|G_j|^2 <= (pi k/2) sigma_Theta
    print('(b)',name,'v^H K^-1 v = %.5e  int|f|^2 = %.5e  ratio %.3f'%(lb,full,lb/full))
print('cond K = %.2e'%np.linalg.cond(Kmat))
