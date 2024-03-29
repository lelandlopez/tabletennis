import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
from multiprocessing import pool
from functools import partial
import sys
import time
import pickle
sys.path.insert(1, './')
from helpers import helpers
from formatter import formatter

start = time.time()

df = helpers.createDF()

lenargs = len(sys.argv)
if  lenargs == 1:
    df = formatter(df)
elif lenargs == 2:
    if sys.argv[1] == 'test':
        df = formatter(df[0:2000], True)
    else:
        print('not recognized')
elif lenargs == 3:
    if sys.argv[1] == 'test':
        df = formatter(df[0:int(sys.argv[2])], True)
    else:
        print('not recognized')
df.to_csv('./csv/working.csv', index=False)
print(time.time()-start)
