from django.shortcuts import render
from django.http import JsonResponse
import csv
import sys
import json
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options


placedBetsFilePath = './scraper/Bets/placedBets.csv'
matchDFFP = './csv/static/matchDF.csv'
betAmount = 0.1

def getPayout(line):
    p = 0 
    if line > 0:
        p = betAmount * (line/100)
    else:
        p = betAmount / (abs(line)/100)
    return p


def openBrowser(request):
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.bovada.lv/")
    driver.find_element_by_xpath("/html/body/bx-site/ng-component/bx-header-ch/div/nav/aside[2]/bx-header-unlogged-actions/div/a[3]").click()
    # email = driver.find_element_by_xpath("/html/body/bx-site/bx-overlay-ch/bx-overlay/div/div/bx-login-overlay/bx-overlay-container/div/bx-overlay-body/section/bx-login-placeholder/bx-login/div/bx-form/form/bx-form-group/div/bx-input-field-container[1]/div/input")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/bx-site/bx-overlay-ch/bx-overlay/div/div/bx-login-overlay/bx-overlay-container/div/bx-overlay-body/section/bx-login-placeholder/bx-login/div/bx-form/form/bx-form-group/div/bx-input-field-container[1]/div/input"))).send_keys("lelandlopez@gmail.com")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/bx-site/bx-overlay-ch/bx-overlay/div/div/bx-login-overlay/bx-overlay-container/div/bx-overlay-body/section/bx-login-placeholder/bx-login/div/bx-form/form/bx-form-group/div/bx-input-field-container[2]/div/input"))).send_keys("Waiakea2009!")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/bx-site/bx-overlay-ch/bx-overlay/div/div/bx-login-overlay/bx-overlay-container/div/bx-overlay-body/section/bx-login-placeholder/bx-login/div/bx-form/form/div[2]/button"))).click()

    return JsonResponse({})

def getEstimatedVsActualProfit(request):
    betAmount = float(request.GET.get('betAmount'))

    df = pd.read_csv(placedBetsFilePath)
    df = df[df['sideWin'].isnull() == False].copy()
    df['line'] = 0
    df.loc[df['team'] == 0, ['line']] = df['lline']
    df.loc[df['team'] == 0, ['edge']] = df['ledge']
    df.loc[df['team'] == 1, ['line']] = df['rline']
    df.loc[df['team'] == 1, ['edge']] = df['redge']

    df['tepayout'] = df['line'].apply(getPayout)
    df['tepayout'] = df['tepayout'] * 100
    df['tepayout'] = df['tepayout'].apply(np.floor)
    df['tepayout'] = df['tepayout']/100

    df['payout'] = df['line'].apply(getPayout)

    df['tepayout'] = df['wonBet'] * df['tepayout']
    df['payout'] = df['wonBet'] * df['payout']
    df.loc[df['tepayout'] == 0, 'tepayout'] = -betAmount
    df.loc[df['payout'] == 0, 'payout'] = -betAmount

    df['actualte']= df['tepayout'].cumsum()
    df['actual']= df['payout'].cumsum()

    df['edge'] = df['edge'] * betAmount
    df['te']= df['edge'].cumsum()
    actualte = df['actualte'].values.tolist()
    actual = df['actual'].values.tolist()
    te = df['te'].values.tolist()
    id = df['id'].values.tolist()
    line = df['line'].values.tolist()
    tepayout = df['tepayout'].values.tolist()
    payout = df['payout'].values.tolist()
    te = {
        'id':id,
        'actualte':actualte,
        'actual':actual,
        'te':te,
        'payout':payout,
        'line':line,
        'tepayout':tepayout,
    }
    return JsonResponse(te)


def updateModelPerformance(request):

    df = pd.read_csv(placedBetsFilePath)
    mdf = pd.read_csv(matchDFFP)

    missingWinDF = df
    for (index, i) in missingWinDF.iterrows():
        k = mdf[mdf['id'] == i['id']]
        if k['lScore'].values != '-' and k['rScore'].values != '-':
            lScore = int(k['lScore'].values[0])
            rScore = int(k['rScore'].values[0])
            if int(lScore) >= 3 or int(rScore) >= 3:
                if lScore > rScore:
                    df.loc[df['id'] == i['id'], 'sideWin'] = 0
                else:
                    df.loc[df['id'] == i['id'], 'sideWin'] = 1
            df['wonBet'] = df['sideWin'] == df['team']
    df = df.to_csv(placedBetsFilePath, index=False)
    return JsonResponse({})

