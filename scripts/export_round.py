import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.db import init_db,seed_demo,one
from app.services.csv_service import round_csv_text

p=argparse.ArgumentParser(description='Export one Greenhill ordering round to CSV.')
p.add_argument('--round',type=int,required=True,help='Round number, e.g. 35')
p.add_argument('--output',help='Output filename; defaults to round_<number>.csv')
a=p.parse_args()
init_db(); seed_demo()
r=one('SELECT * FROM rounds WHERE number=?',(a.round,))
if not r: raise SystemExit(f'Round {a.round} not found')
out=Path(a.output or f'round_{a.round}.csv')
out.write_text('\ufeff'+round_csv_text(r['id']),encoding='utf-8')
print(out.resolve())
