from django.shortcuts import render
from django.http import JsonResponse
import csv
import sys
import json
import pandas as pd
import numpy as np
    

placedBetsFilePath = './scraper/Bets/placedBets.csv'
matchDFFP = './csv/static/matchDF.csv'

def getEstimatedVsActualProfit(request):
    def getPayout(line):
        p = 0 
        if line > 0:
            p = line
        else:
            p = 100 + 100/abs(line)
        return p/100

    df = pd.read_csv(placedBetsFilePath)
    df = df[df['win'].isnull() == False]

    df['payout'] = df['line'].apply(getPayout)
    df['payout'] = df['win'] * df['payout']
    df.loc[df['payout'] == 0, 'payout'] = -1
    print(df['payout'])
    df['actual']= df['payout'].cumsum()

    te = df['edge'].cumsum().tolist()
    df['te']= df['edge'].cumsum()
    actual = df['actual'].values.tolist()
    te = df['te'].values.tolist()
    te = {
        'actual':actual,
        'te':te,
    }
    return JsonResponse(te)


def updateModelPerformance(request):

    df = pd.read_csv(placedBetsFilePath)
    mdf = pd.read_csv(matchDFFP)
    missingWinDF = df[df['win'].isnull()]
    print(missingWinDF.id)
    for (index, i) in missingWinDF.iterrows():
        k = mdf[mdf['id'] == i['id']]
        if k['lScore'].values != '-' and k['rScore'].values != '-':
            lScore = int(k['lScore'].values[0])
            rScore = int(k['rScore'].values[0])
            if int(lScore) >= 3 or int(rScore) >= 3:
                if lScore > rScore:
                    if i['team'] == 0:
                        df.loc[df['id'] == i['id'], 'win'] = 1
                    else:
                        df.loc[df['id'] == i['id'], 'win'] = 0
                if lScore < rScore:
                    if i['team'] == 1:
                        df.loc[df['id'] == i['id'], 'win'] = 0
                    else:
                        df.loc[df['id'] == i['id'], 'win'] = 1
    df = df.to_csv(placedBetsFilePath, index=False)
    return JsonResponse({})

def getPlacedBets(request):
    df = pd.read_csv(placedBetsFilePath)
    def _getStats(df):
        numBets = len(df)
        betsPending = len(df[df['win'].isnull()])
        betsCompleted = len(df[df['win'].isnull() == False])
        betsWon = len(df[df['win'] == 1])
        completedBetsWins = df[df['win'].isnull() == False]['win'].cumsum().tolist()
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

def index(request):
    with open('./websiteInfo.json') as f:
        websiteInfo = json.load(f)

    jsonArray = getBets()

    context = {
        'bets': jsonArray,
        'websiteInfo': websiteInfo
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
    fixtures = request.GET.get('fixtures') == 'true'
    results = request.GET.get('results') == 'true'
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
    line = request.GET.get('line')
    edge = request.GET.get('edge')
    site = request.GET.get('site')
    team = request.GET.get('teamSide')
    print(request.GET)
    placedBetsFilePath = './scraper/Bets/placedBets.csv'
    df = pd.read_csv(placedBetsFilePath)
    k = pd.DataFrame([[now, id, team, line, edge, site]], columns=['time', 'id', 'team', 'line', 'edge', 'site'])
    df = df.append(k)
    df.to_csv(placedBetsFilePath, index=False)
    return JsonResponse({})