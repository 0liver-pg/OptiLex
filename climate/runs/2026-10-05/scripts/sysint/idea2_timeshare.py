"""Idea 2: one capture plant time-shared between a cycling gas plant and a baseload industrial
flue gas; reboiler heat in gas-off hours from an electric boiler / heat pump on cheap power.
Calibrated to NETL Rev 4A F-class NGCC: $61/t captured at 85% CF (2018$), fixed share 50-70%."""
import numpy as np
from common import *

rng = np.random.default_rng(1)
H = 8760
# Synthetic hourly gas-plant dispatch: runs in the highest-price hours. Price model: daily+seasonal
# shape + noise, calibrated so the plant runs ~f_on of hours. Off-hours = cheap hours.
t = np.arange(H)
price = 70 + 25*np.sin(2*np.pi*(t % 24 - 6)/24) + 15*np.cos(2*np.pi*t/H) + rng.normal(0, 22, H)
price = np.clip(price, -10, None)

R_cap = 2.0e6 / H        # t/h stripper capacity (2 Mt/yr at 100% CF, NZT-class)
def run(f_on, fixed_share, ind_rate_frac, p_ngcc_steam=None):
    thr = np.quantile(price, 1 - f_on)
    on = price >= thr
    v = 61 * (1 - fixed_share)                # $/t variable at NETL point (incl. steam penalty)
    F = 61 * fixed_share * 0.85               # $/yr per (t/yr nameplate)
    fixed_annual = F * R_cap * H
    ngcc_t = R_cap * on.sum()
    ind_rate = ind_rate_frac * R_cap          # industrial CO2 arriving t/h, continuous
    ind_t_shared = min(ind_rate, R_cap) * (~on).sum()   # captured only in gas-off hours
    # extra fixed costs for sharing: duct + pretreatment (DCC/FGD) + 300 MWth e-boiler/HP:
    extra_fixed = 0.20 * fixed_annual
    # off-hour reboiler energy: 2.7 GJ/t heat by e-boiler (99%) at the off-hour price
    off_price = price[~on].mean()
    on_price = price[on].mean()
    eboiler = 2.7 / 0.99 / 3.6 * off_price          # $/t
    v_ind = v - 0.45*v + eboiler                    # replace NGCC steam-penalty part (~45% of v) with e-boiler
    shared_cost = (fixed_annual + extra_fixed + v*ngcc_t + v_ind*ind_t_shared) / (ngcc_t + ind_t_shared)
    ngcc_alone = fixed_annual/ngcc_t + v
    # industrial stand-alone plant sized for its own rate, 90% CF, scale exponent 0.6, 25% smaller
    # absorber per tonne for 10-15% CO2 flue (assumption)
    ind_fixed = F * (ind_rate*H) * (ind_rate/R_cap)**(-0.4) * 0.75
    ind_alone_t = ind_rate * H * 0.90
    ind_alone = ind_fixed/ind_alone_t + v
    sep_total = (fixed_annual + v*ngcc_t + ind_fixed + v*ind_alone_t) / (ngcc_t + ind_alone_t)
    return dict(f_on=f_on, cf_plant=(ngcc_t+ind_t_shared)/(R_cap*H), ngcc_alone=ngcc_alone,
                ind_alone=ind_alone, shared=shared_cost, sep_total=sep_total, ind_share_captured=(~on).mean()*0.9,
                off_price=off_price, on_price=on_price, eboiler=eboiler,
                marginal_ind=(extra_fixed + v_ind*ind_t_shared)/ind_t_shared)

print("f_on fixed  indRate  plantCF  NGCCalone  INDalone  sharedAvg  separateAvg  marginal$/t_ind  indCapt%  offP onP")
for f_on in (0.3, 0.45, 0.6):
    for fs in (0.5, 0.7):
        for ir in (0.5, 1.0):
            r = run(f_on, fs, ir)
            print(f"{f_on:.2f} {fs:.1f}   {ir:.1f}     {r['cf_plant']:.2f}    {r['ngcc_alone']:6.0f}    {r['ind_alone']:6.0f}"
                  f"    {r['shared']:6.0f}     {r['sep_total']:6.0f}        {r['marginal_ind']:5.0f}         "
                  f"{r['ind_share_captured']*100:4.0f}   {r['off_price']:.0f} {r['on_price']:.0f}")

print("\nVerifier check of the rejected variant (run idle absorber on ambient air = DAC mode):")
for dp in (2000, 5000):
    print(f"  fan work at {dp} Pa, 75% capture of 420 ppm: {fan_work_gj_per_tonne(420e-6, 0.75, dp):.1f} GJ/t "
          f"(vs separation floor {gj_per_tonne(min_separation_work(420e-6,0.75)):.2f})")
print("Floors: NGCC 4% flue", round(gj_per_tonne(min_separation_work(0.04,0.9)),3),
      "GJ/t; refinery/industrial 12%", round(gj_per_tonne(min_separation_work(0.12,0.9)),3), "GJ/t")
print("e-boiler 2.7 GJ_th/t = ", round(2.7/0.99/3.6*1000), "kWh/t; heat pump COP 2.5 =", round(2.7/2.5/3.6*1000), "kWh/t")
