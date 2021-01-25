from bs4 import BeautifulSoup
import pandas as pd
import os, sys, time, csv
import numpy as np
# import libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from datetime import date

sys.path.insert(1, './scraper/')
from helper import fetchPageSource 
sys.path.insert(1, '.')
from formatter import formatter
sys.path.insert(1, './evaluation/')
from evaluate import predict, prep


matchDF_filename = './csv/static/matchDF.csv'
test = False
url = 'https://beta.betonline.ag/sportsbook/table-tennis/todaygames'
search_regex = '.offering-today-games__table'
time_regex = '.offering-today-games__link'
if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        test = True
    else:
        url = sys.argv[1]
        search_regex = '.offering-games__table-row'
        time_regex = '.offering-games__link'




def processBetOnline(page_source):
    s = BeautifulSoup(str(page_source), 'html.parser')
    cols = ['time', 'lTeam', 'rTeam', 'lLine', 'rLine']
    df = pd.DataFrame([], columns=cols)
    matches = s.select(search_regex)
    for (index, match) in enumerate(matches):
        teams = match.select('.lines-row__team-name')
        lines = match.select('.lines-row__money')
        time = match.select(time_regex)
        k = pd.DataFrame([[time[0].text, teams[0].text, teams[1].text, lines[0].text, lines[1].text]], columns=cols)
        df = df.append(k)
    return df.reset_index(0, drop=True)

def formatName(str):
    k = str.split(',')
    return (k[0] + k[1][0:2] + '.').strip()

def findCorresponding(df, l, r):
    today = date.today()
    d = today.strftime("%d.%m")
    k = df.loc[((df['lPlayer'].str.startswith(l[:-1])) | (df['rPlayer'].str.startswith(l[:-1]))) & ((df['lPlayer'].str.startswith(r[0:-1])) | (df['rPlayer'].str.startswith(r[:-1]))) & (df['datetime'].str[0:5] == d)]
    return k
            

def getCorrespondingGames(df):
    gameDF = pd.read_csv(matchDF_filename)
    gameDF = gameDF.loc[gameDF['lScore'] == '-']
    d = pd.DataFrame()
    o = pd.DataFrame()
    for index, i in df.iterrows():
        k = findCorresponding(gameDF, formatName(i['lTeam']), formatName(i['rTeam']))
        if k.shape[0] != 0:
            d = d.append(k.iloc[0])
            i['merge_index'] = k.id.values[0]
            o = o.append(i)
    return d, o

def americanToImplied(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        odds = odds * -1
        return odds / (odds + 100)


if test == False:
    ps = fetchPageSource(url)
    text_file = open("./Debug/ps.txt", "w")
    text_file.write(ps)
    text_file.close()
else:
    file = open('./Debug/ps.txt', 'r')
    ps = file.read()
    file.close()

df = processBetOnline(ps)
cdf, cbdf = getCorrespondingGames(df)


print(cdf)
ul = set(list(cdf['lPlayer'].unique()) + list(cdf['rPlayer'].unique()))
mdf = pd.read_csv(matchDF_filename)
today = date.today()
mdf.loc[(mdf['datetime'].str[0:5] == today.strftime("%d.%m")) & (mdf['lScore'] == '-'), ['lScore', 'rScore']] = ['0', '0']
udf = mdf
udf = mdf[(mdf['lPlayer'].isin(ul)) | (mdf['rPlayer'].isin(ul))]
udf.to_csv('./test_before.csv')
formatted = formatter(udf, True, ignore_ids = cdf['id'])

formatted = formatted[formatted['id'].isin(cdf['id'])]
formatted.to_csv('./test.csv')
predictions = predict(formatted)
formatted['predictions'] = predictions.tolist()
formatted['rWinPred'] = formatted['predictions'].apply(lambda x: x[0])
formatted['lWinPred'] = formatted['predictions'].apply(lambda x: x[1])

formatted = formatted.merge(cbdf, left_on='id', right_on='merge_index')


formatted = formatted[formatted['lLine'] != '']
formatted = formatted[formatted['rLine'] != '']


def switchLR(formatted):
    k = formatted['lLine'].copy()
    formatted['lLine'] = formatted['rLine'].copy()
    formatted['rLine'] = k
    return formatted

for index, i in formatted.iterrows():
    k = [i['lTeam'], i['lLine']]
    formatted.loc[index, ['lTeam', 'lLine']] = [i['rTeam'], i['rLine']]
    formatted.loc[index, ['rTeam', 'rLine']] = k

formatted['lOdds'] = formatted['lLine'].astype(int).apply(americanToImplied)
formatted['rOdds'] = formatted['rLine'].astype(int).apply(americanToImplied)


formatted['ledge'] = formatted['lWinPred'] - formatted['lOdds']
formatted['redge'] = formatted['rWinPred'] - formatted['rOdds']

def toMilitary(time):
    if 'AM' in time:
        time = time[:-3]
        time = time.replace(':', '')
        time = int(time)
        if (time < 1300 and time >= 1200) == True:
            return time + 1200
        return time
    else:
        time = time[:-3]
        time = time.replace(':', '')
        time = int(time)
        if (time < 1300 and time >= 1200) == False:
            return time + 1200
        return time

formatted['time'] = formatted['time'].apply(toMilitary)

formatted = formatted.sort_values('time')


print(formatted[['time', 'id', 'Player_left', 'Player_right', 'lTeam', 'rTeam', 'lWinPred', 'rWinPred', 'lOdds', 'rOdds', 'lLine', 'rLine', 'ledge', 'redge']])
formatted[['time', 'id', 'Player_left', 'Player_right', 'lTeam', 'rTeam', 'lWinPred', 'rWinPred', 'lOdds', 'rOdds', 'lLine', 'rLine', 'ledge', 'redge']].to_csv('./predictions.csv')
# print(formatted[['Player_left', 'Player_right'] + [i for i in formatted.columns if 'cumsum' in i]])
# print(cbdf)


