import sys
import pandas as pd
sys.path.insert(1, './scraper/')
import scraperHelper

def test_swap():
    startDF = pd.DataFrame([
        ['3', '1', '1', '3', '1', '2'], 
        ['2', '2', '2', '2', '1', '2'], 
        ['1', '3', '3', '1', '1', '2']],
        columns=['lTeam', 'rTeam', 'Player_left', 'Player_right', 'Score_left', 'Score_right'])

    correctDF = pd.DataFrame([
        ['1', '3', '1', '3', '2', '1'], 
        ['2', '2', '2', '2', '1', '2'], 
        ['3', '1', '3', '1', '2', '1']],
        columns=['lTeam', 'rTeam', 'Player_left', 'Player_right', 'Score_left', 'Score_right'])
    


    resultingDF = scraperHelper.swap(startDF, ['lTeam', 'Player_left'], [['lTeam', 'rTeam'], ['Score_left', 'Score_right']])
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_getLargest():
    startDF = pd.DataFrame([
        ['a', '1', '2', 1, 3, 'bovada'],
        ['a', '1', '2', 0, 1, 'betonline'], 
        ['b', '1', '2', 2, 1, 'betonline'],
        ['b', '1', '2', 1, 1, 'bovada'],
        ['c', '1', '2', 1, 1, 'bovada']],
        columns=['id', 'lTeam', 'rTeam', 'lValue', 'rValue', 'platform'])

    correctDF = pd.DataFrame([
        ['a', '1', '2', 1, 3, 'bovada'],
        ['b', '1', '2', 2, 1, 'betonline'],
        ['c', '1', '2', 1, 1, 'bovada']],
        columns=['id', 'lTeam', 'rTeam', 'lValue', 'rValue', 'platform'])
    
    resultingDF = startDF.groupby(['id']).apply(lambda x: scraperHelper.getLargest(x, 'lValue', 'rValue')).reset_index(['id'], drop=True)

    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_getLargestInGroup():
    startDF = pd.DataFrame([
        ['a', '1', '2', 1, 3, 'bovada'],
        ['a', '1', '2', 0, 1, 'betonline'], 
        ['b', '1', '2', 2, 1, 'betonline'],
        ['b', '1', '2', 1, 1, 'bovada']],
        columns=['id', 'lTeam', 'rTeam', 'lValue', 'rValue', 'platform'])

    correctDF = pd.DataFrame([
        ['a', '1', '2', 1, 3, 'bovada'],
        ['b', '1', '2', 2, 1, 'betonline']],
        columns=['id', 'lTeam', 'rTeam', 'lValue', 'rValue', 'platform'])
    
    resultingDF = scraperHelper.getLargestInGroup(startDF, ['id'], 'lValue', 'rValue') 

    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_filterOnlyNew():
    startDF = pd.DataFrame([
        ['1', 'a', 'b', 1],
        ['2', 'a', 'c', 2], 
        ['3', 'd', 'b', 3], 
        ['3', 'e', 'f', 3], 
        ['3', 'e', 'd', 4], 
        ['3', 'l', 'p', 4], 
        ['3', 'j', 'k', 4], 
        ['3', 'k', 'o', 4], 
        ['4', 'd', 'c', 4]],
        columns=['id', 'lTeam', 'rTeam', 'datetime'])

    correctDF = pd.DataFrame([
        ['1', 'a', 'b', 1],
        ['3', 'e', 'f', 3]], 
        columns=['id', 'lTeam', 'rTeam', 'datetime'])
    
    resultingDF = scraperHelper.filterOnlyNew(startDF, ['l', 'k'], 'datetime')

    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_americanToImplied():
    assert round(scraperHelper.americanToImplied(100), 2) == 0.50
    assert round(scraperHelper.americanToImplied(-200), 2) == 0.67
    assert round(scraperHelper.americanToImplied(200), 2) == 0.33