def getPlacedBets(request):
    df = pd.read_csv(placedBetsFilePath)

    def _getStats(df):
        numBets = len(df)
        colNull = 'sideWin'
        betsPending = len(df[df[colNull].isnull()])
        betsCompleted = len(df[df[colNull].isnull() == False])
        betsWon = len(df[df['wonBet'] == 1])
        completedBetsWins = df[df[colNull].isnull() == False]['wonBet'].cumsum().tolist()
        aw = df[(df[colNull].isnull() == False) & (df['wonBet'] == True)]
        aw.loc[aw['team'] == 0, ['line']] = df['lline']
        aw.loc[aw['team'] == 0, ['edge']] = df['ledge']
        aw.loc[aw['team'] == 1, ['line']] = df['rline']
        aw.loc[aw['team'] == 1, ['edge']] = df['redge']
        aw = aw['line'].apply(getPayout).mean()
        k = []
        ix = 1
        for i in completedBetsWins:
            k.append(i/ix*100)
            ix += 1
        winPer = k
        return {
            'numBets': numBets,
            'betsPending': betsPending,
            'betsWon': betsWon,
            'betsCompleted': betsCompleted,
            'percentWin': betsWon/betsCompleted,
            'averageWin': aw,
            'betAmount': 0.1
        }

    p = _getStats(df)
        

    return JsonResponse(p)

def _getPlacedBets():
    placedBets = []
    with open('./scraper/Bets/placedBets.csv', encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            placedBets.append(row['id'])
    return placedBets

def getBets():
    csvFilePath = './predictions.csv'
    placedBets = _getPlacedBets()
    jsonArray = []
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            if row['id'] not in placedBets:
                if float(row['ledge']) > 0.05 or float(row['redge']) > 0.05:
                    jsonArray.append(row)
    return jsonArray

def getPending():
    csvFilePath = './scraper/Bets/placedBets.csv'
    jsonArray = []
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            if row['sideWin'] == '':
                jsonArray.append(row)
    return jsonArray

def removePlaced(request):
    id = request.GET.get('id')
    csvFilePath = './scraper/Bets/placedBets.csv'
    df = pd.read_csv(csvFilePath)
    df = df.loc[df['id'] != id]
    df = df.to_csv(csvFilePath, index=False)
    return JsonResponse({})

def index(request):
    with open('./websiteInfo.json') as f:
        websiteInfo = json.load(f)

    jsonArray = getBets()
    pending = getPending()

    context = {
        'bets': jsonArray,
        'websiteInfo': websiteInfo,
        'pending': pending
    }
    return render(request, 'bets/index.html', context)

def getBetsResponse(request):
    jsonArray = getBets()
    data = {
        'bets': jsonArray
    }
    return JsonResponse(data)


def calculateBets(request):
    data = {
    }
    return JsonResponse(data)


def scrapeEntire(request):
    sys.path.insert(1, './scraper')
    from scrapeSpecific import insertSpecific
    from scrapeSpecific import scrapeSpecificForever
    fixtures = request.GET.get('fixtures') == 'true'
    results = request.GET.get('results') == 'true'
    # scrapeSpecificForever()
    insertSpecific(fixtures, results)
    data = {
    }
    return JsonResponse(data)

def scrapeBets(request):
    sys.path.insert(1, './scraper/Bets')
    jsonArray = []
    from scrapeBets import scrapeBets
    scrapeBets()
    csvFilePath = './predictions.csv'
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
    data = {
        'bets': jsonArray
    }
    return JsonResponse(data)

def placeBet(request):
    from datetime import datetime
    now = datetime.now() 
    id = request.GET.get('id')
    lline = request.GET.get('lline')
    ledge = request.GET.get('ledge')
    rline = request.GET.get('rline')
    redge = request.GET.get('redge')
    site = request.GET.get('site')
    team = request.GET.get('teamSide')
    print(request.GET)
    placedBetsFilePath = './scraper/Bets/placedBets.csv'
    df = pd.read_csv(placedBetsFilePath)
    k = pd.DataFrame([[now, id, team, lline, ledge, rline, redge, site]], columns=['time', 'id', 'team', 'lline', 'ledge', 'redge', 'rline', 'site'])
    df = df.append(k)
    df.to_csv(placedBetsFilePath, index=False)
    return JsonResponse({})