import sys
import pandas as pd
import numpy as np
import random
sys.path.insert(1, './evaluation/')
import evaluate


def test_prep():
    startArr = [
        [1, 2, np.nan]
    ]
    startDF = pd.DataFrame(
        startArr, 
        columns=['Player_left', 'Player_right', 'score'])
    correctArr = [
        [0.0]
    ]
    correctDF = pd.DataFrame(
        correctArr, 
        columns=['score'])
    resultingDF = evaluate.prep(startDF)
    print(correctDF)
    print(resultingDF)
    assert resultingDF.equals(correctDF)

def test_calculateLWIN():
    startArr = [
        [1],
        [2],
        [3],
        [4],
        [5],
        [6]
    ]
    mergeArr = [
        [1, 1, 6],
        [2, 2, 5],
        [3, 3, 4],
        [7, 4, 4],
        [4, 4, 3],
        [5, 5, 2],
        [6, 6, 1]
    ]
    startDF = pd.DataFrame(
        startArr, 
        columns=['id'])
    mergeDF = pd.DataFrame(
        mergeArr, 
        columns=['id', 'lScore', 'rScore'])
    correctArr = [
        [1, 1, 6, False],
        [2, 2, 5, False],
        [3, 3, 4, False],
        [4, 4, 3, True],
        [5, 5, 2, True],
        [6, 6, 1, True]
    ]
    correctDF = pd.DataFrame(
        correctArr, 
        columns=['id', 'lScore', 'rScore', 'lwin'])
    resultingDF = evaluate.calculateLWIN(startDF, mergeDF = mergeDF)
    print(correctDF)
    print(resultingDF)
    assert resultingDF.equals(correctDF)