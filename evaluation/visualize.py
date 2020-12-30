import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
from multiprocessing import pool
from functools import partial
import sys
import time
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('../csv/working.csv')
df.head()
start = time.time()
lefts = [i for i in df.columns if 'left' in i and 'last' in i]
# bares = [left[:len('_left') * -1] for left in lefts]
# rights = [bare + '_right' for bare in bares]
# df[lefts].subtract(df[rights], axis=0)
# df[lefts].subtract
for left in lefts:
    bare = left[:len('_left') * -1]
    diff = bare + '_diff'
    right = bare + '_right'
    df[diff] = df[left].sub(df[right])
print(time.time()-start)

df = pd.read_csv('../csv/beforeMerge.csv', index_col = False )


df = pd.read_csv('../test.csv', index_col = False )
cdf = pd.read_csv('../test_before.csv')
df.columns
k = [i for i in cdf.columns if 'cumsum' in i]
k = ['last_Scorew_left', 'last_', 'last_Player_Score_cumsum_right']
df[(df['Player_left'] == 'Muslikov S.') | (df['Player_right'] == 'Muslikov S.')][['Player_left', 'Player_right', 'id'] + k]

# sys.path.insert(1, './evaluation')
# from helpers import helpers
# df = pd.read_csv('../csv/working.csv')
# df.columns
# from ast import literal_eval
# df['lwin'] = df['Score_left']
# ku
# print(df.shape)
# print([i for i in df.columns if 'num_match' in i and 'last' not in i ])
# df.head()
# df = pd.read_csv('../matchDF.csv')
# df[['lScore', 'rScore']]
# df['lwin'] = df['lScore'] > df['rScore']
# df['lwin'].value_counts()
# df = pd.read_csv('../csv/working.csv')[0:2000]
# df.columns
# df[['datetime']]
# df.dtypes
# df[df['lGames'].apply(len) == 0]
# df = df[df['lGames'].apply(len) != 2]
# df.head()
# df[['lGames', 'rGames']]
# df = df[df['lScore'] != df['rScore']]
#
# df['lGames'] = df['rGames'].apply(literal_eval)
# df['len_new'] = df['new'].apply(len)
# df['len_new']
# df.columns
# df['datetime'].astype(str).str.apply(lambda x: print(len(x)))
# df['d'] = df['datetime'].astype(str).apply(lambda x: len(x))
# df['d'].value_counts()
# df[['Player', 'other_label', 'datetime']]
# df.columns
df = pd.read_csv('../csv/beforeMerge.csv')
df
df.columns
cols = ['Player_num_match', 'Player'] + [i for i in df.columns if 'diff' in i] + ['Player_num_match']
k = df[(df['Player'] == 'Mishakin V.')].sort_values('Player_num_match')
k[['datetime', 'Player_num_match', 'last_Score', 'last_Player_Score_cumsum']]
# df = pd.read_csv('../matchDF.csv')
# df.head()
# Vinit = pd.read_csv('./matchDF.csv')
# init['lwin'] = init['lScore'] > init['rScore']
# p = df.merge(init, on='id')
# df.shape
# p.shape
# p.head()
# k = [i for i in df.columns if 'diff' in i]
# p = p[k + ['lwin']]
#
# for i in k:
#     plt.figure()
#     sns.kdeplot(data=p, x=i, hue="lwin")
#     plt.show(block=False)
# plt.show()

# mdf = pd.read_csv('../matckkbbbbbbbbbbkDF.csv')
# mdf['lwin'] = mdf['lScore'] > mdf['rScore']
# df = mdf[['lwin', 'id']].merge(df, on='id')
# k = [i for i in df.columns if '_ave' in i]
# df.columns
# k = df.columns.to_list()
# cols = [i for i in list(df.columns) if str(i).endswith('_diff')] + ['lwin']
# cols

# df[cols]
# df[cols]
# df.columns


# df = pd.read_csv('./csv/beforeMerge.csv')
# df['datetime']
# df['date'] = df['datetime'].astype(str).str[0:8]
# df['date'] = df['date'].astype('int')
# df[df['Player'] == 'Chernov V.'][['date', 'num_games', 'Score', 'last_Score_cumsum_ave']]
# df.columns[0:100]


# k = [i for i in df.columns if 'cumsum' in i]
# print([i for i in k if 'ave' not in i])
# print(df.columns)
# print(df.shape)



#
# df.head()
# df.columns
# df.columns
# df[['index']]
# cols = [i for  i in df.columns if 'index' in i]
# cols
# cols = [i for  i in df.columns if 'diff' in i]
# df[cols]
# df.columns
