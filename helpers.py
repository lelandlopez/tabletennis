import time
import pandas as pd

class helpers:
    def __init__():
        pass

    def printTime(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            k = func(*args, **kwargs)
            print(time.time()-start, func.__name__)
            return k
        return wrapper

    def createDF():
        df1 = pd.read_csv('./csv/static/matchDF.csv')
        df = pd.read_csv('./csv/static/matchDF_1.csv')
        frames = [df, df1]
        return pd.concat(frames).reset_index()