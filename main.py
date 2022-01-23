import os
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import datetime
import time
import sys
import pandas as pd
import regex as re
import requests
import json
import random
import functools
import csv
from fake_useragent import UserAgent

#my imports
from parsers import Parser
#from queries import Queries

class Scraper():

    def __init__(self):
        self.urlbase = "https://www.njmls.com"
        self.params = {
            "zoomlevel": '0',
            "action": 'xhr.results.view.rerunphoto',
            "page": '1',
            "display": '30',
            "sortBy": 'newest',
            "isFuzzy": 'false',
            "location": '',
            "city": '',
            "state": 'NJ',
            "county": 'PASSAIC',
            "zipcode": '',
            "radius": '',
            "proptype": ',1,3a,3b,2',
            "maxprice": '',
            "minprice": '',
            "beds": '0',
            "baths": '0',
            "dayssince": '',
            "newlistings": '',
            "pricechanged": '',
            "keywords": '',
            "mls_number": '',
            "garage": '',
            "basement": '',
            "fireplace": '',
            "pool": '',
            "yearBuilt": '',
            "building": '',
            "officeID": '',
            "openhouse": '',
            "countysearch": 'true',
            "ohdate": '',
            "style": '',
            "rerun": '',
            "rerundate": '',
            "searchname": '',
            "backtosearch": 'false',
            "token": 'false',
            "searchid": '',
            "searchcountid": '',
            "emailalert_yn": 'I',
            "status": 'A',
            "_": str(1642896937090 + random.randint(1,999999999)),
        }

        self.headerBase = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'Referer': 'https://www.njmls.com/listings/index.cfm?action=dsp.results&county=PASSAIC&state=NJ&proptype=1%2C3a%2C3b%2C2&searchtype=county_search&status=A&mlsSearch=1&minprice=&maxprice=',
            'upgrade-insecure-requests': '1',
        }

    def start(self):
        r=None
        self.headerBase['user-agent']=UserAgent().random
        with requests.Session() as s:
            r=s.get(self.urlbase + "/listings/index.cfm", headers=self.headerBase, params=self.params)
        self.mainSoup = BeautifulSoup(r.content, 'html.parser')

    def page(self):
        #temp
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, 'data\html\start.html')
        with open(filename, "r") as f:
            self.mainSoup = BeautifulSoup(f, 'html.parser')

        #not temp
        classes = self.mainSoup.findAll('span', class_="text-uppercase prompt-semibold")
        for c in classes:
            time.sleep(random.randint(5,10))
            href = c.next_sibling.next_sibling.contents[1]['href']
            r=None
            self.headerBase['user-agent']=UserAgent().random
            with requests.Session() as s:
                r=s.get(self.urlbase + href, headers=self.headerBase)
            self.mainSoup = BeautifulSoup(r.content, 'html.parser')

            parser = Parser(self.mainSoup)
            parser.transform(test=True)

            exit()


    def printSoup(self, soup): print(soup.prettify())

if __name__ == '__main__':
    test = Scraper()
    #test.start()
    test.page()
