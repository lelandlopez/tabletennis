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
from scraperHelper import fetchPageSource, swap, createDriver, doSomethingFetchPageSource
from scraperHelper import getLargestInGroup, filterOnlyNew, americanToImplied
sys.path.insert(1, '.')
from formatter import formatter
sys.path.insert(1, './evaluation/')
from evaluate import predict, prep


def scrapeBets():
    matchDF_filename = './csv/static/matchDF.csv'
    test = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test = True
        else:
            url = sys.argv[1]
            search_regex = '.offering-games__table-row'
            time_regex = '.offering-games__link'

    def processGamesPlaying(driver):
        url = 'https://www.flashscore.com/table-tennis/'
        def doSomething(driver):
            button = driver.find_element_by_xpath('//*[@id="live-table"]/div[1]/div/div[2]/div[1]')
            button.click()
        page_source, driver = doSomethingFetchPageSource(url, driver=driver, doSomething=[doSomething])
        text_file = open("./temp/gamesPlaying.txt", "w")
        text_file.write(page_source)
        text_file.close()

        search_regex = '.event__participant'
        s = BeautifulSoup(str(page_source), 'html.parser')
        players = s.select(search_regex)
        k = []
        for (index, player) in enumerate(players):
            p = player.text
            p = p[:p.find('(')].strip()
            k.append(p)
        return k

    cols = ['time', 'lTeam', 'rTeam', 'lLine', 'rLine', 'link']

    def processBetOnline(driver):
        url = 'https://beta.betonline.ag/sportsbook/table-tennis/todaygames'
        base = 'https://beta.betonline.ag'
        page_source = fetchPS(url, test, driver)

        text_file = open("./temp/betonline.txt", "w")
        text_file.write(page_source)
        text_file.close()

        def formatTeamNames(teams):
            def formatSide(side):
                end = side.find(',')
                return (side[: end] + ' ' + side[end + 2: end + 3] + '.').strip()
            return [formatSide(teams[0].text), formatSide(teams[1].text)]
        s = BeautifulSoup(str(page_source), 'html.parser')
        df = pd.DataFrame([], columns=cols)
        search_regex = '.offering-today-games__table-row'
        time_regex = '.offering-today-games__link'
        matches = s.select(search_regex)
        for (index, match) in enumerate(matches):
            teams = match.select('.lines-row__team-name')
            lines = match.select('.lines-row__money')
            time = match.select(time_regex)
            teams = formatTeamNames(teams)
            link = base + time[0].get('href')
            k = pd.DataFrame([[time[0].text, teams[0], teams[1], lines[0].text.strip('()'), lines[1].text.strip('()'), link]], columns=cols)
            df = df.append(k)
        df['platform'] = url
        return df.reset_index(0, drop=True)

    def processBovada(driver):
        url = 'https://www.bovada.lv/sports/table-tennis' 
        base = 'https://www.bovada.lv'
        page_source = fetchPS(url, test, driver, waitFor=['class', 'grouped-events'])
        text_file = open("./temp/bovada_ps.txt", "w")
        text_file.write(page_source)
        text_file.close()
        def formatLines(lines):

            def formatLine(line):
                l = line.strip()
                if l == 'EVEN':
                    return '+100'
                return l
            if len(lines) > 2:
                return [formatLine(lines[2].text), formatLine(lines[3].text)]
            return [formatLine(lines[0].text), formatLine(lines[1].text)]

        def formatTeamNames(teams):
            def formatSide(side):
                end = side.find(',')
                if end == -1:
                    end = side.find(' ')
                    return (side[end:] + ' ' + side[0:1] + '.').strip()
                return (side[:end] + ' ' + side[end+2:end+3] + '.').strip()
            return [formatSide(teams[0].text), formatSide(teams[1].text)]
        def formatTime(time):
            text = time[0].text
            e = text.find(' ', 2)
            return text[e + 1:]
        s = BeautifulSoup(str(page_source), 'html.parser')
        df = pd.DataFrame([], columns=cols)
        search_regex = '.coupon-content.more-info'
        time_regex = '.period'
        s = s.select('.next-events-bucket')
        if len(s) == 0:
            return df
        s = s[0]
        matches = s.select(search_regex)
        for (index, match) in enumerate(matches):
            teams = match.select('.competitor-name')
            link = match.select('.game-view-cta')
            link = link[0].find_all('a', href=True)[0].get('href')
            link = base + link
            lines = match.select('.bet-price')
            time = match.select(time_regex)
            lines = formatLines(lines)
            teams = formatTeamNames(teams)
            time = formatTime(time)
            k = pd.DataFrame([[time, teams[0], teams[1], lines[0].strip('()'), lines[1].strip('()'), link]], columns=cols)
            df = df.append(k)
        df['platform'] = url
        return df.reset_index(0, drop=True)

    def findCorresponding(df, l, r):
        # print(l, r)
        today = date.today()
        d = today.strftime("%d.%m")
        k = df.loc[((df['lPlayer'] == r.strip()) & (df['rPlayer'] == l.strip())) | ((df['lPlayer'] == l.strip()) & (df['rPlayer'] == r.strip()))]
        return k
                

    def getCorrespondingGames(df):
        gameDF = pd.read_csv(matchDF_filename)
        gameDF = gameDF.loc[gameDF['lScore'] == '-']
        d = pd.DataFrame()
        o = pd.DataFrame()
        for index, i in df.iterrows():
            k = findCorresponding(gameDF, i['lTeam'], i['rTeam'])
            if k.shape[0] != 0:
                d = d.append(k.iloc[0])
                i['merge_index'] = k.id.values[0]
                o = o.append(i)
        return d, o


    def fetchPS(url, test, driver, **kwargs):
        ps = ''
        if test == False:
            if 'waitFor' in kwargs:
                ps, driver = fetchPageSource(url, waitFor=kwargs['waitFor'], driver=driver)
            else:
                ps, driver = fetchPageSource(url, driver=driver)
            text_file = open("./Debug/ps.txt", "w")
            text_file.write(ps)
            text_file.close()
        else:
            file = open('./Debug/ps.txt', 'r')
            ps = file.read()
            file.close()
        return ps





    driver = createDriver()
    gamesPlaying = processGamesPlaying(driver)
    k = processBetOnline(driver)
    l = processBovada(driver)
    k.to_csv('./temp/betOnline.csv')
    l.to_csv('./temp/bovada.csv')
    bettingSitesDF = [k, l]
    df = pd.concat(bettingSitesDF)

    def formatLines(df):
        df.loc[df['rTeam'].str.strip() > df['lTeam'].str.strip(), 
                ['lTeam', 'rTeam', 'lLine', 'rLine']] = df.loc[df['rTeam'].str.strip() > df['lTeam'].str.strip()][['rTeam', 'lTeam', 'rLine', 'lLine']].values
        df = df.sort_values('time')
        df.to_csv('./temp/combined.csv')
        return df
        

    df.to_csv('./temp/bettingSitesDF.csv')
    df = formatLines(df).reset_index()
    cdf, cbdf = getCorrespondingGames(df)
    print(cdf.to_csv('./temp/cdf.csv'))
    print(cbdf.to_csv('./temp/cbdf.csv'))

    ul = set(list(cdf['lPlayer'].unique()) + list(cdf['rPlayer'].unique()))
    mdf = pd.read_csv(matchDF_filename)
    udf = mdf[(mdf['lPlayer'].isin(ul)) | (mdf['rPlayer'].isin(ul))]


    udf.to_csv('./test_before.csv')
    formatted = formatter(udf, True, ignore_ids = cdf['id'])

    formatted = formatted[formatted['id'].isin(cdf['id'])]
    formatted = formatted.merge(mdf, on ='id')

    def formatSequencer(df, seq):
        df.loc[df[seq].str.contains(' ') == False, seq] = df[seq] + '0000'
        df.loc[df[seq].str.contains(' '), seq] = df[seq].str[0:6] + '2020' + df[seq].str[-5:]
        df[seq] = df[seq].str.replace('.', '')
        df[seq] = df[seq].str.replace(':', '')
        df[seq] = df[seq].str[4:8] + df[seq].str[2:4] + df[seq].str[0:2] + df[seq].str[8:]
        k = df[df[seq].str.contains(' ')][[seq]]
        df[seq] = df[seq].astype(int)
        return df

    formatted = formatSequencer(formatted, 'datetime')
    formatted.to_csv('./temp/merged.csv')
    
    predictions = predict(formatted)
    formatted['predictions'] = predictions.tolist()
    formatted['rWinPred'] = formatted['predictions'].apply(lambda x: x[0])
    formatted['lWinPred'] = formatted['predictions'].apply(lambda x: x[1])

    formatted = formatted.merge(cbdf, left_on='id', right_on='merge_index')

    formatted.to_csv('./temp/formatted.csv')



    formatted = formatted[formatted['lLine'] != '']
    formatted = formatted[formatted['rLine'] != '']


    formatted = swap(formatted, ['lTeam', 'Player_left'], [['lTeam', 'rTeam'], ['lLine', 'rLine']])

    formatted['lOdds'] = formatted['lLine'].astype(int).apply(americanToImplied)
    formatted['rOdds'] = formatted['rLine'].astype(int).apply(americanToImplied)


    formatted['ledge'] = round(formatted['lWinPred'] - formatted['lOdds'], 4)
    formatted['redge'] = round(formatted['rWinPred'] - formatted['rOdds'], 4)

    formatted['lOdds'] = round(formatted['lOdds'], 4)
    formatted['rOdds'] = round(formatted['rOdds'], 4)

    formatted['lWinPred'] = round(formatted['lWinPred'], 4)
    formatted['rWinPred'] = round(formatted['rWinPred'], 4)




    formatted = formatted.sort_values('datetime')
    formatted = getLargestInGroup(formatted, ['id'], 'ledge', 'redge')
    formatted = formatted.sort_values('datetime')
    formatted = filterOnlyNew(formatted, gamesPlaying, 'datetime')
    formatted = formatted.sort_values('datetime')

    cols = ['datetime', 'id', 'lTeam', 'rTeam', 'Player_left', 'Player_right', 'lWinPred', 'rWinPred', 'lOdds', 'rOdds', 'lLine', 'rLine', 'ledge', 'redge', 'platform', 'link']
    formatted[cols].to_csv('./predictions.csv')
    print("done")


