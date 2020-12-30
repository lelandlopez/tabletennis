from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time
import numpy as np
import multiprocessing
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
import seaborn as sns
from matplotlib import pyplot
import pickle
matchDF_filename = './csv/static/matchDF.csv'

df = pd.read_csv(matchDF_filename)
# k = pd.read_csv('../csv/afterFormat.csv', index_col=0)
# k[k['max'] == 4]

# k['max'].value_counts()
# k['max'].value_counts()
# df = df[['id']].merge(k, on='id', how='left')

# df[-50:]
# df.shape
# df.shape
# df = pd.read_csv('./oneoffformatted_diff.csv')
# k = pd.read_csv('../FinalModel.csv', index_col=0)
# df = df[k['features'].to_list() + ['date', 'id']]
# df.shape
# df[df['lPlayer'] == 1304]
# df
# df
# df.shape
# df['year'] = df['date'].astype(str).str[0:4]
# df = df.drop(columns=['lScore', 'rScore', 'lresult', 'rresult'])
df = df.replace([np.inf, -np.inf], np.nan)
df = df.fillna(0)


# df = df.drop(columns=['year', 'num_game_otherPlayer_diff'])

def evaluate(df):
    from sklearn.model_selection import train_test_split
    from sklearn import metrics
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    # train = df[df['date'] == 20201008]
    train = df
    train.columns
    train_features = train.drop(columns=['id'])

    # train = df[(df['date'] == 20200830) & (df['legs'] == 9)]
    # train

    # print(train_features.columns)
    # print(test_features.columns)
    # print(train_labels.columns)
    # print(test_labels.columns)
    # train_features, test_features, train_labels, test_labels = train_test_split(df.drop(columns=['lwin']), df['lwin'], test_size = 0.25, random_state = 42)
    filename = './models/finalized_model.sav'
    rf = pickle.load(open(filename, 'rb'))
    # Make predictions and determine the error
    predictions = rf.predict_proba(train_features)
    predict = rf.predict(train_features)
    # train = train.join(predictions)
    train['predictions'] = predictions.tolist()
    train['predict'] = predict.tolist()
    return train

print(df.dtypes)

predictions = evaluate(df)
predictions
# predictions[['id', 'predictions', 'predict']]
df = pd.read_csv('./matchDF.csv')

k = df[['id', 'lPlayer', 'rPlayer']].merge(predictions, on='id', how='right')
k
predictions
# k = k[pd.isnull(k['lScore']) == False]
# k = k[(k['lScore'] == 0) & (k['rScore'] == 0)]
# k['pred'] = k['predictions'].to_list()
k['pred0'] = k['predictions'].apply(lambda x: x[0])
k['pred1'] = k['predictions'].apply(lambda x: x[1])
# k['pred2'] = k['pred'].apply(lambda x: x[2])
k
k[k['id'] == 'IsU3bBfL'][['lPlayer', 'rPlayer', 'id', 'pred0', 'pred1', 'predict']]
# k
# k['pred0'] = [KvhPfXbE]
# k['pred1'] = k['predictions'][1]



# predictions['predictions'][0]
# k[['lPlayer_x', 'rPlayer_x', 'id', 'predictions', 'predict']]
# k[k['id'] == 'j5kAVUgD'][['lPlayer_x', 'rPlayer_x', 'id', 'predictions', 'predict']]
# # kkV
# k[k['id'] == 'j5kAVUgD']
# k.columns
# k
# df[df['id'] == 'j5kAVUgD'][['todayGameNumber_left', 'todayGameNumber_right']]

# # df.describe
#
# from bs4 import BeautifulSoup
# import pandas as pd
# import os
# import sys
# import time
# import numpy as np
# import multiprocessing
# from sklearn import preprocessing
# from sklearn.metrics import roc_auc_score
# import seaborn as sns
# import pickle
#
# df = pd.read_csv('./formatted_diff.csv')
# df['lwin'] = df['lScore'] > df['rScore']
# df['year'] = df['date'].astype(str).str[0:4]
# df = df.drop(columns=['id', 'lScore', 'rScore', 'lresult', 'rresult', 'date'])
# df = df.replace([np.inf, -np.inf], np.nan)
# df = df.fillna(0)
# df['lPlayer'] = df['lPlayer'].astype('category')
# df['rPlayer'] = df['rPlayer'].astype('category')
#
#
# df = df.drop(columns=['year', 'happened', 'num_game_otherPlayer_diff'])
#
# df.head()
# def predict(df):
#     from sklearn.model_selection import train_test_split
#     from sklearn import metrics
#     from sklearn.ensemble import RandomForestRegressor
#     from sklearn.model_selection import train_test_split
#     features = df.drop(columns=['lwin'])
#     print(len(features.columns))
#     filename = './finalized_model.sav'
#     rf = pickle.load(open(filename, 'rb'))
#     # Make predictions and determine the error
#     predictions = rf.predict(features)
#     print(predictions)
#     # df['lwinPer'] = predictions
#     # print(df)
#     # df.to_csv('./predictions.csv')
#
# predict(df)
