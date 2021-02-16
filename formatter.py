import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
import sys
import time
from ast import literal_eval
sys.path.insert(1, '..')
from helpers import helpers
sys.path.insert(1, './formatter')
from autoFeatureEngineer import autoFeatureEngineer
                    
afe = autoFeatureEngineer(True)

@helpers.printTime
def dropAndFormat(df, ignore_ids = []):
    df = afe.dropBadGames(df, ignore_ids)
    df = afe.dropBadSequencer(df, 'datetime')
    df = afe.formatSequencer(df, 'datetime')
    return df



@helpers.printTime
def createColsBeforeSplit(df):
    df = afe.createWinColumns(df, ['l', 'r'], 'Score')

    df = afe.applyOnBoth(df, 
            ['Games', 'Games'],
            literal_eval)

    df = afe.applyOnBoth(df, 
            ['Games', 'Games'],
            lambda x: [int(i) for i in x])

    print(df.columns)
    df = afe.createDiffColumns(df)
    print(df.columns)

    df = afe.applyOnBoth(df, 
            ['DiffGamesSum', 'DiffGames'],
            lambda x: sum(x))

    df = afe.applyOnBoth(df, 
            ['Games_len', 'Games'],
            len)

    df.loc[df['lScore'] >= df['rScore'], 'toScore'] = df['lScore']
    df.loc[df['lScore'] < df['rScore'], 'toScore'] = df['rScore']
    df = df.replace(['-'], np.nan)
    df['toScore'] = df['toScore'].astype(float)

    df = afe.applyOnBoth(df, 
            ['FirstGameW', 'DiffGames'],
            lambda x: x[0] > 0 if len(x) > 0 else False)
    return df

def createStatsAfterSplit(df):
    le = preprocessing.LabelEncoder()
    df['label'] = le.fit_transform(df.Player.values)
    df['other_label'] = le.fit_transform(df.otherPlayer.values)
    df['Score'] = df['Score'].astype('float')
    df['ScoretoScore'] = df['toScore']-df['Score']


    groups = [['Player'], ['Player', 'other_label']]
    cols = ['Score', 'ScoretoScore', 'Win', 'Games_len']
    dividers = ['Games_len']
    sn = []

    for group in groups:
        colsToShift = []
        df, numMatchCol = afe.createNumMatch(df, group)
        df, cumsumCols = afe.getCumsum(df, group, cols)
        colsToShift = colsToShift + cumsumCols
        df, rollingSumCols = afe.getRollingSum(df, group, cols, 5)  
        colsToShift = colsToShift + rollingSumCols

        names = afe.createDivNames(group, cols, numMatchCol, '_ave')
        # print(df.head())
        # df = df.reset_index(drop=True)
        # print(df.head())
        colsToShift = colsToShift + names
        df[names] = df[cumsumCols].div(df[numMatchCol] + 1, axis=0)
        for divider in dividers:
            n = afe.createDivNames(group, cols, divider, '_ave')
            div = afe.createNames(group)
            df[n] = df[cumsumCols].div(df[div + divider + '_cumsum'], axis=0)
            colsToShift = colsToShift + n


        df, shiftedNames = afe.shift(df, group, colsToShift)
        sn = sn + shiftedNames

    df = df[sn + ['Player', 'id']]
    return df


def formatter(df, save = False, **kwargs):
    copy = df.copy()
    sys.path.insert(1, './formatter/')

    if 'ignore_ids' in kwargs:
        df = dropAndFormat(df, kwargs['ignore_ids'].tolist())
    else:
        df = dropAndFormat(df)
    print(df)

    df = createColsBeforeSplit(df)
    df = afe.split(df, ['Player', 'Score', 'Win', 'Games_len', 'DiffGamesSum'], ['id', 'datetime', 'toScore'])
    print(df)
    df = createStatsAfterSplit(df)
    k = copy

    df = afe.merge(df, k)
    df = afe.cleanup(df)
    return df

