import pandas as pd
import sys

sys.path.insert(1, './')
from evaluate import evaluate
df = pd.read_csv('./csv/working.csv')
df = df.drop(columns=[i for i in df.columns if "datetime" in i])
df = df.drop(columns=[i for i in df.columns if "index" in i])
if len(sys.argv) == 2:
    evaluate(df, sys.argv[1])
else:
    print('required model arg')
