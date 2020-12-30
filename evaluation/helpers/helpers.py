import pandas as pd
import numpy as np

class helpers():
    def visualizeDiffs(df, init):
        init['lwin'] = init['lScore'] > init['rScore']
        p = df.merge(init, on='id')
        df.shape
        p.shape
        p.head()
        k = [i for i in df.columns if 'diff' in i]
        p = p[k + ['lwin']]
        for i in k:
            plt.figure()
            sns.kdeplot(data=p, x=i, hue="lwin")