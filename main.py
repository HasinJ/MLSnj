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
import traceback
from fake_useragent import UserAgent

#my imports
from parsers import Parser
from queries import Queries

class Scraper():

    def __init__(self):
        self.count=0
        self.maxItems=0
        self.county=''

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

    def requestIntoSoup(self, header=None, param=None, extraURL='', test=False, json=False):
        if not test: time.sleep(random.randint(3,7))
        r=None
        self.headerBase['user-agent']=UserAgent().random
        with requests.Session() as s:
            if(param==None): r=s.get(self.urlbase + extraURL, headers=header)
            else: r=s.get(self.urlbase + extraURL, headers=header, params=param)
        if json: return r.json()
        else: return BeautifulSoup(r.content, 'html.parser')


    def mainPage(self) -> bool:
        print(self.headerBase['Referer'])
        self.mainSoup = self.requestIntoSoup(header=self.headerBase, param=self.params, extraURL="/listings/index.cfm")
        try:
            self.maxItems = int(self.mainSoup.find('input', class_="totalSearchResult")['value'])
            if(self.maxItems<=0): return False
            print(f"MAX ITEMS: {self.maxItems}")
            print(f"PAGE: {self.params['page']}")
            print("\n")
        except:
            return False
        return True

    def extract(self, test=False):
        #not temp
        classes = self.mainSoup.findAll('span', class_="text-uppercase prompt-semibold")
        #for c in classes:
            #print(c.next_sibling.next_sibling.contents[1]['href'])
        #exit()
        for c in classes:
            self.count+=1
            print(f"current: {self.count}")

            try:
                href = c.next_sibling.next_sibling.contents[1]['href']
                print(href)

                self.mainSoup = self.requestIntoSoup(header=self.headerBase, extraURL=href)
                if not self.mainSoup: continue
                self.saveHTML(self.mainSoup.prettify(), fr"data\html\html{self.count}.html")

                parser = Parser(self.urlbase + href, self.mainSoup, self.requestIntoSoup)
                if not parser.transform(self.county): continue

                queries = Queries(parser.getExtractions())
                queries.loadAddress(test)
                queries.loadRef(parsers.getMLSNum)
                queries.loadDate(parser.listDate, test)
                queries.loadDetails(test)
                if(parser.soldDate):
                    queries.loadDate(parser.soldDate, test)
                    queries.loadLastSold()

                queries.cursor.close()

            except Exception:
                traceback.print_exc()

            if(self.count>=self.maxItems): return
            #if(self.count % 1 == 0): return #testing house count
            print("\n")

    def onePage(self, href, test=False):
        try:
            self.mainSoup = self.requestIntoSoup(header=self.headerBase, extraURL=href)
            self.saveHTML(self.mainSoup.prettify(), fr"data\testHTML\TEST.html")
            parser = Parser(self.urlbase + href, self.mainSoup, self.requestIntoSoup)
            if not parser.transform('PASSAIC', test): return

            queries = Queries(parser.getExtractions())
            queries.loadAddress(test)
            queries.loadRef(parsers.getMLSNum)
            queries.loadDate(parser.listDate, test)
            queries.loadDetails(test)
            if(parser.soldDate):
                queries.loadDate(parser.soldDate, test)
                queries.loadLastSold()
            queries.cursor.close()

        except Exception:
            traceback.print_exc()

    def saveHTML(self, html, dir):
        html_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), dir)
        with open(html_file, 'w') as f:
            f.write(html)

    def printSoup(self, soup): print(soup.prettify())

    def setCounty(self, county: str):
        county=county.upper()
        self.headerBase['Referer'] = 'https://www.njmls.com/listings/index.cfm?action=dsp.results&county=&state=NJ&proptype=1%2C3a%2C3b%2C2&searchtype=county_search&status=A&mlsSearch=1&minprice=&maxprice='
        self.headerBase['Referer'] = re.sub(r"(?<=county\=).?(?=&)", county, self.headerBase.get('Referer'))
        self.params['county']=county
        self.county=county

    def addPage(self, num: int): self.params['page'] = f"{int(self.params.get('page')) + 1}"

    def setPage(self, num: int): self.params['page'] = f'{num}'

    def resetCounters(self):
        self.count=0
        self.maxItems=0
        self.setPage(1)

if __name__ == '__main__':
    counties = [
        #"ATLANTIC",
        "BERGEN", #North
        #"BURLINGTON",
        #"CAMDEN",
        #"CAPE MAY",
        #"CUMBERLAND",
        "ESSEX", #North
        "GLOUCESTER",
        "HUDSON", #North
        "HUNTERDON", #Central
        "MERCER", #Central
        "MIDDLESEX", #Central
        "MONMOUTH", #Central
        "MORRIS", #North
        "OCEAN", #Central
        "PASSAIC", #North
        #"SALEM",
        "SOMERSET", #Central
        "SUSSEX", #North
        "UNION", #North
        "WARREN", #North
    ]

    test = Scraper()
    #"""
    for county in counties:
        time.sleep(random.randint(3,5))
        print("\n",county.upper())
        test.setCounty(county)
        if (test.mainPage()==False): print('\n'); continue;

        while(test.count<test.maxItems):
            test.extract()
            test.addPage(1)
            test.mainPage()
            #if(int(test.params['page'])>=1): break #testing page count
            print("\n")

        #reset
        test.resetCounters()
        print("\n")
    #"""
    #test.onePage("/listings/index.cfm?action=dsp.info&mlsnum=21046492&openhouse=true&dayssince=15&countysearch=true", True)
    #test.onePage("/listings/index.cfm?action=dsp.info&mlsnum=22002223&openhouse=true&dayssince=15&countysearch=true", True)
