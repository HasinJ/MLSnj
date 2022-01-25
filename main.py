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
from queries import Queries

class Scraper():

    def __init__(self):
        self.count=0
        self.maxItems=3

        self.urlbase = "https://www.njmls.com"
        self.params = {
            "zoomlevel": '0',
            "action": 'xhr.results.view.rerunphoto',
            "page": f'1',
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
            'upgrade-insecure-requests': '1',
        }

    def start(self):
        r=None
        self.headerBase['user-agent']=UserAgent().random
        with requests.Session() as s:
            r=s.get(self.urlbase + "/listings/index.cfm", headers=self.headerBase, params=self.params)
        self.mainSoup = BeautifulSoup(r.content, 'html.parser')
        self.maxItems = int(self.mainSoup.find('input', class_="totalSearchResult")['value'])
        print(f"MAX ITEMS: {self.maxItems} current: {self.count}")
        print(f"PAGE: {self.params['page']}")
        print("\n")


    def extract(self, test=False):
        """
        #temp
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, 'data\html\start.html')
        with open(filename, "r") as f:
            self.mainSoup = BeautifulSoup(f, 'html.parser')
        """

        #not temp
        classes = self.mainSoup.findAll('span', class_="text-uppercase prompt-semibold")
        for c in classes:
            time.sleep(random.randint(5,10))
            self.count+=1
            href = c.next_sibling.next_sibling.contents[1]['href']
            print(href)
            r=None
            self.headerBase['user-agent']=UserAgent().random
            with requests.Session() as s:
                r=s.get(self.urlbase + href, headers=self.headerBase)
            self.mainSoup = BeautifulSoup(r.content, 'html.parser')
            #self.saveHTML(r.content, fr"data\html\html{self.count+1}.html")

            parser = Parser(self.mainSoup)
            parser.transform()

            queries = Queries(parser.getExtractions())
            queries.loadAddress()
            queries.loadRef(href)
            queries.loadDetails(test)

            queries.cursor.close()
            if(self.count>=self.maxItems): return
            if(self.count % 1 == 0): return #testing house count
            print("\n")

    def onePage(self, href, test=False):
        r=None
        self.headerBase['user-agent']=UserAgent().random
        with requests.Session() as s:
            r=s.get(self.urlbase + href, headers=self.headerBase)
        self.mainSoup = BeautifulSoup(r.content, 'html.parser')
        self.saveHTML(r.content, fr"data\html\TEST.html")

        parser = Parser(self.mainSoup)
        parser.transform(test)

        queries = Queries(parser.getExtractions())
        queries.loadAddress(test)
        queries.loadRef(href)
        queries.loadDetails(test)

        queries.cursor.close()

    def saveHTML(self, html, dir):
        html_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), dir)
        with open(html_file, 'wb') as f:
            f.write(html)

    def printSoup(self, soup): print(soup.prettify())

    def setCounty(self, county: str):
        self.headerBase['Referer'] = 'https://www.njmls.com/listings/index.cfm?action=dsp.results&county=&state=NJ&proptype=1%2C3a%2C3b%2C2&searchtype=county_search&status=A&mlsSearch=1&minprice=&maxprice='
        self.headerBase['Referer'] = re.sub(r"(?<=county\=).?(?=&)", county, self.headerBase.get('Referer'))

    def addPage(self, num: int):
        self.params['page'] = f"{int(self.params.get('page')) + 1}"

    def setPage(self, num: int):
        self.params['page'] = f'{num}'

if __name__ == '__main__':
    counties = [
        'Passaic',
        'MIDDLESEX',
    ]
    test = Scraper()

    for county in counties:
        time.sleep(random.randint(3,5))
        county=county.upper()
        print("\n",county)
        test.setCounty(county)
        #print(test.headerBase['Referer'])

        while(test.count<test.maxItems):
            test.start()
            test.extract()
            test.addPage(1)
            if(int(test.params['page'])>=1): break #testing page count
            print("\n\n")

        #reset
        test.setPage(1)
        print("\n")

    #test.onePage("/listings/index.cfm?action=dsp.info&mlsnum=22002223&openhouse=true&dayssince=15&countysearch=true", True)
