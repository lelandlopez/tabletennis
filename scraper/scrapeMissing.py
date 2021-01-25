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
        # run firefox webdriver from executable path of your choice
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        # more_xpath = "event__more"
        # exists = check_exists_by_xpath(driver, more_xpath)
        # #live-table > div.event.event--results > div > div > a
        # if exists == False:
        #   time.sleep(5)
        # while(exists):
        #     try:
        #         driver.find_element_by_class_name(more_xpath).click()
        #     except:
        #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #         exists = check_exists_by_xpath(driver, more_xpath)

        # time.sleep(1)
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


def fetchPageSource(url):
    print('fetching page source:', url)
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    page_source = ""
    try:
        # run firefox webdriver from executable path of your choice
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.headless = True
        driver.get(url)
        page_source = driver.page_source
    except:
        pass
    finally:
        driver.close()
        driver.quit()
        try:
            ffpid = int(driver.service.process.pid)
            os.kill(ffpid, signal.SIGTERM)
        except:
            pass
    return page_source

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

def initial():
    url = "https://www.flashscore.com/darts/"
    page_source = fetchPageSource(url)
    processPlayer(page_source)


def processPlayer(df, page_source, id):
    print(id)
    s = BeautifulSoup(str(page_source), 'html.parser')

    status = s.select('.error')
    if len(status) > 0:
        bdf = pd.read_csv('./csv/static/matchDF.csv', index_col=False)
        bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'Error'
        bdf.to_csv('./csv/static/matchDF.csv', index=False)
    status = s.select('.status___XFO5ZlK')
    if len(status) > 0:
        bdf = pd.read_csv('./csv/static/matchDF.csv', index_col=False)
        bdf.loc[bdf['id'] == id, 'datetime'] = bdf['datetime'] + 'CA'
        bdf.to_csv('./csv/static/matchDF.csv', index=False)
    # if len(status) > 0:
    #     print('errer')

    # status = s.select('.noData___1Tt1d17')
    # if len(status) > 0:
    #     if status[0].text == 'No live score information available now, the match has not started yet.':
    #         return
    # scores = s.select('.score___cth2ReO')
    # print(scores[0].text)
    # print(scores[1].text)
    # def rsToString(rs):
    #     k = []
    #     for i in rs:
    #         k.append(i.text)
    #     return k
    # lGamesStructured = []
    # for i in range(1, 8):
    #     k = s.select('.part___1Pd43ek.home___2CzqfVu.part--' + str(i))
    #     if k[0].text != '':
    #         lGamesStructured.append(k[0].text)
    # rGamesStructured = []
    # for i in range(1, 8):
    #     k = s.select('.part___1Pd43ek.away___3Ys1r_C.part--' + str(i))
    #     if k[0].text != '':
    #         rGamesStructured.append(k[0].text)
    # date = s.select('.time___xAe_YNy')
    # bDF = pd.read_csv('./matchDF.csv')
    # row = [scores[0].text, scores[1].text, lGamesStructured, rGamesStructured, date[0].text]
    # bDF.loc[bDF['id'] == id, ['lScore', 'rScore', 'lGames', 'rGames', 'datetime']] = row
    # bDF.to_csv("./matchDF.csv", index=False)


def insertSpecific():
    df = pd.read_csv('./csv/static/matchDF.csv')
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
    for (index, i) in df.iterrows():
        url = 'https://www.flashscore.com/match/' + i['id'] + '/#match-summary'
        print(url)
        ps = getPlayer(url)
        processPlayer(df, ps, i['id'])
        break
        # print(index, df.shape[0])



insertSpecific()
