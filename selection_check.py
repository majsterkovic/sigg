"""Paired sign randomisation with a max-over-configurations selection correction."""
import argparse
import json
import numpy as np
import pandas as pd


def check(path,draws=100000,seed=20261116):
    r=pd.read_csv(path);p=r.pivot(index='year',columns=['min_to','basket','strat'],values='ret')
    differences=np.array([p[col]-p[(col[0],'całość (z NC)',col[2])] for col in p]).T
    key=(300000,'płynność 21–140 (proxy)','podium (combo, 3)');target=list(p.columns).index(key)
    observed=differences.mean(axis=0);rng=np.random.default_rng(seed)
    null=rng.choice([-1,1],size=(draws,len(p)))@differences/len(p)
    bootstrap=differences[rng.integers(0,len(p),size=(draws,len(p))),target].mean(axis=1)
    return dict(seed=seed,draws=draws,n_years=len(p),n_configurations=len(p.columns),target=list(key),
        paired_gain=float(observed[target]),wins=int(sum(differences[:,target]>0)),
        p_one_sided=float((1+sum(null[:,target]>=observed[target]))/(draws+1)),
        p_max_configurations=float((1+sum(null.max(axis=1)>=observed[target]))/(draws+1)),
        bootstrap90=np.quantile(bootstrap,[.05,.95]).tolist(),
        caveat='In-sample exploratory result; annual sign symmetry assumed. Earlier signal selection is not included.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--years',default='results/seg_years.csv');ap.add_argument('--out',default='results/selection_check.json')
    a=ap.parse_args();r=check(a.years);open(a.out,'w').write(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
