import sys
import pandas as pd
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