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
from fake_useragent import UserAgent

class Parser():

    def __init__(self, fullLink, houseSoup, requester):
        self.__fullLink = fullLink
        self.__houseSoup = houseSoup
        self.__requester=requester
        self.__listingHistory = None
        self.__extractions = {}
        self.__MLSnum = None
        self.listDate = None
        self.soldDate = None

    def transform(self, county=None, test=False) -> bool:
        address = self.__transformAddress(test)
        #if address==None:
            #print("ADDRESS: No address found")
            #return False
        address['county']=county
        if test: print(f"address: {address}")

        details = self.__transformDetails(test)
        if test: print(f"details: {details}")
        if test: print(f"listing date: {self.listDate}")

        soldInfo = self.__transformSold(test)
        details['prevprice'] = soldInfo['price']
        if test: print(f"last sold info: {soldInfo}")

        self.__extractions['address'] = address
        self.__extractions['details'] = details
        self.__extractions['sold'] = soldInfo

        return True

    def __transformSold(self, test):
        def clean(index):
            list = self.__listingHistory[index]
            date = datetime.datetime.strptime(list['hs_date'], "%m/%d/%y")
            if(int(date.strftime('%Y'))<2020): return False
            return list

        def grab(list, res):
            self.soldDate = self.__transformDate(datetime.datetime.strptime(list['hs_date'], "%m/%d/%y"), test)
            res['date'] = self.soldDate['fullDate']
            res['price'] = list['hs_price'].strip().replace(',','').replace('$','')


        res = {'date': None, 'price': 0}
        headers = {'accept': '*/*', 'Content-Type': 'application/json', 'Referer': self.__fullLink}
        self.__listingHistory = self.__requester(header=headers, param={'mlsnum': f'{self.__MLSnum}'}, extraURL='/listings/mlshistoryinfo.cfm', json=True)
        if test: print(f"history: {self.__listingHistory}")
        for i in range(len(self.__listingHistory)):
            list = clean(i)
            if not list: break

            #if price change date is greater than list date
            if(list['hs_hscode']=='Price change' and datetime.datetime.strptime(list['hs_date'], "%m/%d/%y") > datetime.datetime.strptime(self.listDate['fullDate'], '%Y-%m-%d')):
                for j in range(len(self.__listingHistory)):
                    list = clean(j)
                    if not list: break
                    if list['hs_hscode']=='Listed':
                        grab(list, res)
                        return res

            elif(list['hs_hscode']=="Off-market" or list['hs_hscode']=="Sold"):
                grab(list, res)
                return res

        return res

    def __transformDetails(self, test):
        def clean(x):
            if(x.strip()=='None'): return None
            return x.strip().replace(' ','').replace(":","").replace("$",'').replace(",","").lower()

        details = self.__houseSoup.findAll("span", {"class": re.compile(r'^prompt-semibold')})
        cols = ['MLS #:','Current Price:', 'bedrooms:', 'full baths:', 'half baths:', 'basement:', 'garage:', 'category:', 'taxes:', 'list date:']
        res = {'currentprice': None, 'bedrooms': None, 'fullbaths': '0', 'halfbaths': '0', 'basement': None, 'garage': None, 'category': None, 'listdate': None, 'taxes': '0'}
        found=0

        for detail in details:
            #print(detail)
            if detail.contents[0].strip() in cols:
                found+=1
                key = clean(detail.contents[0])
                value = clean(detail.next_sibling.next_sibling.contents[0])
                if(key == 'mls#'): self.__MLSnum=value
                elif(key=='listdate'):
                    value = datetime.datetime.strptime(value, "%m/%d/%Y")
                    self.listDate = self.__transformDate(value, test)
                else:
                    if(value and (key=='basement' or key=='garage')): value="Yes"
                    res[key]=value
                if(found>=len(cols)): break

        res['listdate']=self.listDate['fullDate']
        return res

    def __transformAddress(self, test):
        def clean(x):
            x = x.strip()
            pos = x.index(':')
            x = x[:pos] + '"' + x[pos:]
            return '"' + x + '"'

        address = self.__houseSoup.find("a", {"class" : re.compile(r'^fancybox listing-map')})
        if address==None: return None
        address = " ".join(address['class'][3:-1]).split("mls_number")[0].split("',")[:-1]
        address = ', '.join(list(map(clean, address)))
        address = "{" + address.replace("'", '"') + '}'
        address = json.loads(address)
        address['street'] = address['address']

        return address

    def __transformDate(self, value, test):

        return {
            'fullDate': value.strftime('%Y-%m-%d'),
            'day': value.strftime('%d'),
            'month': value.strftime('%m'),
            'monthShort': value.strftime('%b'),
            'monthFull': value.strftime('%B'),
            'year': value.strftime('%Y'),
            'DOW': value.strftime('%a'),
            'fullDOW': value.strftime('%A'),
        }

    def getExtractions(self): return self.__extractions

    def getMLSNum(self) -> int: return self.__MLSnum
