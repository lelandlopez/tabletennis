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

matchID = 'E3G2nI5H'
start = time.time()
sys.path.insert(1, './')
from formatter import formatter
k = formatter(matchID)
k.to_csv('./csv/asdfasdf.csv', index=False)
print(k.shape)


r, l = 'Pandur I.','Mishakin V.'

df = pd.read_csv('./csv/working.csv')
df = df[(df['Player_left'] == l) | (df['Player_left'] == r) | (df['Player_right'] == l) | (df['Player_right'] == r) ]
print(df.shape)
print(k.eq(df))
# print(df[['datetime_left', 'datetime_right', 'lastScore_ave_left', 'lastScore_ave_right']])
# df.shape
# df[df['id'] == '6civ8qu0'][['Player_left', 'Player_right']]
# df = df[(df['Player_left'] == 'Mishakin V.') | (df['Player_left'] == 'Belugin 0.') | (df['Player_right'] == 'Mishakin V.') | (df['Player_right'] == 'Belugin 0.') ]
# print(df.shape, k.shape)
# print(df.iloc[26][df.columns].equals(k.iloc[26][df.columns]))
    # if (t[[i]].eq(p[[i]])) == False:
    #     print(t[[i]], p[[i]])
#
# df = pd.read_csv('./csv/working.csv')


# print([x for x in df.columns if 'result' in x])
# cols = pd.read_csv('./csv/finalized_model_columns.csv', index_col = 0).fetures.values
# df = df[cols]
# sys.path.insert(1, './evaluation/')
# from evaluate import prepForPredict
# df = prepForPredict(df)
# temp = df.drop(columns=['id'])
#
# filename = './finalized_model.sav'
# rf = pickle.load(open(filename, 'rb'))
# # Make predictions and determine the error
# predictions = rf.predict_proba(temp)
# predict = rf.predict(temp)
#
# df['predictions'] = predictions.tolist()
# df['predict'] = predict.tolist()
# # train = train.join(predictions)
#
# k = pd.read_csv('./matchDF.csv')
#
# k = k[['id', 'lPlayer', 'rPlayer', 'lScore', 'rScore']].merge(df, on='id', how='right')
# k['predict_x'] = 1 - k['predict']
# k['predict_y'] = 2 - k['predict']
# # k = k[(k['lScore'] == 0) & (k['rScore'] == 0)]
# # k['pred'] = k['predictions'].to_list()
# k['rWinPer'] = k['predictions'].apply(lambda x: x[0])
# k['lWinPer'] = k['predictions'].apply(lambda x: x[1])
# # k['pred2'] = k['pred'].apply(lambda x: x[2])
# print(k[['lPlayer', 'rPlayer', 'id', 'lWinPer', 'rWinPer', 'predict']])
