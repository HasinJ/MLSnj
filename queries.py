from db import config

class Queries(config):

    def __init__(self, dictionary):
        super().__init__()
        self.__extractions = dictionary
        self.cursor = self.mydb.cursor()

    def getUIDaddress(self, test=False):
        self.cursor.execute('SELECT `UID` FROM `addresstbl` WHERE street=%(street)s AND city=%(city)s AND state=%(state)s AND zip=%(zip)s', (
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
            self.cursor.execute('INSERT INTO addressTBL (`street`, `city`, `state`, `zip`) VALUES (%(street)s, %(city)s, %(state)s, %(zip)s);', self.__extractions['address'])
            self.mydb.commit()
            #self.cursor.close()

            print(f"LOADED ADDRESS: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Address: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in addressTBL.")

        self.getUIDaddress(test)

    def loadRef(self, href, test=False):
        try:
            self.cursor.execute("INSERT INTO reftbl (`UID`,`href`) VALUES (%(UID)s, %(href)s)", {'UID': self.__extractions['UID'], 'href': href});
            self.mydb.commit()
            print(f"LOADED REF: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Ref: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in refTBL.")

    def loadDetails(self, test=False):
        self.__extractions['details']['UID'] = self.__extractions['UID']

        try:
            self.cursor.execute("""
            INSERT INTO detailstbl (`category`, `currentPrice`, `tax`, `baths`, `beds`, `halfbaths`, `basement`, `garage`, `UID`)
            VALUES (%(category)s, %(currentprice)s, %(taxes)s, %(fullbaths)s, %(bedrooms)s, %(halfbaths)s, %(basement)s, %(garage)s, %(UID)s)
            ON DUPLICATE KEY UPDATE `category`=%(category)s, `currentPrice`=%(currentprice)s, `tax`=%(taxes)s, `baths`=%(fullbaths)s, `beds`=%(bedrooms)s, `halfbaths`=%(halfbaths)s, `basement`=%(basement)s, `garage`=%(garage)s
            ;
            """,
                self.__extractions['details']
            )
            self.mydb.commit()
            #self.cursor.close()

            print(f"LOADED DETAILS: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} inserted.")

        except self.MySQLdb._exceptions.IntegrityError: #https://stackoverflow.com/questions/4205181/insert-into-a-mysql-table-or-update-if-exists
            print(f"Details: {self.__extractions['address']['street']}, {self.__extractions['address']['state']} exists in detailstbl.")
            return
