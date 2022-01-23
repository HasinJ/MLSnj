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
        address = self.__transformAddress()
        if test: print(address)

        self.__extractions = {
            'address': address
        }

    def __transformAddress(self):
        def clean(x):
            x = x.strip()
            if x in ['lat:', 'lng:']: print(x)
            pos = x.index(':')
            x = x[:pos] + '"' + x[pos:]
            return '"' + x

        address = self.__houseSoup.find("a", {"class" : re.compile(r'^fancybox listing-map')})
        address = " ".join(address['class'][3:-1]).split(',')
        address = ', '.join(list(map(clean, address)))
        address = "{" + address.replace("'", '"') + "}"
        #print(address[12:])
        address = json.loads(address)
        return address

    def getExtractions(): return self.__extractions
