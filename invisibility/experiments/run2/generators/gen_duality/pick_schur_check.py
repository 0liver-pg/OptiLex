# Check: per-pixel Pick-Schur LMI for causal passive Lorentz media (h(z)=z*chi(z) Herglotz, Nevanlinna mass s=sum wp^2)
import numpy as np
rng=np.random.default_rng(0)
worst_aug=np.inf; worst_pick=np.inf
for trial in range(20000):
    K=rng.integers(1,6)
    z=rng.uniform(0.7,1.3,K)*np.pi/2 + 1j*rng.uniform(1e-3,0.3,K)*np.pi/2
    J=rng.integers(1,4)
    w0=rng.uniform(0.05,20,J); g=rng.uniform(1e-3,1,J); s=rng.uniform(0,3,J)
    chi=np.array([np.sum(s/(w0**2-zz**2-1j*g*zz)) for zz in z])
    E=rng.normal(size=K)+1j*rng.normal(size=K); P=chi*E
    # lifted Schur form: M_ij*Y_ij = (z_i P_i conj(E_j) - conj(z_j) E_i conj(P_j))/(z_i-conj z_j)
    MY=np.array([[ (z[i]*P[i]*np.conj(E[j]) - np.conj(z[j])*E[i]*np.conj(P[j]))/(z[i]-np.conj(z[j])) for j in range(K)] for i in range(K)])
    worst_pick=min(worst_pick, np.linalg.eigvalsh((MY+MY.conj().T)/2).min()/max(1,np.abs(MY).max()))
    S=s.sum()
    v=z*P
    A=np.block([[np.array([[S]]), v.conj()[None,:]],[v[:,None], MY]])
    # note Hermitian layout: A_{0j}=z_j P_j, A_{i0}=conj
    A=(A+A.conj().T)/2
    worst_aug=min(worst_aug, np.linalg.eigvalsh(A).min()/max(1,np.abs(A).max()))
print('min normalized eig, Pick-Schur:',worst_pick,' augmented (mass s):',worst_aug)
# non-dispersive real chi: Pick with linear term b z -> also PSD; check
z=np.pi/2*(1+np.array([0.05j,0.02j-0.03,0.04+0.01j])); chi=4.0; E=rng.normal(size=3)+1j*rng.normal(size=3); P=chi*E
MY=np.array([[ (z[i]*P[i]*np.conj(E[j]) - np.conj(z[j])*E[i]*np.conj(P[j]))/(z[i]-np.conj(z[j])) for j in range(3)] for i in range(3)])
print('nondispersive Pick-Schur eigs:',np.linalg.eigvalsh((MY+MY.conj().T)/2))
# K=1 reduction: Im(z P conj E)/Im z
# tightness: single oscillator at minimum mass -> augmented LMI should be singular (rank deficient) 
z=np.pi/2*np.array([1+0.05j,0.97+0.01j,1.04+0.02j]); s=0.7; chi=s/(2.0**2-z**2-1j*0.01*z)
E=np.ones(3,complex); P=chi*E; v=z*P
MY=np.array([[ (z[i]*P[i]*np.conj(E[j]) - np.conj(z[j])*E[i]*np.conj(P[j]))/(z[i]-np.conj(z[j])) for j in range(3)] for i in range(3)])
for S in [0.7,0.69,0.6]:
    A=np.block([[np.array([[S]]), v.conj()[None,:]],[v[:,None], MY]]); print('mass',S,'min eig',np.linalg.eigvalsh((A+A.conj().T)/2).min())
# K=1 reduction check: augmented 2x2 <=> |z chi|^2 <= s Im(z chi)/Im z
