"""Fixed hypotheses, separate from operational strategy rules."""
import numpy as np
import pandas as pd


def decorrelate(ranked, returns, threshold=.70, min_overlap=84):
    """Greedy admissible ranking; returns must end on the signal date."""
    corr=returns.reindex(columns=ranked.index).corr(min_periods=min_overlap)
    accepted=[]
    for k in ranked.index:
        values=corr.loc[k,accepted]
        if not accepted or (np.isfinite(values).all() and (values<=threshold).all()):
            accepted.append(k)
    return ranked.loc[accepted]


def risk_on(wig, t, periods=200):
    history=wig.loc[:t].dropna().tail(periods)
    return len(history)==periods and history.iloc[-1]>history.mean()


def choose_training_winner(years, target_year):
    train=years[years.year<target_year]
    means=train.groupby('variant').ret.mean()
    return means.sort_index().sort_values(ascending=False,kind='stable').index[0]
