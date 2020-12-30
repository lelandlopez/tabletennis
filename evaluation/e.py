import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
from multiprocessing import Pool
from functools import partial
import sys
import timeit
from multiprocessing import Pool, cpu_count

df = pd.read_csv('../csv/afterSplit.csv')
def wrapper(func, *args, **kwargs):
     def wrapped():
         return func(*args, **kwargs)
     return wrapped
def f(df):
    df['Score_cumsum', 'fromtoscore'] = df.groupby(['Player'])['Score', 'fromtoscore'].cumsum()
    # print(df['Score_cumsum'].head())

def f2(df):
    df['Score_cumsum', 'fromtoscore'] = df.groupby(['Player'])['Score', 'fromtoscore'].apply(np.cumsum)
    # print(df['Score_cumsum'].head())

    # df['Score_cumsum'] = df.groupby(['Player'])['Score'].cumsum()

fwrapped = wrapper(f, df)
# f2wrapped = wrapper(f2, df)

print(timeit.timeit(fwrapped, number=100))
# print(timeit.timeit(f2wrapped, number=100))

# df = pd.read_csv('../csv/afterSplit.csv')
# SETUP_CODE = '''
# import pandas as pd
# import time
# from ast import literal_eval
# import numpy as np
# from sklearn import preprocessing
# from multiprocessing import Pool
# from functools import partial
# import sys
# import timeit
# '''
#
# TEST_CODE = '''
# df['Score'] = df['Score'].astype('float')
# df.groupby(['Player'])['Score'].expanding().sum()
# '''
#
# times = timeit.repeat(setup = SETUP_CODE,
#                           stmt = TEST_CODE,
#                           repeat = 3,
#                           number = 50)
# def Average(lst):
#     return sum(lst) / len(lst)
#
# print(Average(times), min(times), max(times))
