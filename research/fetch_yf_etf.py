"""Fetch Warsaw ETF bars from Yahoo (.WA) plus gold proxy inputs into SIGG_DATA_DIR. Run with the yfinance python."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd,yfinance as yf
from paths import DATA,data_path

CODES='ETFSP500 ETFDAX ETFNATO ETFPZUGOLD ETFBW20TR ETFBM40TR ETFBS80TR ETFBSPXPL ETFBNDXPL ETFBTBSP ETFBCASH ETFBTCPL'.split()
PROXY={'GOLD_USD':'GC=F','USDPLN':'PLN=X'}

def main():
 if DATA.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Set SIGG_DATA_DIR outside repository')
 bars=[];divs=[]
 for code in CODES:
  t=yf.Ticker(code+'.WA')
  d=t.history(start='2005-01-01',end='2026-11-14',auto_adjust=False,actions=True)
  if not len(d):print(code,'no data');continue
  d.index=d.index.tz_localize(None).normalize();d.index.name='date'
  d['code']=code;bars.append(d.reset_index()[['code','date','Open','High','Low','Close','Adj Close','Volume']])
  x=d['Dividends'];x=x[x>0]
  divs+= [dict(code=code,ex_date=i,value=float(v)) for i,v in x.items()]
  print(code,len(d),d.index.min().date(),d.index.max().date(),flush=True)
 pd.concat(bars).to_parquet(data_path('yf_war_etf.parquet'),index=False)
 pd.DataFrame(divs).to_parquet(data_path('yf_war_etf_dividends.parquet'),index=False)
 proxy=[]
 for name,ticker in PROXY.items():
  d=yf.Ticker(ticker).history(start='2002-06-01',end='2026-11-14',auto_adjust=False)
  d.index=d.index.tz_localize(None).normalize();proxy.append(d['Close'].rename(name))
 pd.concat(proxy,axis=1).to_parquet(data_path('yf_gold_proxy.parquet'))
 print('saved',DATA)

if __name__=='__main__':main()
