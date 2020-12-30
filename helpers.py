import time
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