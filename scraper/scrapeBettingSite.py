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

    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    results = driver.page_source
    return results


def fetchPageSource(url):
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    page_source = ""
    try:
        run firefox webdriver from executable path of your choice
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.headless = True
        driver.get(url)
        page_source = driver.page_source
    except:
        pass
    # finally:
        # driver.close()
        # driver.quit()
        # try:
        #     ffpid = int(driver.service.process.pid)
        #     os.kill(ffpid, signal.SIGTERM)
        # except:
        #     pass
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



def processPlayer(page_source):
    s = BeautifulSoup(str(page_source), 'html.parser')
    cols = ['lTeam', 'rTeam', 'lLine', 'rLine']
    df = pd.DataFrame([], columns=cols)
    print(df)
    matches = s.select('.offering-games__table-row')
    for (index, match) in enumerate(matches):
        teams = match.select('.lines-row__team-name')
        # print(teams)
        lines = match.select('.lines-row__money')
        # print(lines)
        k = pd.DataFrame([[teams[0].text, teams[1].text, lines[0].text, lines[1].text]], columns=cols)
        print(k)
        df = df.append(k)
    return df
    # killPROC("geckodriver")
    # killPROC("firefox")

# url = 'https://beta.betonline.ag/sportsbook/table-tennis/russia/moscow-liga-pro'
# url = 'https://beta.betonline.ag/sportsbook/darts/pdc/pdc-home-tour'
url = 'https://beta.betonline.ag/sportsbook/darts/pdc/pdc-home-tour'
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
page_source = getPlayer(url)
k = processPlayer(page_source)
killPROC("geckodriver")
killPROC("firefox")
k
