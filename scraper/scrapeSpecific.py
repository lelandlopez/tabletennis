import json
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

sys.path.insert(1, '.')
import scraperHelper

frontPage_url = 'https://www.flashscore.com/table-tennis/'
matchDF_filename = './csv/static/matchDF.csv'
playerDF_filename = './csv/static/playerDF.csv'


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




@helpers.printTime
def insertSpecific(results, fixtures, url = ""):
    driver = scraperHelper.createDriver()
    if url == "":
        ps, driver = scraperHelper.fetchPageSource(frontPage_url, driver=driver)
        urls = getTournaments(ps)
    else:
        urls = [url]
    for i in urls:
        if results == True:
            k = i + 'results'

            print(driver)
            ps, driver = scraperHelper.fetchPageSource(i + 'results', driver=driver)
            scraperHelper.processPlayer(ps, playerDF_filename, matchDF_filename)
        if fixtures == True:
            print(driver)
            k = i + 'fixtures'
            ps, driver = scraperHelper.fetchPageSource(i + 'fixtures', driver=driver)
            scraperHelper.processPlayer(ps, playerDF_filename, matchDF_filename)

    import json
    from datetime import datetime
    websiteInfoFileDir = './websiteInfo.json'
    with open(websiteInfoFileDir) as f:
        websiteInfo = json.load(f)
    websiteInfo['lastScraped'] = datetime.now().__str__()
    with open(websiteInfoFileDir, 'w') as json_file:
        json.dump(websiteInfo, json_file)
    scraperHelper.quitDriver(driver)
    
def scrapeSpecificForever(dResults = 300, dFixtures = 3600):

    sys.path.insert(1, './scraper/Bets')
    jsonArray = []
    from scrapeBets import scrapeBets
    tStartResults = time.time()
    tStartFixtures = time.time()
    print('scraping')
    insertSpecific(True, True)
    print('finished')
    while(True):
        if time.time() - tStartResults > dResults:
            insertSpecific(True, False)
            tStartResults = time.time()
            scrapeBets()
        if time.time() - tStartFixtures > dFixtures:
            insertSpecific(False, True)
            tStartFixtures = time.time()
            scrapeBets()




