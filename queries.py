from db import config

class Queries(config):

    def __init__(self, dictionary):
        super().__init__()
        self.__extractions = dictionary
        self.cursor = self.mydb.cursor()

    def getUIDaddress(self, test=False):
        self.cursor.execute('SELECT `UID` FROM `addresstbl` WHERE street=%(street)s AND city=%(city)s AND state=%(state)s AND zip=%(zip)s;', (
                self.__extractions['address']
            )
        )
        self.mydb.commit()
        result = self.cursor.fetchall()
        if test: print(f"UID: {result[0][0]}")
        #self.cursor.close()
        self.__extractions['UID']=result[0][0]

    def loadAddress(self, test=False):
        try:
            self.cursor.execute("""
            INSERT INTO addressTBL (`street`, `city`, `state`, `zip`, `county`)
            VALUES (%(street)s, %(city)s, %(state)s, %(zip)s, %(county)s)
            ON DUPLICATE KEY UPDATE `county`=%(county)s
            ;""", self.__extractions['address'])
            self.mydb.commit()
            #self.cursor.close()

            #print(f"LOADED ADDRESS: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Address: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in addressTBL.")

        self.getUIDaddress(test)

    def loadRef(self, href, test=False):
        try:
            self.cursor.execute("INSERT INTO reftbl (`UID`,`href`) VALUES (%(UID)s, %(href)s);", {'UID': self.__extractions['UID'], 'href': href});
            self.mydb.commit()
            #print(f"LOADED REF: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Ref: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in refTBL.")

    def loadDetails(self, test=False):
        self.__extractions['details']['UID'] = self.__extractions['UID']

        try:
            self.cursor.execute("""
            INSERT INTO activetbl (`listdate`, `category`, `currentPrice`, `prevPrice`, `tax`, `baths`, `beds`, `halfbaths`, `basement`, `garage`, `UID`)
            VALUES (%(listdate)s, %(category)s, %(currentprice)s, %(prevprice)s, %(taxes)s, %(fullbaths)s, %(bedrooms)s, %(halfbaths)s, %(basement)s, %(garage)s, %(UID)s)
            ON DUPLICATE KEY UPDATE `listdate`=%(listdate)s, `category`=%(category)s, `currentPrice`=%(currentprice)s, `prevPrice`=%(prevprice)s, `tax`=%(taxes)s, `baths`=%(fullbaths)s, `beds`=%(bedrooms)s, `halfbaths`=%(halfbaths)s, `basement`=%(basement)s, `garage`=%(garage)s
            ;
            """,
                self.__extractions['details']
            )
            self.mydb.commit()
            #self.cursor.close()

            #print(f"LOADED ACTIVE: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Active: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in activetbl.")
            return

    def loadDate(self, date, test=False):
        try:
            self.cursor.execute("""
            INSERT INTO datetbl (`fullDate`,`day`,`month`,`monthShort`,`monthFull`,`year`,`DOW`,`fullDOW`)
            VALUES (%(fullDate)s, %(day)s, %(month)s, %(monthShort)s, %(monthFull)s, %(year)s, %(DOW)s, %(fullDOW)s)
            ;
            """, date)
            self.mydb.commit()
            #self.cursor.close()

            #print(f"LOADED DATE: {date['fullDate']} {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Date: {date['fullDate']} {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in datetbl.")
            return

    def loadLastSold(self, test=False):
        self.__extractions['sold']['UID'] = self.__extractions['UID']
        if(self.__extractions['sold']['date']==None or self.__extractions['sold']['price']==0):
            print(f"NOT FOUND LAST SOLD: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} doesn't have history of price change.")
            return

        try:
            self.cursor.execute("""
            INSERT INTO soldtbl (`UID`, `date`, `price`)
            VALUES (%(UID)s, %(date)s, %(price)s)
            ON DUPLICATE KEY UPDATE `UID`=%(UID)s, `date`=%(date)s, `price`=%(price)s
            ;
            """,
                self.__extractions['sold']
            )
            self.mydb.commit()
            #self.cursor.close()

            #print(f"LOADED LAST SOLD: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Last Sold: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in soldtbl.")
            return
