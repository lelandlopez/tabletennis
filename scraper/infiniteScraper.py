
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
# import libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import psutil

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
        more_xpath = "event__more"
        exists = check_exists_by_xpath(driver, more_xpath)
        #live-table > div.event.event--results > div > div > a
        if exists == False:
          time.sleep(5)
        while(exists):
            try:
                driver.find_element_by_class_name(more_xpath).click()
            except:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                exists = check_exists_by_xpath(driver, more_xpath)

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
    l = s.select('.participantName___1pLLLzn')
    for p in l:
        if p.text != "":
            k = p.find_all(href=True)
            if len(k) > 0:
                players.append([k[0].text, k[0]['href']])
    return players


def dropCountry(name):
    return name[:name.find('(')-1]

def seperateDateTime(date):
    return name[:name.find('(')-1]

def initial():
    if 'playerDF.csv' not in os.listdir('./'):
        playerDF = pd.DataFrame([['Mishakin V.', '/player/mishakin-vladimir/IZRAHYmS',   False]], columns=['name', 'url', 'scraped'])
        playerDF.to_csv('./playerDF.csv', index=False)
        print('no PlayerDF')
    else:
        playerDF = pd.read_csv('./playerDF.csv', index_col = False)
        print('found PlayerDF')
    playerDF = playerDF[playerDF['scraped'] == False]
    print(playerDF.shape)
    for (index, p) in playerDF.iterrows():
        url = 'https://www.flashscore.com/' + p.url + '/results'
        page_source = getPlayer(url)
        processPlayer(page_source)
        pDF = pd.read_csv('./playerDF.csv', index_col=False)
        pDF.loc[pDF['url'] == p.url, 'scraped'] = True
        pDF.to_csv('./playerDF.csv', index=False)


def processPlayer(page_source):
    s = BeautifulSoup(str(page_source), 'html.parser')
    matches = s.select('.event__match')
    pDF = pd.read_csv('./playerDF.csv', index_col = False)
    bDFCols = ['lPlayer', 'rPlayer', 'lScore', 'rScore', 'lGames', 'rGames', 'datetime', 'id']
    if './csv/static/matchDF.csv' not in os.listdir('./'):
        bDF = pd.DataFrame([], columns=bDFCols)
    else:
        bDF = pd.read_csv('./csv/static/matchDF.csv', index_col = False)
    for (index, match) in enumerate(matches):
        players = match.select('.event__participant')
        if len(players) > 0:
            if match.get('id')[5:] not in bDF.id.values:
                for player in players:
                    playerName = dropCountry(player.text)
                    if playerName not in pDF.name.values:
                        url = 'https://www.flashscore.com/match/' + match.get('id')[5:] + '/#match-summary'
                        page_source = fetchPageSource(url)
                        pArr = getPlayers(page_source)
                        for row in pArr:
                            if row[1] not in pDF.url.values:
                                pDF = pDF.append(pd.DataFrame([[row[0], row[1], False]], columns=['name', 'url', 'scraped']))
                                pDF.to_csv("./playerDF.csv", index=False)


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
                row = [dropCountry(players[0].text), dropCountry(players[1].text), lScore[0].text, rScore[0].text, rsToString(lGames), rsToString(rGames), date[0].text, match.get('id')[5:]]

                new = pd.DataFrame([row], columns=bDFCols)
                bDF = bDF.append(new)
                pDF.to_csv("./playerDF.csv", index=False)
                bDF.to_csv("./csv/static/matchDF.csv", index=False)
                killPROC("geckodriver")
                killPROC("firefox")
    killPROC("geckodriver")
    killPROC("firefox")
initial()
