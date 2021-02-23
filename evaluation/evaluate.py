import pandas as pd
import time
from ast import literal_eval
import numpy as np
import pickle
import sys
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
sys.path.insert(1, './helpers')
from helpers import helpers

filename = './models/finalized_model.sav'
cols_filename = './models/finalized_model_features.csv'
matchDF_filename = './csv/static/matchDF.csv'

def splitForTraining(df, split):
    df = prep(df)
    df = calculateLWIN(df)
    df = df.drop(columns=['id'])

    train, test = train_test_split(df, test_size=0.2)

    train_features = train.drop(columns=['lwin', 'lScore', 'rScore'])
    test_features = test.drop(columns=['lwin', 'lScore', 'rScore'])
    train_labels = train[['lwin']]
    test_labels = test[['lwin']]
    train_features = train_features[[i for i in train_features.columns if train_features[i].dtypes != 'object']]
    test_features = test_features[[i for i in test_features.columns if test_features[i].dtypes != 'object']]
    return train_features, test_features, train_labels, test_labels


def prep(df):
    if 'Player_left' in df.columns:
        df = df.drop(columns=['Player_left', 'Player_right'])
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)
    return df 

  
def calculateLWIN(df, **kwargs):
    if 'mergeDF' in kwargs:
        k = kwargs['mergeDF']
    else:
        k = helpers.createDF()
    df = df.merge(k[['lScore', 'rScore', 'id']], on='id', how='left', suffixes=['', '_y'])
    df = df[df['lScore'] != df['rScore']]
    df['lwin'] = df['lScore'] > df['rScore']
    return df

def randomForest(train_features, test_features, train_labels, test_labels):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_selection import SelectFromModel
    sel = SelectFromModel(RandomForestClassifier(n_estimators = 500))
    sel.fit(train_features, train_labels.values.ravel())
    selected_feat= train_features.columns[(sel.get_support())]
    train_features = train_features[selected_feat]

    rf = RandomForestClassifier(n_estimators = 1000, n_jobs = -1).fit(train_features, train_labels.values.ravel())

    filename = './finalized_model.sav'
    pickle.dump(rf, open(filename, 'wb'))
    test_features = test_features[selected_feat]
    predictions = rf.predict_proba(prep(test_features))
    predict = rf.predict(test_features)
    accuracy = rf.score(test_features, test_labels.values.ravel())
    predict = pd.DataFrame(predict)
    predictions = pd.DataFrame(predictions)
    k = np.concatenate([predictions, predict, test_labels], axis = 1)
    k = pd.DataFrame(k)
    k[0]
    d = k

    print("RF: ",  accuracy)
    return rf


def xgb(train_features, test_features, train_labels, test_labels):
    from xgboost import XGBClassifier
    from sklearn.feature_selection import SelectFromModel
    sel = SelectFromModel(XGBClassifier(n_estimators = 500, n_jobs = -1))
    sel.fit(train_features, train_labels.values.ravel())
    selected_feat= train_features.columns[(sel.get_support())]
    train_features = train_features[selected_feat]

    rf = XGBClassifier(n_estimators = 1000, n_jobs = -1).fit(train_features, train_labels.values.ravel())

    pickle.dump(rf, open(filename, 'wb'))
    test_features = test_features[selected_feat]
    df = pd.DataFrame(selected_feat)
    df.to_csv(cols_filename)
    predictions = rf.predict_proba(test_features)
    predict = rf.predict(test_features)
    accuracy = rf.score(test_features, test_labels.values.ravel())
    predict = pd.DataFrame(predict)
    predictions = pd.DataFrame(predictions)
    k = np.concatenate([predictions, predict, test_labels], axis = 1)
    k = pd.DataFrame(k)
    print("RF: ",  accuracy)
    return rf

def predict(features, filename = filename, cols_filename = cols_filename):
    features = prep(features)
    rf = pickle.load(open(filename, 'rb'))
    df = pd.read_csv(cols_filename, index_col=False)
    cols = df['0'].to_list()
    predictions = rf.predict_proba(features[cols])
    return predictions



# @helpers.printTime
def evaluate(df, type):
    train_features, test_features, train_labels, test_labels = splitForTraining(df, 2/3)
    if type == 'randomForest':
        rf = randomForest(train_features, test_features, train_labels, test_labels)
    elif type == 'xgb':
        rf = xgb(train_features, test_features, train_labels, test_labels)
        print(rf)
    else:
        print(type, ': not supported model')

    importances = rf.feature_importances_
    indices = np.argsort(importances)
    features = train_features.columns
    pyplot.title('Feature Importances')
    pyplot.barh(range(len(indices)), importances[indices], color='b', align='edge', height=1, linewidth=1)
    pyplot.yticks(range(len(indices)), [features[i] for i in indices])
    pyplot.xlabel('Relative Importance')
    pyplot.show()    # Make predictions and determine the error

