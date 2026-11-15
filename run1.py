from bt import *
years=range(1998,2026); MIN=300_000; COST=0.0039
w=wigret(years); e=ew(MIN,years)
rows=[]
def summ(name,d):
    x=d.ret; ex=x-w.reindex(x.index); exe=x-e.reindex(x.index)
    return dict(strat=name,n=len(x),mean=x.mean(),median=x.median(),min=x.min(),max=x.max(),
      beatWIG=(ex>0).mean(),exWIG=ex.mean(),exEW=exe.mean(),p20=(x>0.2).mean(),p40=(x>0.4).mean())
rows.append(summ('WIG',pd.DataFrame({'ret':w})))
rows.append(summ('EW univ',pd.DataFrame({'ret':e})))
for sig in SIG:
    for N in (1,3,5,10):
        rows.append(summ(f'{sig} top{N}',run(sig,N,MIN,COST,years)))
R=pd.DataFrame(rows).set_index('strat')
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(R.round(3).to_string())
R.to_csv('run1.csv')
