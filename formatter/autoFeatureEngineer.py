import pandas as pd
import time
from ast import literal_eval
import numpy as np
from sklearn import preprocessing
from multiprocessing import Pool
from functools import partial
from ast import literal_eval
from itertools import combinations
import time
import sys
sys.path.insert(1, './')
from helpers import helpers
from multiprocessing import Pool


class autoFeatureEngineer:

    def __init__(self, save = False):
        self.save = save
    
    def createWinColumns(self, df, pre, col):
        df['lWin'] = np.where((df.lScore > df.rScore), True, False)
        df['rWin'] = np.where((df.lScore < df.rScore), True, False)
        return df
    
    def createDiffColumns(self, df):
        df['lDiffGames'] = df.apply(lambda x: np.subtract(x['lGames'], x['rGames']), axis=1)
        df['rDiffGames'] = df['lDiffGames'].apply(lambda x: x * -1)
        return df


    def createDivNames(self, group, cols, divider, append='', prepend=''):
        k = []
        for col in cols:
            div = prepend
            for i in group:
                div = i + '_' + div
            div = div + col + '_' + divider + append
            k.append(div)
        return k

    def createNames(self, group, append='', prepend=''):
        div = prepend
        for i in group:
            div = i + '_' + div
        div = div + append
        return div

    def createNumMatch(self, df, group):
        div = self.createNames(group, 'num_match')
        df[div] = df.sort_values('datetime').groupby(group).cumcount()
        return df, div

    @helpers.printTime
    def shift(self, df, group, cols):
        numMatchName = self.createNames(group, 'num_match')
        df = df.sort_values(group + [numMatchName])
        names = ['last_' + i for i in cols]
        print(cols)
        df[names] = df.groupby(group)[cols].shift(1)
        df = df.drop(columns=cols)
        return df, ['last_' + i for i in cols]

    @helpers.printTime
    def getCumsum(self, df, group, cols):
        name = self.createNames(group)
        names = [name + i + '_cumsum' for i in cols]

        numMatchName = self.createNames(group, 'num_match')
        df = df.sort_values(group + [numMatchName])
        k = df.groupby(group)[cols].expanding().sum()
        k = k.reset_index(group, drop=True)
        k.columns = names
        df = pd.concat([df, k], axis=1)
        return df, names


    @helpers.printTime
    def getRollingSum(self, df, group, cols, num):
        name = self.createNames(group)
        names = [name + i + '_rolling_' + str(num) for i in cols]
        numMatchName = self.createNames(group, 'num_match')
        df = df.sort_values(group + [numMatchName])
        k = df.groupby(group)[cols].rolling(num).sum()
        k = k.reset_index(group, drop=True)
        k.columns = names
        df = pd.concat([df, k], axis=1)
        return df, names

    def formatSequencer(self, df, seq):
        df.loc[df[seq].str.contains(' ') == False, seq] = df[seq] + '0000'
        df.loc[df[seq].str.contains(' '), seq] = df[seq].str[0:6] + '2020' + df[seq].str[-5:]
        df[seq] = df[seq].str.replace('.', '')
        df[seq] = df[seq].str.replace(':', '')
        df[seq] = df[seq].str[4:8] + df[seq].str[2:4] + df[seq].str[0:2] + df[seq].str[8:]
        k = df[df[seq].str.contains(' ')][[seq]]
        df[seq] = df[seq].astype(int)
        return df

    def dropBadSequencer(self, df, sequencer):
        k = df.shape[0]
        df = df[df[sequencer].str.contains('WO') == False]
        df = df[df[sequencer].str.contains('Awrd') == False]
        df = df[df[sequencer].str.contains('Abn') == False]
        df = df[df[sequencer].str.contains('FRO') == False]
        df = df[df[sequencer].str.contains('Canc') == False]
        df = df[df[sequencer].str.contains('CA') == False]
        df = df[df[sequencer].str.contains('Error') == False]
        print(f'dropped dropBadSequencer :', k-df.shape[0])
        return df

    def subtractArrFromArr(self, df, cols, resultingCol):
        difference = []
        zipOb = zip(df[cols[0]], df[cols[1]])
        for list1_i, list2_i in zipOb:
            difference.append(np.array(list1_i, dtype='object') - np.array(list2_i, dtype='object'))
        df[resultingCol] = difference
        return df

    def applyOnBoth(self, df, base, func):
        for i in ['l', 'r']:
            df[i + base[0]] = df[i + base[1]].apply(func)
        return df

    def split(self, df, stats, extraStats):
        def processSubject(df, stats, extraStats):
            k = pd.DataFrame()
            p = pd.DataFrame()
            for i in stats:
                p[i] = df['l' + i]
            for i in extraStats:
                p[i] = df[i]
            p['otherPlayer'] = df['rPlayer']
            k = k.append(p)
            for i in stats:
                p[i] = df['r' + i]
            for i in extraStats:
                p[i] = df[i]
            p['otherPlayer'] = df['lPlayer']
            k = k.append(p).reset_index(0, drop=True)
            print(k)
            return k


        df = processSubject(df, stats, extraStats)
        if self.save == True:
            print('saving to afterSplit')
            df.to_csv('./csv/afterSplit.csv', index=False)
        return df

    @helpers.printTime
    def dropBadGames(self, df, ignore_ids):
        df = df[(df['lGames'].str.len() > 2) | (df['id'].isin(ignore_ids))]
        return df

    def merge(self, l, df):
        if self.save == True:
            print('saving to beforeMerge')
            l.to_csv('./csv/beforeMerge.csv', index=False)
        df = df[['lPlayer', 'rPlayer', 'id']].copy()
        df['mergeCol'] = df['lPlayer'].astype(str) + df['id']
        l['mergeCol'] = l['Player'].astype(str) + l['id']
        k = l.drop(columns=['id'])
        df = df.merge(k, on='mergeCol', how='inner')
        df['mergeCol'] = df['rPlayer'].astype(str) + df['id']
        l['mergeCol'] = l['Player'].astype(str) + l['id']
        k = l.drop(columns=['id'])
        df = df.merge(k, on='mergeCol', suffixes=['_left', '_right'], how='inner')
        df = df.drop(columns=['mergeCol', 'lPlayer', 'rPlayer'])
        return df

    def calculateDiffs(self, df):
        lefts = [i for i in df.columns if 'left' in i and 'last' in i]
        for left in lefts:
            bare = left[:len('_left') * -1]
            diff = bare + '_diff'
            right = bare + '_right'
            df[diff] = df[left] - df[right]
        return df


    def cleanup(self, df):
        k= [i for i in df.columns if 'num_match' in i and 'last' not in i ]
        df = df.drop(columns=k)
        k =[i for i in df.columns if 'last' not in i and 'Player' not in i and i != 'id']
        df = df.drop(columns=k)

        df = self.calculateDiffs(df)
        return df

    @helpers.printTime
    def createWinStreaks(self, df, group, cols):
        name = self.createNames(group)
        names = [name + i + '_streak' for i in cols]

        numMatchName = self.createNames(group, 'num_match')
        df = df.sort_values(group + [numMatchName])
        def f(df):
            df = df.sort_values('datetime')
            return df['Win'].groupby((df['Win'] != df['Win'].shift()).cumsum()).cumcount()
        df[names[0]] = df.groupby(group).apply(f).reset_index(group, drop=True)
        return df, names

    @helpers.printTime
    def findWinGame_X(self, df, col, game_num):
        name = col + '_win_game_' + str(game_num)
        def f(x):
            return x[game_num] > 0
        df[name] = df[col].apply(f)
        return df, [name]