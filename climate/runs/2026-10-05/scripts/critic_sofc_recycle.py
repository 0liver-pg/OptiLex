# Critic check: ASU-free anode loop = WGS shift -> dry -> compress -> chill -> flash liquid CO2,
# recycle non-condensables (H2, N2, CO2 vapour) to anode, purge to bleed feed N2.
# Basis: 1 mol CH4-equivalent feed (1 C, 4 H2-eq), f mol N2. Ideal flash: y_CO2 = Psat/P. ASSUMED simplifications.
import math
def psat_co2(TC):  # Antoine-like fit for CO2 vapour pressure (bar), ~-56..31 C (ASSUMED fit)
    T=TC+273.15; Tc=304.13; Pc=73.77
    tau=1-T/Tc
    return Pc*math.exp(Tc/T*(-7.0602*tau+1.9391*tau**1.5-1.6463*tau**2-3.2995*tau**4))
for TC,P in [(-50,30),(-50,60),(-30,60)]:
    y=psat_co2(TC)/P
    print(f"\nFlash {TC} C, {P} bar: Psat={psat_co2(TC):.1f} bar, y_CO2 vap={y:.3f}")
    for f in [0.01,0.03,0.06]:
        best=None
        for s in [0.02,0.05,0.1,0.2,0.4,1.0]:
            U=0.80
            R=0.0
            for _ in range(500):
                R=(1-s)*(1-U)*(4+R)
            H2out=(1-U)*(4+R)
            N=f/s
            CO2v=y/(1-y)*(H2out+N)
            co2_slip=s*CO2v          # per mol C fed (purge burned, vented)
            fuel_loss=s*H2out/4      # fraction of fuel lost in purge (heat only)
            anodeN2=N/(4+R+N)        # N2 dilution at anode inlet (rough)
            print(f"  N2feed={f:.2f} purge s={s:.2f}: capture={1-co2_slip:.3f} fuel lost={fuel_loss:.3f} anode-inlet N2 frac~{anodeN2:.2f}")
