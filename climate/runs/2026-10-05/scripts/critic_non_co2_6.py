# Critic checks for non_co2_6: marginal (post-capex) economics vs venting, and input-side mass balance
M={'CHCl3':119.38,'CHClF2':86.47,'HF':20.006,'HCl':36.46,'CHF3':70.01,'CH4':16.04,'VDF':64.03}
# input-side anchors per t HCFC-22 (CHCl3 + 2HF -> CHClF2 + 2HCl)
print('CHCl3 t per t HCFC-22: %.3f'%(M['CHCl3']/M['CHClF2']))
print('HF t per t HCFC-22: %.3f'%(2*M['HF']/M['CHClF2']))
print('HCl co-product t per t HCFC-22: %.3f'%(2*M['HCl']/M['CHClF2']))
# marginal operating margin per t HFC-23 once the unit is built (capex sunk)
for name,sel,pvdf,hf,disp,egj,eprice,ch4ratio,ch4p in [('low',0.7,6000,2000,200,4.83,5,1,4),('base',0.5,3500,1500,500,7.73,8,2,8),('high',0.3,2000,1000,1500,16.33,15,4,12)]:
    vdf=sel*M['VDF']/M['CHF3']*pvdf
    hfc=sel*M['HF']/M['CHF3']*hf
    ch4=ch4ratio*M['CH4']/M['CHF3']*50*ch4p*0.3  # ~50 GJ/t CH4, assume 30% of excess CH4 not recovered as fuel
    e=egj*eprice
    margin=vdf+hfc-disp-e-ch4
    print(f'{name}: marginal margin ${margin:,.0f}/t HFC-23 = ${margin/14600:.3f}/t CO2e; per t HCFC-22 at 2%: ${margin*0.02:,.1f}')
# what a venting operator forgoes vs penalty scale: a CNY 1e6 fine cap equivalent
print('Max fine-like penalty needed to dominate base margin per kt HFC-23 vented: n/a (margin is revenue, venting cost 0)')
