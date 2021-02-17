from django.shortcuts import render
from django.http import JsonResponse
import csv
import sys
import json
import pandas as pd
    




def index(request):
    csvFilePath = './predictions.csv'
    jsonArray = []
    placedBets = []

    with open('./websiteInfo.json') as f:
        websiteInfo = json.load(f)


    with open('./scraper/Bets/placedBets.csv', encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            placedBets.append(row['id'])
    print(placedBets)

    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            if row['id'] not in placedBets:
                jsonArray.append(row)

    

    context = {
        'bets': jsonArray,
        'websiteInfo': websiteInfo
    }
    return render(request, 'bets/index.html', context)

def calculateBets(request):
    data = {
    }
    return JsonResponse(data)


def scrapeEntire(request):
    sys.path.insert(1, './scraper')
    from scrapeSpecific import insertSpecific
    insertSpecific(True, True)
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
    placedBetsFilePath = './scraper/Bets/placedBets.csv'
    df = pd.read_csv(placedBetsFilePath)
    print(df)
    k = pd.DataFrame([[now, id]], columns=['time', 'id'])
    print("(*((((((((((((((((")
    print(k)
    print("(*((((((((((((((((")
    df = df.append(k)
    df.to_csv(placedBetsFilePath, index=False)
    return 