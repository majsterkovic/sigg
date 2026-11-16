"""Read-only export: raw data to SIGG_DATA_DIR outside the repository."""
import sys,re,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
from db import q
from paths import DATA

ETF_ISINS='''PLBETWT00010 PLBTFDP00015 PLBTRLV00011 PLBTRSH00015 PLBETF400025 PLBETFN00018 PLBTN2S00018 PLBTN3L00011 PLBSWTR00014 PLBETFS00017 PLBTBSP00012 PLBTFBN00014 PLBEW2L00019 PLBETF200011 PLBTETF00015 LU0252633754 IE000I7E6HL0 IE000IQQEL77 IE0003XW12I8 IE00BNTVVR89 IE0007WMHDE3 IE00BKPTXQ89 IE000R8PO127 IE0005YK6564 IE000MMRLY96 IE000OJ5TQP4 PLPZUZM00011 PLPZUGD00010 PLPZUDG00010 PLPZUTR00013 PLPZUMW00018 LU0496786574'''.split()

def main():
 if DATA.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Set SIGG_DATA_DIR outside repository')
 DATA.mkdir(parents=True,exist_ok=True)
 game=set(re.findall(r'\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b',(ROOT/'data/sigg_instruments_2026-11-16.txt').read_text()))
 assert len(ETF_ISINS)==32 and set(ETF_ISINS)<=game
 meta=q('''select i.instrument_id,i.isin,i.name,i.ref_ticker,i.kind,l.code,l.currency,l.yahoo_ticker
 from instrument i left join listing l on i.instrument_id=l.instrument_id and l.exchange_code='WAR'
 where i.isin=any(%s)''',(ETF_ISINS,))
 assert len(meta)==32 and meta['isin'].nunique()==32
 meta.to_csv(DATA/'etf_metadata.csv',index=False)
 valid=meta.ref_ticker.str.endswith('.WAR')&meta.currency.eq('PLN')
 ids=meta.loc[valid,'instrument_id'].tolist()
 for table,out in [('daily_price','px'),('split','split'),('dividend','dividend')]:
  q('select * from '+table+' where instrument_id=any(%s)',(ids,)).to_parquet(DATA/f'etf_{out}.parquet',index=False)
 print(f'{len(meta)} ISIN; {len(ids)} series with WAR primary listing and PLN; private export: {DATA}')

if __name__=='__main__':main()
