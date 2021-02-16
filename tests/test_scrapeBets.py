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