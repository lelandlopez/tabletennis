
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
# np.warnings.filterwarnings('error', category=np.VisibleDeprecationWarning) 
# import libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import psutil
from datetime import date
today = date.today()
sys.path.insert(1, '.')
from helpers import helpers


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
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        results = driver.page_source
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
    return results


def fetchPageSource(url):
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

matchDF_filename = './csv/static/matchDF.csv'
playerDF_filename = './csv/static/playerDF.csv'


def processPlayer(page_source):
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
                row = np.array([dropCountry(players[0].text), dropCountry(players[1].text), lScore[0].text, rScore[0].text, rsToString(lGames), rsToString(rGames), date[0].text, match.get('id')[5:]], dtype='object')

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
                row = np.array([lScore[0].text, rScore[0].text, rsToString(lGames), rsToString(rGames), date[0].text], dtype='object')
                bDF.loc[bDF['id'] == match.get('id')[5:], ['lScore', 'rScore', 'lGames', 'rGames', 'datetime']] = row
                # killPROC("geckodriver")
                # killPROC("firefox")
    # pDF.to_csv("./playerDFScrapeAgain.csv", index=False)
    bDF.to_csv(matchDF_filename, index=False)
    killPROC("geckodriver")
    killPROC("firefox")

def getTournaments(page_source):
    s = BeautifulSoup(str(page_source), 'html.parser')
    ks = s.select('#mt')
    links = []
    for k in ks:
        tags = k.find_all('a')
 
        for tag in tags:
            links.append(tag.get('href'))
    print(links)
    return ['https://www.flashscore.com' + i for i in links if "/" in i]



frontPage_url = 'https://www.flashscore.com/table-tennis/'

@helpers.printTime
def insertSpecific(results, fixtures, url = ""):
    if url == "":
        ps = fetchPageSource(frontPage_url)
        print(time.asctime( time.localtime(time.time())))
        urls = getTournaments(ps)
    else:
        urls = [url]
    for i in urls:
        print(i)
        if results == True:
            k = i + 'results'
            print(k)
            ps = fetchPageSource(i + 'results')
            processPlayer(ps)


        if fixtures == True:
            k = i + 'fixtures'
            print(k)
            ps = fetchPageSource(i + 'fixtures')
            processPlayer(ps)


lenargs = len(sys.argv)
if lenargs == 2:
    insertSpecific(True, True, sys.argv[1])
else:
    insertSpecific(True, True)
