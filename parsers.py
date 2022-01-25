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

    def __init__(self, houseSoup):
        self.__houseSoup = houseSoup
        self.__extractions = {}

    def transform(self,test=False):
        address = self.__transformAddress(test)

        details = self.__transformDetails(test)

        self.__extractions = {
            'address': address,
            'details': details,
        }

    def __transformDetails(self, test):
        def clean(x):
            if(x.strip()=='None'): return None
            return x.strip().replace(' ','').replace(":","").replace("$",'').replace(",","").lower()

        details = self.__houseSoup.findAll("span", {"class": re.compile(r'^prompt-semibold')})
        cols = ['Current Price:', 'bedrooms:', 'full baths:', 'half baths:', 'basement:', 'garage:', 'category:', 'taxes:']
        res = {}
        found=0

        for detail in details:
            #print(detail)
            if detail.contents[0].strip() in cols:
                found+=1
                key = clean(detail.contents[0])
                value = clean(detail.next_sibling.next_sibling.contents[0])
                res[key]=value
                if(found>=len(cols)): break

        if test: print(f"details: {res}")
        return res

    def __transformAddress(self, test):
        def clean(x):
            x = x.strip()
            pos = x.index(':')
            x = x[:pos] + '"' + x[pos:]
            return '"' + x + '"'

        address = self.__houseSoup.find("a", {"class" : re.compile(r'^fancybox listing-map')})
        address = " ".join(address['class'][3:-1]).split("mls_number")[0].split("',")[:-1]
        address = ', '.join(list(map(clean, address)))
        address = "{" + address.replace("'", '"') + '}'
        address = json.loads(address)
        address['street'] = address['address']

        if test: print(address)
        return address


    def getExtractions(self): return self.__extractions
