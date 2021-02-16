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
    if url == "":
        ps = scraperHelper.fetchPageSource(frontPage_url)
        print(time.asctime( time.localtime(time.time())))
        urls = getTournaments(ps)
    else:
        urls = [url]
    for i in urls:
        print(i)
        if results == True:
            k = i + 'results'
            ps = scraperHelper.fetchPageSource(i + 'results')
            scraperHelper.processPlayer(ps, playerDF_filename, matchDF_filename)
        if fixtures == True:
            k = i + 'fixtures'
            ps = scraperHelper.fetchPageSource(i + 'fixtures')
            scraperHelper.processPlayer(ps, playerDF_filename, matchDF_filename)

    import json
    from datetime import datetime
    websiteInfoFileDir = './websiteInfo.json'
    with open(websiteInfoFileDir) as f:
        websiteInfo = json.load(f)
    websiteInfo['lastScraped'] = datetime.now().__str__()
    with open(websiteInfoFileDir, 'w') as json_file:
        json.dump(websiteInfo, json_file)
    



# lenargs = len(sys.argv)
# if lenargs == 2:
#     insertSpecific(True, True, sys.argv[1])
# else:
#     insertSpecific(True, True)
