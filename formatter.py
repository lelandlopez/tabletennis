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

    def AOB_findFirstGameW(x):
        if len(x) > 0:
            return x[0] > 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstGameW', 'DiffGames'],
            lambda x: AOB_findFirstGameW(x))


    def AOB_findFirstTwoGamesW(x):
        if len(x) > 1:
            return x[0] > 0 and x[1] > 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstTwoGamesW', 'DiffGames'],
            lambda x: AOB_findFirstTwoGamesW(x))

    def AOB_findFirstThreeGamesW(x):
        if len(x) > 2:
            return x[0] > 0 and x[1] > 0 and x[2] > 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstThreeGamesW', 'DiffGames'],
            lambda x: AOB_findFirstThreeGamesW(x))

    def AOB_findFirstGameL(x):
        if len(x) > 0:
            return x[0] < 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstGameL', 'DiffGames'],
            lambda x: AOB_findFirstGameL(x))


    def AOB_findFirstTwoGamesL(x):
        if len(x) > 1:
            return x[0] < 0 and x[1] < 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstTwoGamesL', 'DiffGames'],
            lambda x: AOB_findFirstTwoGamesL(x))

    def AOB_findFirstThreeGamesL(x):
        if len(x) > 2:
            return x[0] < 0 and x[1] < 0 and x[2] < 0
        return False
    df = afe.applyOnBoth(df, 
            ['FirstThreeGamesL', 'DiffGames'],
            lambda x: AOB_findFirstThreeGamesL(x))

    return df


def createStatsAfterSplit(df):
    le = preprocessing.LabelEncoder()

    print(df.Player.values)

    print(df.Player.dtypes)
    df['Player'] = df['Player'].astype('str')
    df['label'] = le.fit_transform(df.Player.values)
    df['other_label'] = le.fit_transform(df.otherPlayer.values)
    df['Score'] = df['Score'].astype('float')
    df['ScoretoScore'] = df['toScore']-df['Score']




    groups = [['Player'], ['Player', 'other_label']]
    cols = ['Score', 'ScoretoScore', 'Win', 'Games_len']
    dividers = ['Games_len']
    sn = []


    for group in groups:


        df, numMatchCol = afe.createNumMatch(df, group)

        colsToShift = []
        for i in ['FirstGameW', 'FirstTwoGamesW', 'FirstThreeGamesW', 'FirstGameL', 'FirstTwoGamesL', 'FirstThreeGamesL']:
            df, n = afe.createWinXWin_game_X(df, group, ['Win', i])
            df, c = afe.getCumsum(df, group, [i, n])
            d = afe.createDivNames(group, [n], c[0])
            df[d] = df[c[1]].div(df[c[0]], axis=0)
            colsToShift = colsToShift + [n] + c + d

        

        df, cumsumCols = afe.getCumsum(df, group, cols)
        df, streakCols = afe.createWinStreaks(df, group, ['Win'])
        colsToShift = colsToShift + cumsumCols + streakCols
        df, rollingSumCols = afe.getRollingSum(df, group, cols, 5)  
        colsToShift = colsToShift + rollingSumCols

        names = afe.createDivNames(group, cols, numMatchCol, '_ave')
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

    df = createColsBeforeSplit(df)
    df = afe.split(df, ['Player', 'Score', 'Win', 'Games_len', 'DiffGamesSum', 'FirstGameW', 'FirstTwoGamesW', 'FirstThreeGamesW', 'FirstGameL', 'FirstTwoGamesL', 'FirstThreeGamesL'], 
            ['id', 'datetime', 'toScore'])
    df = createStatsAfterSplit(df)
    k = copy

    df = afe.merge(df, k)
    df = afe.cleanup(df)
    return df

