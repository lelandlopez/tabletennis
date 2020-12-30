from bs4 import BeautifulSoup
import os
import sys
import numpy as np
# import libraries
import psutil

def fetchPageSource(url):
    print('fetching: ', url)
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    page_source = ""
    try:
        options = Options()
        options.headless = True
        driver.get(url)
        page_source = driver.page_source
    except:
        print('error')
        pass
    return page_source