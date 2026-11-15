"""Write the simulation results as {rows, meta} JSON for the dashboard."""
import json, math, pandas as pd
from pathlib import Path
here=Path(__file__).resolve().parent
code=[{"label":n,"value":(here/n).read_text(),"type":"code","lang":"python"} for n in ("bt.py","sim.py","post.py","make_json.py")]
R=pd.read_csv(here/'sim_years.csv'); R=R[R.year>=2003]
def clean(v):
    if isinstance(v,float) and math.isnan(v): return None
    return v
S=json.load(open(here/'sim.json'))
stats=[{k:clean(v) for k,v in r.items()} for r in S['stats']]
ws={k:clean(v) for k,v in S['wigstats'].items()}; ws.update(strat='WIG',cost=0.0)
stats.append(ws)
for r in stats:
    for k in ('mean','median','q10','q90','worst','best','beatWIG','loss','p20','p40','p60'):
        if r.get(k) is not None: r[k]=round(r[k],4)
    for k in ('trades','fees'):
        if r.get(k) is not None: r[k]=round(r[k],1)
    r['n']=int(r['n'])
t=R[R.cost==0.0039].pivot_table(index='year',columns='strat',values='ret')
t['wig']=R.groupby('year').wig.first()
years=[{"year":int(y),"spokojna":round(r.spokojna,4),"podium":round(r.podium,4),"mix":round(r['mix 50/50'],4),"wig":round(r.wig,4)} for y,r in t.iterrows()]
common=[{"label":"Dane","value":"Baza marketdata (daily_price, źródło EODHD), 930 spółek z GPW w tym 351 wycofanych, do 26.10.2026"},
        {"label":"Okno","value":"pierwsza sesja od 16.11 do ostatniej sesji przed 12.03 następnego roku, lata 2003-2025"}]
json.dump({"rows":years,"meta":common+[{"label":"Prowizja","value":"0,39% od każdej transakcji"}]+code},open(here/'sigg_years.json','w'),ensure_ascii=False)
json.dump({"rows":stats,"meta":common+[{"label":"Prowizja","value":"0; 0,2; 0,39; 0,6% od każdej transakcji (kolumna cost)"}]+code},open(here/'sigg_stats.json','w'),ensure_ascii=False)
print(len(years),len(stats)); print(stats[-1]); print(years[0])
