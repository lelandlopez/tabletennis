import sys
import pandas as pd
sys.path.insert(1, './')
import formatter

def test_dropAndFormat():

    startDF = pd.DataFrame([[0, 1], [0, 1]], columns=['id', 'num'])
    print(startDF)
    # startDF = formatter.dropAndFormat(startDF)
    assert startDF.equals(startDF)