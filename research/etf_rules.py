"""ETF rules independent of the database, with explicit policy history."""
import pandas as pd
from corporate import stable_ranking

CASH_START=pd.Timestamp('2024-01-02')

def mask_policy_history(frame,cash_id):
 result=frame.copy()
 result.loc[result.index<CASH_START,cash_id]=float('nan')
 return result

def etf_choice(momentum,eligible,equities,cash_id,rule,risk_on=True):
 """One full-capital slot. Ineligible fund is never treated as executable cash."""
 x=stable_ranking(momentum.reindex(equities).where(eligible.reindex(equities,fill_value=False)))
 if rule=='wig_cash':
  if risk_on:return x
  x=x.iloc[:0]
 elif rule in ['positive','positive_cash']:
  x=x[x>0]
 if len(x):return x
 if rule in ['positive_cash','wig_cash'] and eligible.get(cash_id,False) and momentum.get(cash_id,float('nan'))>0:
  return pd.Series({cash_id:1.})
 return pd.Series(dtype=float)
