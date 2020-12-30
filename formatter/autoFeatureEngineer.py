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
sys.path.insert(1, '..')
from helpers import helpers
from multiprocessing import Pool

def t(gbf, lf):
    return gbf.transform(lf[0])

def LECols(df, cols):
    k = []
    for i in cols:
        k = k + list(df[i].unique())
    le = preprocessing.LabelEncoder()
    le.fit(seq)
    for i in cols:
        df[i] = le.transform(df[i])
    return df

def changeDType(df, col, type):
    df[col] = df[col].astype(type)
    return df

def strArrToIntArr(arr):
    return list(map(int, arr))

def numCloseGamesL(series):
    return len([x for x in series if (x < 0) & (x >= -2)])

def numCloseGamesW(series):
    return len([x for x in series if (x > 0) & (x <= 2)])

def numCloseGames(series):
    return len([x for x in series if (x <= 2) & (x >= -2)])

def numBlowouts(series):
    return len([x for x in series if x == 0])

def flattenList(l):
    return [item for sublist in l for item in sublist]


class autoFeatureEngineer:
    def __init__(self, save = False):
        self.save = save


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
    def shift(self, df, cols, gbf):
        df[['last_' + i for i in cols]] = gbf[cols].shift(1)
        df = df.drop(columns=cols)
        return df, ['last_' + i for i in cols]

    @helpers.printTime
    def shiftBase(self, df, cols, group, gbf):
        name = self.createNames(group) 
        names = ['last_' + name + i for i in cols]
        df[names] = gbf[cols].shift(1)
        return df

    @helpers.printTime
    def getCumsum(self, df, group, gbf, cols):
        name = self.createNames(group)
        names = [name + i + '_cumsum' for i in cols]
        df[names] = gbf[cols].expanding().sum().reset_index(0, drop=True)
        return df, names


    def getRollingSum(self, df, group, gbf, cols, num):
        name = self.createNames(group)
        names = [name + i + '_rolling_' + str(num) for i in cols]
        # print(names)
        # print(cols)
        # print(gbf[cols].rolling(num).sum().reset_index(0, drop=True).reset_index(0, drop=True))
        df[names] = gbf[cols].rolling(num).sum().reset_index(0, drop=True).reset_index(0, drop=True)
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
        print(f'dropped dropBadSequencer :', k-df.shape[0])
        return df

    def subtractArrFromArr(self, df, cols, resultingCol):
        difference = []
        zipOb = zip(df[cols[0]], df[cols[1]])
        for list1_i, list2_i in zipOb:
            difference.append(np.array(list1_i, dtype='object') - np.array(list2_i, dtype='object'))
        df[resultingCol] = difference
        return df
    def changeDType(self, df, col, type, paired = True):
        if paired:
            df[col + '_left'] = df[col + '_left'].astype(type)
            df[col + '_right'] = df[col + '_right'].astype(type)
        else:
            df[col] = df[col].astype(type)
        return df

    def cleanData(self):
        def clean():
            def dropDuplicateIds():
                k = self.df.shape[0]
                self.df = self.df.drop_duplicates(subset=self.id[0])
                print(f'dropped duplicate id:', k-self.df.shape[0])

            def dropSubjectVSubject():
                k = self.df.shape[0]
                l = self.df[self.df[self.subjects[0]] == self.df[self.subjects[1]]]
                for i in l[self.subjects[0]].unique():
                    self.df = self.df[self.df[self.subjects[0]] != i]
                    self.df = self.df[self.df[self.subjects[1]] != i]
                print(f'dropped SubjectVSubject :', k-self.df.shape[0])

            def dropBadSubjectScore():
                k = self.df.shape[0]
                self.df = self.df[self.df[self.subjectScore[0]].str.isnumeric()]
                self.df = self.df[self.df[self.subjectScore[1]].str.isnumeric()]
                print(f'dropped dropBadSubjectScore :', k-self.df.shape[0])

            dropDuplicateIds()
            dropSubjectVSubject()
            dropBadSubjectScore()
            dropBadSequencer()
            print(f'total remaining rows: ', self.df.shape[0])
            return self

        def format():
            def formatSequencer():
                k = self.sequencer[0]
                self.df.loc[self.df[k].str.contains(' ') == False, k] = self.df[k] + '0000'
                self.df.loc[self.df[k].str.contains(' '), k] = self.df[k].str[0:6] + '2020' + self.df[k].str[7:]
                self.df[k] = self.df[k].str.replace('.', '')
                self.df[k] = self.df[k].str.replace(':', '')
                self.df[k] = self.df[k].str[4:8] + self.df[k].str[2:4] + self.df[k].str[0:2] + self.df[k].str[8:]
                self.df[k] = self.df[k].astype(int)
            def formatSubjects():
                self.df = LECols(self.df, self.subjects)
            #
            def formatStringArrays():
                for i in flattenList(self.arrStr):
                    self.df[i] = self.df[i].apply(literal_eval).apply(strArrToIntArr)
            # def formatSubjectScore():
            #     self.df = changeDType(self.df, self.subjectScore[0], int)
            #     self.df = changeDType(self.df, self.subjectScore[1], int)

            formatSequencer()
            # formatSubjects()
            # formatSubjectScore()
            formatStringArrays()

        clean()
        format()

    def getCloseGames(self, df, col, resulting):
        if resulting == 'numCloseGamesL':
            func = numCloseGamesL
        elif resulting == 'numCloseGamesW':
            func = numCloseGamesW
        elif resulting == 'numCloseGames':
            func = numCloseGames
        elif resulting == 'numBlowouts':
            func = numCloseGames
        else:
            print("function not recognized")
            return
        df['l' + resulting] = df['l' + col].apply(func)
        df['r' + resulting] = df['r' + col].apply(func)
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
            k = k.append(p)
            return k


        df = processSubject(df, stats, extraStats).reset_index()
        if self.save == True:
            print('saving to afterSplit')
            df.to_csv('./csv/afterSplit.csv', index=False)
        return df


    def dropVariance():
        k = self.df.shape[1]
        self.df = self.df.replace([np.inf, -np.inf], np.nan)
        self.df = self.df.fillna(0)
        self.df = self.df.drop(columns='datetime')

        from sklearn.feature_selection import VarianceThreshold
        sel = VarianceThreshold()
        def variance_threshold_selector(data, threshold=0):
            selector = VarianceThreshold(threshold)
            selector.fit(data)
            return data[data.columns[selector.get_support(indices=True)]]
        id = self.df.id
        self.df = variance_threshold_selector(self.df.drop(columns=['id']))
        self.df['id'] = id
        print('variance dropped: ', self.df.shape[1])

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
