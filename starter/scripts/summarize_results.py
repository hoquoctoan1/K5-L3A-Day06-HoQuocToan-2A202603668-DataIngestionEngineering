"""Recompute hit counts from explicit review labels, without guessing labels."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluation import summarize

parser=argparse.ArgumentParser()
parser.add_argument('--dev-run',default='dev_20261113_210325')
parser.add_argument('--test-run',default='test_20261113_214547')
args=parser.parse_args()
results=Path(__file__).resolve().parents[1]/'results'
rows=[]
for split,run in [('dev',args.dev_run),('test',args.test_run)]:
    for review in json.loads((results/run/f'{split}_review.json').read_text(encoding='utf-8')):
        rows.append({**review,'split':split})
print(json.dumps(summarize(rows),ensure_ascii=False,indent=2))
