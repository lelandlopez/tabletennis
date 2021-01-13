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
def dropAndFormat(df):
    df = afe.dropBadGames(df)
    df = afe.dropBadSequencer(df, 'datetime')
    df = afe.formatSequencer(df, 'datetime')
    return df



@helpers.printTime
def createColsBeforeSplit(df):
    df['lWin'] = np.where((df.lScore > df.rScore), True, False)
    df['rWin'] = np.where((df.lScore < df.rScore), False, True)

    df = afe.applyOnBoth(df, 
            ['Games', 'Games'],
            literal_eval)

    df = afe.applyOnBoth(df, 
            ['Games', 'Games'],
            lambda x: [int(i) for i in x])

    df['lDiffGames'] = df.apply(lambda x: np.subtract(x['lGames'], x['rGames']), axis=1)
    df['rDiffGames'] = df['lDiffGames'].apply(lambda x: x * -1)

    df = afe.applyOnBoth(df, 
            ['DiffGamesSum', 'DiffGames'],
            lambda x: sum(x))

    df = afe.applyOnBoth(df, 
            ['Games_len', 'Games'],
            len)

    df.loc[df['lScore'] >= df['rScore'], 'toScore'] = df['lScore']
    df.loc[df['lScore'] < df['rScore'], 'toScore'] = df['rScore']
    df['toScore'] = df['toScore'].astype(float)

    df = afe.applyOnBoth(df, 
            ['FirstGameW', 'DiffGames'],
            lambda x: x[0] > 0)
    return df

def createStatsAfterSplit(df):
    le = preprocessing.LabelEncoder()
    df['label'] = le.fit_transform(df.Player.values)
    df['other_label'] = le.fit_transform(df.otherPlayer.values)
    df['Score'] = df['Score'].astype('float')
    df['ScoretoScore'] = df['toScore']-df['Score']


    # groups = [['Player']]
    groups = [['Player'], ['Player', 'other_label']]
    # cols = ['Score']
    cols = ['Score', 'ScoretoScore', 'Win', 'Games_len']
    dividers = ['Games_len']
    # dividers = []
    sn = []

    for group in groups:
        colsToShift = []
        df, numMatchCol = afe.createNumMatch(df, group)
        gbf = df.sort_values(numMatchCol).groupby(group, as_index=False).filter(lambda x: len(x)> 1).groupby(group, as_index=False)

        # gbf = df.sort_values(numMatchCol).groupby(group, as_index=False)
        df, cumsumCols = afe.getCumsum(df, group, gbf, cols)
        colsToShift = colsToShift + cumsumCols

        df, rollingSumCols = afe.getRollingSum(df, group, gbf, cols, 5)  
        colsToShift = colsToShift + rollingSumCols

        names = afe.createDivNames(group, cols, numMatchCol, '_ave')
        colsToShift = colsToShift + names
        df[names] = df[cumsumCols].div(df[numMatchCol] + 1, axis=0)
        # df = afe.shift(df, names, df.sort_values(numMatchCol).groupby(group, as_index=False))
        for divider in dividers:
            n = afe.createDivNames(group, cols, divider, '_ave')
            div = afe.createNames(group)
            df[n] = df[cumsumCols].div(df[div + divider + '_cumsum'], axis=0)
            colsToShift = colsToShift + n


        df, shiftedNames = afe.shift(df, colsToShift, df.sort_values(numMatchCol).groupby(group, as_index=False))
        sn = sn + shiftedNames

        # df = afe.shiftBase(df, cols, group, df.sort_values(numMatchCol).groupby(group, as_index=False))
    df = df[sn + ['Player', 'id']]
    return df

def cleanup(df):
    k= [i for i in df.columns if 'num_match' in i and 'last' not in i ]
    df = df.drop(columns=k)
    # k =[i for i in df.columns if 'last' not in i and 'Player' not in i and i != 'id']
    # df = df.drop(columns=k)

    df = afe.calculateDiffs(df)
    return df

def formatter(df, save = False):
    copy = df.copy()
    sys.path.insert(1, './formatter/')

    df = dropAndFormat(df)
    df = createColsBeforeSplit(df)
    df = afe.split(df, ['Player', 'Score', 'Win', 'Games_len', 'DiffGamesSum'], ['id', 'datetime', 'toScore'])
    df = createStatsAfterSplit(df)
    k = copy
    df = afe.merge(df, k)
    df = cleanup(df)
    return df

