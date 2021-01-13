import sys
import pandas as pd
import numpy as np
sys.path.insert(1, './formatter/')
from autoFeatureEngineer import autoFeatureEngineer


def test_applyOnBoth():
    afe = autoFeatureEngineer(False)
    startDF = pd.DataFrame([
        [[1, 2], [2]], 
        [[1], [2, 3, 4]], 
        [[2, 3, 4], [3, 4]]], 
        columns=['lCount', 'rCount'])

    correctDF = pd.DataFrame([
        [[1, 2], [2], 2, 1], 
        [[1], [2, 3, 4], 1, 3], 
        [[2, 3, 4], [3, 4], 3, 2]], 
        columns=['lCount', 'rCount', 'lCountLen', 'rCountLen'])

    resultingDF = afe.applyOnBoth(startDF, ['Count', 'CountLen'], len)
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_createNumMatch():
    afe = autoFeatureEngineer(False)
    startDF = pd.DataFrame([
        ['3', '1'], 
        ['2', '2'], 
        ['1', '1']],
        columns=['datetime', 'Player'])

    correctDF = pd.DataFrame([
        ['3', '1', 1], 
        ['2', '2', 0], 
        ['1', '1', 0]],
        columns=['datetime', 'Player', 'Player_num_match'])

    o = afe.createNumMatch(startDF, ['Player'])
    resultingDF = o[0]
    resultingDiv = o[1]
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF) and resultingDiv == 'Player_num_match'

def test_getCumsum():
    afe = autoFeatureEngineer(False)
    group = ['Player']
    startDF = pd.DataFrame([
        ['3', '1', 1], 
        ['2', '2', 3], 
        ['1', '1', 2]],
        columns=['datetime', 'Player', 'Score'])
    startDF, numMatchCol = afe.createNumMatch(startDF, group)
    gbf = startDF.sort_values(numMatchCol).groupby(group, as_index=False).filter(lambda x: len(x)> 1).groupby(group, as_index=False)
    correctDF = pd.DataFrame([
        ['3', '1', 1, 1, 3], 
        ['2', '2', 3, 0, np.NaN], 
        ['1', '1', 2, 0, 2]],
        columns=['datetime', 'Player', 'Score', 'Player_num_match', 'Player_Score_cumsum'])

    o = afe.getCumsum(startDF, group, gbf, ['Score'])
    resultingDF = o[0]
    resultingDiv = o[1]
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF) and resultingDiv == ['Player_Score_cumsum']