import math, json, csv
A = dict(  # assumptions
 hh_size=3.8, grocery_share=0.14, org_base=0.10, org_slope=0.002, org_cap=0.40,
 qc_weight=1.5, acc_norm=7.0, entry_res=0.12, entry_transit=0.02, conversion=0.75,
 basket_base=350, basket_slope=2.5, blend_w=0.5, store_sqft=10000, gm=0.21,
 staff=1.10e7, other_opex_pct=0.05, fixed_opex=6.0e6, fitout_psf=2200, deposit_months=6, inventory=8.0e6,
 rent_esc=0.05, cost_inf=0.06, cannib_max=0.35, cannib_radius=8.0, ramp=[0.70,0.90,1,1,1,1,1,1,1], wacc=0.12,
 budget=8.0e7, max_payback=4.0, min_pair_km=5.0, days=365)
W = dict(demand=0.20, profit=0.30, competition=0.10, rent=0.10, access=0.10, cannib=0.15, growth=0.05)
existing = [ # name, lat, lon, pop1.5km, income, footfall, res_share, comps, rent, access, growth, actual_sales(Cr)
 ["Koramangala",12.9352,77.6245,110000,115000,19000,0.55,6,165,8,0.020,31.5],
 ["Indiranagar",12.9784,77.6408,95000,130000,21000,0.45,6,180,9,0.015,30.2],
 ["Jayanagar",12.9250,77.5938,120000,95000,17000,0.70,5,140,8,0.010,29.8],
 ["Malleshwaram",13.0035,77.5709,100000,90000,15000,0.70,4,130,7,0.010,26.1],
 ["HSR Layout",12.9116,77.6474,105000,110000,16000,0.65,5,120,6,0.030,28.4],
 ["Rajajinagar",12.9915,77.5545,115000,80000,14000,0.75,4,110,7,0.010,24.0]]
cands = [
 ["Whitefield",12.9698,77.7500,105000,125000,24000,0.35,7,145,8,0.045],
 ["Marathahalli",12.9569,77.7011,105000,95000,32000,0.25,7,150,6,0.035],
 ["Bellandur",12.9260,77.6762,110000,135000,16000,0.55,5,130,4,0.050],
 ["Sarjapur Road",12.9070,77.6990,95000,120000,12000,0.70,3,95,5,0.070],
 ["Hebbal",13.0358,77.5970,100000,105000,15000,0.60,4,120,7,0.040],
 ["Electronic City",12.8452,77.6602,90000,95000,20000,0.40,4,75,7,0.050],
 ["Kanakapura Road",12.8856,77.5640,105000,85000,13000,0.80,2,65,8,0.055],
 ["Yelahanka",13.1007,77.5963,85000,80000,11000,0.75,2,70,6,0.045]]
def hav(a,b,c,d):
    R=6371; p1,p2=math.radians(a),math.radians(c); dp=p2-p1; dl=math.radians(d-b)
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
def demand(pop,inc,ff,res,comp,acc):
    hh=pop/A['hh_size']; wallet=inc*A['grocery_share']
    org=min(A['org_cap'],A['org_base']+A['org_slope']*inc/1000)
    af=acc/A['acc_norm']; share=af/(af+comp+A['qc_weight'])
    salesA=hh*wallet*org*share*12
    basket=A['basket_base']+A['basket_slope']*inc/1000
    bills=(ff*res*A['entry_res']+ff*(1-res)*A['entry_transit'])*A['conversion']
    salesB=bills*basket*A['days']
    return salesA,salesB,share,bills,basket
# calibration
rows=[];pa=0;ac=0
for e in existing:
    sA,sB,*_=demand(*e[3:8],e[9]); pred=A['blend_w']*sA+(1-A['blend_w'])*sB
    rows.append((e[0],sA/1e7,sB/1e7,pred/1e7,e[11])); pa+=pred; ac+=e[11]*1e7
