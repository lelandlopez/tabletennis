import sys
import pandas as pd
import numpy as np
import random
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

    resultingDF = afe.applyOnBoth(startDF, ['CountLen', 'Count'], len)
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
    startArr = [
        ['1', '1', 1], 
        ['2', '1', 3], 
        ['3', '1', 2],
        ['1', '2', 4], 
        ['2', '2', 5], 
        ['3', '2', 6]]
    random.shuffle(startArr)
    startDF = pd.DataFrame(
        startArr ,
        columns=['datetime', 'Player', 'Score'])
    startDF, numMatchCol = afe.createNumMatch(startDF, group)
    resultingArr = [
        ['1', '1', 1, 0, 1.0],
        ['2', '1', 3, 1, 4.0], 
        ['3', '1', 2, 2, 6.0], 
        ['1', '2', 4, 0, 4.0],
        ['2', '2', 5, 1, 9.0], 
        ['3', '2', 6, 2, 15.0]]
    correctDF = pd.DataFrame(
        resultingArr, 
        columns=['datetime', 'Player', 'Score', 'Player_num_match', 'Player_Score_cumsum'])

    o = afe.getCumsum(startDF, group, ['Score'])
    resultingDF = o[0].reset_index(drop=True)
    resultingDiv = o[1]
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF) and resultingDiv == ['Player_Score_cumsum']

def testRollingSum():
    afe = autoFeatureEngineer(False)
    group = ['Player']
    startArr = [
        ['1', '1', 1], 
        ['3', '1', 2], 
        ['4', '1', 3], 
        ['5', '1', 9], 
        ['6', '1', 7], 
        ['1', '2', 1], 
        ['2', '2', 2], 
        ['3', '2', 3], 
        ['4', '2', 9]]
    random.shuffle(startArr)
    startDF = pd.DataFrame(
        startArr, 
        columns=['datetime', 'Player', 'Score'])
    startDF, numMatchCol = afe.createNumMatch(startDF, group)
    endArr = [
        ['1', '1', 1, 0, np.NaN], 
        ['3', '1', 2, 1, 3],
        ['4', '1', 3, 2, 5],
        ['5', '1', 9, 3, 12],
        ['6', '1', 7, 4, 16],
        ['1', '2', 1, 0, np.NaN], 
        ['2', '2', 2, 1, 3],
        ['3', '2', 3, 2, 5],
        ['4', '2', 9, 3, 12]]
    correctDF = pd.DataFrame(
        endArr,
        columns=['datetime', 'Player', 'Score', 'Player_num_match', 'Player_Score_rolling_2'])
    o = afe.getRollingSum(startDF, group, ['Score'], 2)
    resultingDF = o[0].reset_index(drop=True)
    resultingDiv = o[1]
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF) and resultingDiv == ['Player_Score_rolling_2']

def test_cleanup():
    afe = autoFeatureEngineer(False)
    startArr = [
        [1, '1', 1, 1, 1, 1]]
    startDF = pd.DataFrame(
        startArr, 
        columns=['Score_cumsum', 'Player', 'Score', 'Player_num_match', 'last_Score_cumsum', 'id'])
    endArr = [
        ['1', 1, 1]]
    correctDF = pd.DataFrame(
        endArr,
        columns=['Player', 'last_Score_cumsum', 'id'])
    resultingDF = afe.cleanup(startDF)
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_merge():
    afe = autoFeatureEngineer(False)
    group = ['Player']
    startArr = [
        ['1', '2', '1'], 
        ['2', '2', '1'], 
        ['3', '2', '1'], 
        ['4', '1', '2'], 
        ['5', '1', '2'], 
        ['6', '1', '2']]
    random.shuffle(startArr)
    splitArr = [
        ['1', '1', 1], 
        ['2', '1', 2], 
        ['3', '1', 3], 
        ['4', '1', 4], 
        ['5', '1', 5], 
        ['6', '1', 6],
        ['1', '2', 7], 
        ['2', '2', 8], 
        ['3', '2', 9], 
        ['4', '2', 10], 
        ['5', '2', 11], 
        ['6', '2', 12]]
    random.shuffle(splitArr)
    correctArr = [
        ['1', '2', 7, '1', 1], 
        ['2', '2', 8, '1', 2], 
        ['3', '2', 9, '1', 3], 
        ['4', '1', 4, '2', 10], 
        ['5', '1', 5, '2', 11], 
        ['6', '1', 6, '2', 12]]
    startDF = pd.DataFrame(
        startArr, 
        columns=['id', 'lPlayer', 'rPlayer'])
    splitDF = pd.DataFrame(
        splitArr, 
        columns=['id', 'Player', 'Score'])
    correctDF = pd.DataFrame(
        correctArr,
        columns=['id', 'Player_left', 'Score_left', 'Player_right', 'Score_right'])
    resultingDF = afe.merge(splitDF, startDF)
    resultingDF = resultingDF.sort_values('id').reset_index(drop=True)
    print(resultingDF)
    print(correctDF)
    assert resultingDF.equals(correctDF)

def test_shift():
    afe = autoFeatureEngineer(False)
    group = ['Player']
    startArr = [
        ['1', 0, 1.0],
        ['1', 1, 4.0], 
        ['1', 2, 6.0], 
        ['2', 0, 4.0],
        ['2', 1, 9.0], 
        ['2', 2, 15.0]]
    startDF = pd.DataFrame(
        startArr, 
        columns=['Player', 'Player_num_match', 'Player_Score_cumsum'])
    correctArr = [
        ['1', 0, np.NaN],
        ['1', 1, 1.0], 
        ['1', 2, 4.0], 
        ['2', 0, np.NaN],
        ['2', 1, 4.0], 
        ['2', 2, 9.0]]
    correctDF= pd.DataFrame(
        correctArr, 
        columns=['Player', 'Player_num_match', 'last_Player_Score_cumsum'])

    o = afe.shift(startDF, group, ['Player_Score_cumsum'])
    resultingDF = o[0].reset_index(drop=True)
    resultingDiv = o[1]
    print(resultingDF)
    print(correctDF)
    print(resultingDiv)
    assert resultingDF.equals(correctDF) and resultingDiv == ['last_Player_Score_cumsum']