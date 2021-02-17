from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time
import numpy as np
import re
import multiprocessing
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
import seaborn as sns
import signal
# import libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import psutil
from datetime import date

sys.path.insert(1, './')
from helpers import helpers

sys.path.insert(1, './scraper/')
from scraperHelper import fetchPageSource 
from scraperHelper import swap 
from scraperHelper import createDriver
from scraperHelper import quitDriver
today = date.today()


def check_exists_by_xpath(driver, xpath):
    try:
        x = driver.find_element_by_class_name(xpath)
    except NoSuchElementException:
        return False
    return True

def killPROC(str):
    PROCNAME = str
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()


def getPlayer(url):

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        results = driver.page_source
    except:
        pass
    finally:
        try:
            ffpid = int(driver.service.process.pid)
            os.kill(ffpid, signal.SIGTERM)
            killPROC("geckodriver")
            killPROC("firefox")
        except:
            pass
    return results


# def fetchPageSource(url):
#     print('fetching page source:', url)
#     from selenium.webdriver.firefox.options import Options
#     options = Options()
#     options.headless = True
#     driver = webdriver.Firefox(options=options)
#     page_source = ""
#     try:
#         # run firefox webdriver from executable path of your choice
#         from selenium.webdriver.firefox.options import Options
#         options = Options()
#         options.headless = True
#         driver.get(url)
#         page_source = driver.page_source
#     except:
#         pass
#     finally:
#         driver.close()
#         driver.quit()
#         try:
#             ffpid = int(driver.service.process.pid)
#             os.kill(ffpid, signal.SIGTERM)
#         except:
#             pass
#     return page_source

def getPlayers(page_source):
    players = []
    s = BeautifulSoup(str(page_source), 'html.parser')
    l = s.select('.participant-imglink')
    for p in l:
        if p.text != "":
            k = p.get('onclick')
            first = k.find("'")
            players.append([k[first+1 : k.find("'", first+2)], p.text])
    return players


def dropCountry(name):
    return name[:name.find('(')-1]

def seperateDateTime(date):
    return name[:name.find('(')-1]


def processPlayer(df, page_source, id):
    print(id)
    s = BeautifulSoup(str(page_source), 'html.parser')

    status = s.select('.error')
    if len(status) > 0:
        bdf = pd.read_csv(matchDF_filename, index_col=False)
        bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'Error'
        bdf.to_csv(matchDF_filename, index=False)
        return
    status = s.select('.status___XFO5ZlK')
    print(status)
    if len(status) > 0:
        print('got in here')
        if status[0].text == 'Cancelled':
            bdf = pd.read_csv(matchDF_filename, index_col=False)
            bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'CA'
            bdf.to_csv(matchDF_filename, index=False)
            return
        if status[0].text == 'Walkover':
            bdf = pd.read_csv(matchDF_filename, index_col=False)
            bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'WO'
            bdf.to_csv(matchDF_filename, index=False)
            return
        if status[0].text == 'Awarded':
            bdf = pd.read_csv(matchDF_filename, index_col=False)
            bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'AW'
            bdf.to_csv(matchDF_filename, index=False)
            return
        if 'FRO' in status[0].text:
            return
        if status[0].text.strip() == '':
            return

    status = s.select('.noData___1Tt1d17')
    if len(status) > 0:
        if status[0].text == 'No live score information available now, the match has not started yet.':
            return
    scores = s.select('.score___3_4DOfL')
    def rsToString(rs):
        k = []
        for i in rs:
            k.append(i.text)
        return k
    lGames = []
    rGames = []
    for i in range(1, 8):
        k = s.select('.part___PWW-lip.home___2hIlHif.part--' + str(i))
        if len(k) == 0:
            break
        if k[0].text == "":
            break
        lGames.append(k[0].text)
        k = s.select('.part___PWW-lip.away___2Q2jzQu.part--' + str(i))
        rGames.append(k[0].text)
    # if k[0].text != '':
    #     lGamesStructured.append(k[0].text)
    # rGamesStructured = []
    # for i in range(1, 8):
    #     k = s.select('.away___2Q2jzQu.part--' + str(i))
    #     if k[0].text != '':
    #         rGamesStructured.append(k[0].text)
    date = s.select('.time___22qYh_R ')
    bDF = pd.read_csv(matchDF_filename)
    row = [scores[0].text, scores[1].text, lGames, rGames, date[0].text]
    row = np.array(row, dtype="object")
    bDF.loc[bDF['id'] == id, ['lScore', 'rScore', 'lGames', 'rGames', 'datetime']] = row
    bDF.to_csv(matchDF_filename, index=False)


def insertSpecific():
    df = pd.read_csv(matchDF_filename)
    print(df.shape)
    df = df[df['lScore'] == '-']

    lc = 'abcdefghijklmnopqrstuvwxyz'  
    uc = lc.upper()
    k = lc + uc
    p = ""
    for i in k:
        p = p + i + '|'
    p = p.strip('|')
    df = df[df['datetime'].str.contains(p) == False]

    print(df.shape)
    print(df.head())
    print(df['datetime'].str.len().unique())
    driver = createDriver()
    for (index, i) in df.iterrows():
        url = 'https://www.flashscore.com/match/' + i['id'] + '/#match-summary'
        print(url)
        try:
            ps, driver = fetchPageSource(url, 
                    driver=driver, executeScript=["window.scrollTo(0, document.body.scrollHeight);"])
        except:
            quitDriver(driver)
        processPlayer(df, ps, i['id'])




matchDF_filename = './csv/static/matchDF.csv'
insertSpecific()
