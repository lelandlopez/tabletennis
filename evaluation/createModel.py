import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
from multiprocessing import pool
from functools import partial
import sys
import time

start = time.time()
sys.path.insert(1, './')
from evaluate import evaluate
evaluate(pd.read_csv('./csv/working.csv'))
