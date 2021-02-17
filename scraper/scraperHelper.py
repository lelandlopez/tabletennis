from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import time
import numpy as np
import multiprocessing
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score
import seaborn as sns
import signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
import psutil
from datetime import date
today = date.today()
sys.path.insert(1, '.')
from helpers import helpers

def killPROC(str):
    PROCNAME = str
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

def createDriver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    return driver

def quitDriver(driver):
    driver.quit()
    try:
        ffpid = int(driver.service.process.pid)
        os.kill(ffpid, signal.SIGTERM)
        killPROC("geckodriver")
        killPROC("firefox")
    except:
        print('error in quit Driver')


def fetchPageSource(url, **kwargs):
    driver = "" 
    if 'driver' in kwargs:
        driver = kwargs['driver']
    else:
        driver = createDriver()
    page_source = ""
    driver.get(url)
    try:
        if 'waitFor' in kwargs:
            if kwargs['waitFor'][0] == 'class':
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, kwargs['waitFor'][1]))
                )

        if 'executeScript' in kwargs:
            for i in kwargs['executeScript']:
                driver.execute_script(i)
        page_source = driver.page_source
        time.sleep(1)
    except TimeoutException:
        print("took too much time")
    except:
        print("error in fetchPageSource")
        pass
    finally:
        pass
        # try:
        #     ffpid = int(driver.service.process.pid)
        #     os.kill(ffpid, signal.SIGTERM)
        # except:
        #     pass
    return page_source, driver

def processPlayer(page_source, playerDF_filename, matchDF_filename):
    print('got in here')
    s = BeautifulSoup(str(page_source), 'html.parser')
    matches = s.select('.event__match')
    pDF = pd.read_csv(playerDF_filename, index_col = False)
    bDFCols = ['lPlayer', 'rPlayer', 'lScore', 'rScore', 'lGames', 'rGames', 'datetime', 'id']
    if 'matchDF.csv' not in os.listdir('./csv/static'):
        bDF = pd.DataFrame([], columns=bDFCols)
    else:
        bDF = pd.read_csv(matchDF_filename, index_col = False)
    for (index, match) in enumerate(matches):
        players = match.select('.event__participant')
        if len(players) > 0:
            id = match.get('id')[5:]
            if match.get('id')[5:] not in bDF.id.values:
                for player in players:
                    playerName = dropCountry(player.text)

                lScore = match.select('.event__score--home')
                rScore = match.select('.event__score--away')
                lGames = match.select('.event__part--home')
                rGames = match.select('.event__part--away')
                def rsToString(rs):
                    k = []
                    for i in rs:
                        k.append(i.text)
                    return k


                date = match.select('.event__time')
                if date[0].text[6:7] == ' ':
                    date = date[0].text[0:6] + str(today.year) + date[0].text[6:]
                row = np.array([dropCountry(players[0].text), dropCountry(players[1].text), lScore[0].text, rScore[0].text, rsToString(lGames), rsToString(rGames), date, match.get('id')[5:]], dtype='object')

                new = pd.DataFrame([row], columns=bDFCols)
                bDF = bDF.append(new)
            else:
                lScore = match.select('.event__score--home')
                rScore = match.select('.event__score--away')
                lGames = match.select('.event__part--home')
                rGames = match.select('.event__part--away')
                def rsToString(rs):
                    k = []
                    for i in rs:
                        k.append(i.text)
                    return k


                date = match.select('.event__time')
                if date[0].text[6:7] == ' ':
                    date = date[0].text[0:6] + str(today.year) + date[0].text[6:]
                row = np.array([lScore[0].text, rScore[0].text, rsToString(lGames), rsToString(rGames), date], dtype='object')
                bDF.loc[bDF['id'] == match.get('id')[5:], ['lScore', 'rScore', 'lGames', 'rGames', 'datetime']] = row
                # killPROC("geckodriver")
                # killPROC("firefox")
    # pDF.to_csv("./playerDFScrapeAgain.csv", index=False)
    bDF.to_csv(matchDF_filename, index=False)
    # killPROC("geckodriver")
    # killPROC("firefox")

def dropCountry(name):
    return name[:name.find('(')-1]

def check_exists_by_xpath(driver, xpath):
    try:
        x = driver.find_element_by_class_name(xpath)
    except NoSuchElementException:
        return False
    return True

def swap(df, cols, otherCols):
    def calculateArrs(cols, otherCols):
        k = []
        for i in otherCols:
            k = k + [i[0], i[1]]
        return k
    def flipArrs(cols, otherCols):
        k = []
        for i in otherCols:
            k = k + [i[1], i[0]]
        return k

    df.loc[df[cols[0]].str.strip() != df[cols[1]].str.strip(), 
            calculateArrs(cols, otherCols)] = df.loc[df[cols[0]] != df[cols[1]]][flipArrs(cols, otherCols)].values
    return df