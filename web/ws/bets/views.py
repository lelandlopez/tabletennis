from django.shortcuts import render
from django.http import JsonResponse
import csv
import sys
import json
    




def index(request):
    csvFilePath = './predictions.csv'
    jsonArray = []

    with open('./websiteInfo.json') as f:
        websiteInfo = json.load(f)

    print(websiteInfo)

    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
    print(jsonArray)

    context = {
        'bets': jsonArray,
        'websiteInfo': websiteInfo
    }
    return render(request, 'bets/index.html', context)

def calculateBets(request):
    data = {
        'name': 'Vitor',
        'location': 'Finland',
        'is_active': True,
        'count': 28
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
    from scrapeBets import scrapeBets
    scrapeBets()
    data = {
    }
    return JsonResponse(data)

# Create your views here.