calib=ac/pa
mape=sum(abs(r[3]*calib-r[4])/r[4] for r in rows)/len(rows)
print("calib",round(calib,3),"MAPE",round(mape,3))
for r in rows: print(r[0],[round(x,1) for x in r[1:]], round(r[3]*calib,1))
out=[]
for c in cands:
    n,la,lo,pop,inc,ff,res,comp,rent,acc,g=c
    sA,sB,share,bills,basket=demand(pop,inc,ff,res,comp,acc)
    gross=(A['blend_w']*sA+(1-A['blend_w'])*sB)*calib
    dists={e[0]:hav(la,lo,e[1],e[2]) for e in existing}
    near=min(dists,key=dists.get); d=dists[near]
    can=max(0,A['cannib_max']*(1-d/A['cannib_radius']))
    rent_y=rent*A['store_sqft']*12
    store_ebitda=gross*A['gm']-rent_y-A['staff']-A['fixed_opex']-gross*A['other_opex_pct']
    lost=gross*can*(A['gm']-A['other_opex_pct'])
    inc_ebitda=store_ebitda-lost
    capex=A['fitout_psf']*A['store_sqft']+A['deposit_months']*rent*A['store_sqft']+A['inventory']
    cfs=[]
    for y,r in enumerate(A['ramp']):
        s=gross*r*(1+g)**y
        cf=s*A['gm']-rent_y*((1+A['rent_esc'])**y)-(A['staff']+A['fixed_opex'])*((1+A['cost_inf'])**y)-s*A['other_opex_pct']-s*can*(A['gm']-A['other_opex_pct'])
        cfs.append(cf)
    npv=-capex+sum(cf/(1+A['wacc'])**(i+1) for i,cf in enumerate(cfs))
    payback=capex/inc_ebitda if inc_ebitda>0 else 99
    out.append(dict(name=n,lat=la,lon=lo,pop=pop,income=inc,footfall=ff,res=res,comp=comp,rent=rent,access=acc,growth=g,
      salesA=sA/1e7,salesB=sB/1e7,diverg=abs(sA-sB)/max(sA,sB),gross=gross/1e7,spsf=gross/A['store_sqft'],nearest=near,dist=d,cannib=can,
      net=gross*(1-can)/1e7,rentpct=rent_y/gross,ebitda=store_ebitda/1e7,inc_ebitda=inc_ebitda/1e7,capex=capex/1e7,payback=payback,npv=npv/1e7))
for o in out:
    print(f"{o['name']:16} A{o['salesA']:5.1f} B{o['salesB']:5.1f} G{o['gross']:5.1f} ff{o['footfall']:6} near {o['nearest'][:6]} {o['dist']:4.1f}km c{o['cannib']:.2f} rent%{o['rentpct']:.3f} E{o['ebitda']:5.2f} iE{o['inc_ebitda']:5.2f} cap{o['capex']:4.2f} pb{o['payback']:4.1f} npv{o['npv']:5.2f}")
json.dump(dict(A=A,W=W,existing=existing,cands=cands,calib=calib,mape=mape,out=out),open('model_out.json','w'),indent=1)

# ---- scoring ----
crit={'demand':('gross',1),'profit':('npv',1),'competition':('comp',-1),'rent':('rentpct',-1),'access':('access',1),'cannib':('cannib',-1),'growth':('growth',1)}
for k,(f,sgn) in crit.items():
    v=[o[f] for o in out]; lo,hi=min(v),max(v)
    for o in out:
        x=(o[f]-lo)/(hi-lo) if hi>lo else 1
        o['s_'+k]=100*(x if sgn>0 else 1-x)
for o in out:
    o['score']=sum(W[k]*o['s_'+k] for k in crit)
    o['gate']= o['payback']<=A['max_payback'] and o['npv']>0
rank=sorted(out,key=lambda o:(-o['gate'],-o['score']))
picks=[];spent=0
for o in rank:
    if not o['gate']: continue
    if spent+o['capex']*1e7>A['budget']: continue
    if any(hav(o['lat'],o['lon'],p['lat'],p['lon'])<A['min_pair_km'] for p in picks): continue
    picks.append(o); spent+=o['capex']*1e7
print()
for i,o in enumerate(rank,1):
    print(i,f"{o['name']:16} score {o['score']:5.1f} gate {o['gate']} npv {o['npv']:5.2f} pb {o['payback']:4.1f}", {k:round(o['s_'+k]) for k in crit})
print("PICKS",[p['name'] for p in picks],round(spent/1e7,2))
json.dump(dict(A=A,W=W,existing=existing,cands=cands,calib=calib,mape=mape,out=out,picks=[p['name'] for p in picks]),open('model_out.json','w'),indent=1)
with open('data/existing_stores.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['store','lat','lon','pop_1_5km','median_hh_income_inr_month','daily_footfall','resident_share','organised_competitors_2km','rent_inr_sqft_month','accessibility_1_10','catchment_growth_pa','actual_annual_sales_cr'])
    w.writerows(existing)
with open('data/candidate_locations.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['location','lat','lon','pop_1_5km','median_hh_income_inr_month','daily_footfall','resident_share','organised_competitors_2km','rent_inr_sqft_month','accessibility_1_10','catchment_growth_pa'])
    w.writerows(cands)
with open('data/model_results.csv','w',newline='') as f:
    keys=['name','gross','nearest','dist','cannib','net','rentpct','ebitda','inc_ebitda','capex','payback','npv','score','gate']
    w=csv.writer(f); w.writerow(keys)
    for o in rank: w.writerow([round(o[k],3) if isinstance(o[k],float) else o[k] for k in keys])
