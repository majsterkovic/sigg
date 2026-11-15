"""ATH-DMA (gieldowo rules) in SIGG windows, plus turnover-threshold check of the two strategies.
Rules: entry = close at 504-session max and 50-session pre-range <= 18%; stop close < DMA150,
ratchet DMA100 at +50%, DMA50 at +100%; trade next open. Slot = portfolio value / N."""
src=open('sim.py').read().split('years=list')[0]
exec(src)
Pv=P.values; Pf=P.ffill().values; Ov=Oadj.values; n,m=Pv.shape
hi=P.rolling(504,min_periods=504).max().values
pre=P.shift(1).rolling(50,min_periods=50)
rng=((pre.max()-pre.min())/pre.min()).values
d150=P.rolling(150,min_periods=150).mean().values
d100=P.rolling(100,min_periods=100).mean().values
d50=P.rolling(50,min_periods=50).mean().values
okto={}
def uni(i,min_to):
    k=(i,min_to)
    if k not in okto: okto[k]=universe(dates[i],min_to).values
    return okto[k]
def entry_sig(i,min_to):
    return (Pv[i]>=hi[i])&(rng[i]<=0.18)&uni(i,min_to)
# virtual per-ticker state (unconstrained), per turnover threshold
def virtual(min_to):
    inpos=np.zeros(m,bool); ep=np.full(m,np.nan); tier=np.zeros(m,int); edate=np.full(m,-1)
    ev_in=np.zeros((n,m),bool); ev_out=np.zeros((n,m),bool); state=np.zeros((n,m),bool); ED=np.zeros((n,m),int)
    for i in range(505,n-1):
        p=Pv[i]
        g=p/ep-1
        tier=np.where(inpos,np.maximum(tier,np.where(g>=1.0,2,np.where(g>=0.5,1,0))),0)
        stop=np.where(tier==2,d50[i],np.where(tier==1,d100[i],d150[i]))
        out=inpos&(p<stop)
        e=(~inpos)&entry_sig(i,min_to)&np.isfinite(Ov[i+1])&(Ov[i+1]>0)
        ev_out[i+1]=out; ev_in[i+1]=e
        inpos=(inpos&~out)|e; ep=np.where(e,Ov[i+1],ep); tier=np.where(e,0,tier); edate=np.where(e,i+1,edate)
        state[i+1]=inpos; ED[i+1]=edate
    return ev_in,ev_out,state,ED
def sim_ath(V,N,c,y,carry,cap=20000.0):
    ev_in,ev_out,state,ED=V
    s,e=window(y); i0=dates.get_loc(s); i1=dates.get_loc(e)
    cash=cap; pos={}; trades=0; fees=0.0
    def val(i):
        return cash+sum(q*np.nan_to_num(Pf[i,k]) for k,q in pos.items())
    def buy(i,ks):
        nonlocal cash,fees,trades
        slot=val(i-1)/N
        for k in ks:
            if len(pos)>=N or cash<100: break
            amt=min(slot,cash); spend=amt/(1+c); pos[k]=spend/Ov[i,k]; cash-=amt; fees+=spend*c; trades+=1
    for i in range(i0,i1+1):
        for k in [k for k in pos if ev_out[i,k]]:
            px=Ov[i,k] if np.isfinite(Ov[i,k]) else Pf[i-1,k]
            v=pos.pop(k)*px; cash+=v*(1-c); fees+=v*c; trades+=1
        if i==i0 and carry:
            ks=np.where(state[i]&~ev_in[i]&np.isfinite(Ov[i]))[0]
            ks=ks[np.argsort(-ED[i,ks])]       # most recent entry first
            buy(i,list(ks))
        ks=sorted(np.where(ev_in[i])[0], key=lambda k:P.columns[k])   # gieldowo: same-day ties by ticker
        buy(i,[k for k in ks if k not in pos])
    last=Pf[i1]
    v=cash+sum(q*last[k] for k,q in pos.items())
    return v/cap-1,trades,fees
years=list(range(2003,2026)); w=wigret(years)
STRATS={'spokojna':('hi52',10,20),'podium':('combo',3,6)}
res=[]
for mt in [300_000,50_000]:
    V=virtual(mt)
    for N in [5,10,20]:
        for carry in [False,True]:
            for y in years:
                r_,tr,fe=sim_ath(V,N,0.0039,y,carry); res.append(dict(strat=f'ath N={N} {"carry" if carry else "fresh"}',min_to=mt,year=y,ret=r_,trades=tr,fees=fe))
    for name,(sig,N,buf) in STRATS.items():
        for y in years:
            r_,tr,fe=sim(sig,N,buf,0.0039,y,min_to=mt); res.append(dict(strat=name,min_to=mt,year=y,ret=r_,trades=tr,fees=fe))
R=pd.DataFrame(res); R['wig']=R.year.map(w)
def stats(g):
    x=g.ret
    return pd.Series(dict(mean=x.mean(),median=x.median(),q10=x.quantile(.1),worst=x.min(),best=x.max(),
        beatWIG=((x-g.wig)>0).mean(),loss=(x<0).mean(),p40=(x>.4).mean(),late=g[g.year>=2013].ret.mean(),trades=g.trades.mean()))
S=R.groupby(['min_to','strat']).apply(stats).reset_index()
pd.set_option('display.width',250); print(S.round(3).to_string()); print('WIG mean',round(w.mean(),3),'late',round(w[w.index>=2013].mean(),3))
R.to_csv('athdma_years.csv',index=False)
