import os
import pandas as pd
import requests
import pymysql
from pandas_datareader import data as pdr_data
from bs4 import BeautifulSoup
from datetime import datetime


PWD='ehfvkfdl123@'
DB_NAME='KOR_DB'
KRX_URL='http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
NAVER_URL_BASE='https://finance.naver.com/item/sise_day.nhn?code'#068270&page=1'
USER_AGENT='Mozilla/5.0'



class KoreaDB_manager():


    def __init__(self, vnet=False):
        """ constructor: MariaDB connection & code dictionary generation  """

        self.connection = pymysql.connect(host='localhost', port=3306, db=DB_NAME, 
            user='root', passwd=PWD, autocommit=True)  

        with self.connection.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY (code))
            """
            cursor.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date))
            """
            cursor.execute(sql)

        self.connection.commit()
        self.code_dict = dict()


    def __del__(self):
        """ destructor: MariaDB disconnection   """
        self.connection.close() 


    def getKRXcodes(self):
        """ KRX로부터 상장기업 목록 파일을 읽어와서 데이터프레임으로 반환 """
        url = KRX_URL
        krx = pd.read_html(url, header=0)[0]
        krx = krx[['종목코드', '회사명']]
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})
        krx.code = krx.code.map('{:06d}'.format)
        return krx

    def updateCompanyInfo(self):
        """ 종목코드를 company_info 테이블에 업데이트 한 후 딕셔너리에 저장 """

        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.connection)
        for idx in range(len(df)):
            self.code_dict[df['code'].values[idx]] = df['company'].values[idx]
                    
        with self.connection.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                krx = self.getKRXcodes()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]                
                    sql = f"REPLACE INTO company_info (code, company, last"\
                        f"_update) VALUES ('{code}', '{company}', '{today}')"
                    curs.execute(sql)
                    self.code_dict[code] = company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO company_info "\
                        f"VALUES ({code}, {company}, {today})")
                self.connection.commit()
                print('')              


    def getCode(self, target_name):
        for code, name in self.code_dict.items():
            if name == target_name: 
                return code
            else:
                "Can't find code! please check company name again"

    def getName(self, code):
        return self.code_dict[code]

        


    # --------------------------- Data Crawling --------------------------- #
    def getDataFromYahoo(self, code, start, end):

        return pdr_data.get_data_yahoo(code, start, end)

    def getDataFromNaver(self, code=None, name=None, pages_to_fetch=9999):
        """ crawling data from Naver - update: 2021-01-31 """

        if name==None: name=self.getName(code)
        elif code==None: code=self.getCode(name)

        try:
            url = f'{NAVER_URL_BASE}={code}'
            html = BeautifulSoup(requests.get(url, headers={'User-agent': USER_AGENT}).text, 'lxml')
            pgrr = html.find("td", class_="pgRR")
            
            if pgrr is None: 
                print(f"[ERROR] cannot find last page")
                return None

            s = str(pgrr.a["href"]).split('=')
            lastpage = s[-1] 
            df = pd.DataFrame()

            pages = min(int(lastpage), pages_to_fetch)
            for page in range(1, pages + 1)[:]:
                pg_url = '{}&page={}'.format(url, page)

                df = df.append(pd.read_html(requests.get(pg_url,
                    headers={'User-agent': USER_AGENT}).text)[0])                                          
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                print('[{}] {} ({}) : {:04d}/{:04d} pages are downloading...'.
                    format(tmnow, name, code, page, pages), end="\r")

            df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff'
                ,'시가':'open','고가':'high','저가':'low','거래량':'volume'})
            df['date'] = df['date'].str.replace('.', '-')
            df = df.dropna()
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close',
                'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
            
            return df

        except Exception as e:
            print('=================================================')
            print(f'[ERROR] {__name__} : {e}') 
            print(f'Cannot fetch to Naver data. Please check code or url\ncode:{code}\nurl:{url}')
            print('=================================================')
            return None
    

    
        # with urlopen(url) as doc:
        #     html = BeautifulSoup(doc, 'lxml')
        #     print(html)
        #     pgrr = html.find('td', class_='pgRR')
        #     print(pgrr.a['href'])
        # print(code)
        #return data.get_data_yahoo(code, start, end)

    def replaceIntoDB(self, df, num, code, company):
        """네이버에서 읽어온 주식 시세를 DB에 REPLACE"""
        with self.connection.cursor() as curs:
            for r in df.itertuples():
                sql = f"REPLACE INTO daily_price VALUES ('{code}', "\
                    f"'{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, "\
                    f"{r.diff}, {r.volume})"
                curs.execute(sql)
            self.connection.commit()
            print('[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO daily_'\
                'price [OK]'.format(datetime.now().strftime('%Y-%m-%d'\
                ' %H:%M'), num+1, company, code, len(df)))

    def updateDailyPrice(self, pages_to_fetch):
        """KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트"""  
        for idx, code in enumerate(self.code_dict):
            df = self.getDataFromNaver(code, self.code_dict[code], pages_to_fetch)
            if df is None:
                continue
            self.replaceIntoDB(df, idx, code, self.code_dict[code])   


if __name__ == '__main__':

    data_loader = KoreaDB_manager()
    data_loader.updateCompanyInfo()
    data_loader.updateDailyPrice(1)

    #data_loader.execute_daily()








    # --------------------------- TRASH CAN --------------------------- #


    # def addCodeList(self, code_path):
    #     """ data url: https://dev-kind.krx.co.kr/main.do?method=loadInitPage&scrnmode=1 """

    #     path = code_path
    #     if not os.path.exists(path):
    #         path = KOREA_CODE_URL
    #     try:
    #         df = pd.read_html(path)[0]
    #         df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    #         df.code = df.code.map('{:06d}'.format)
    #         self.code_df = df.sort_values(by='name',ignore_index=True)

    #     except Exception as e: 
    #         print('=================================================')
    #         print(f'[ERROR] {__name__} : {e}') 
    #         print(f'Cannot fetch to code data. Please check code path or url\npath:{code_path}\nurl:{KOREA_CODE_URL}')
    #         print('=================================================')


    # def addCodeList(self, code_path):
    #     """ data url: https://dev-kind.krx.co.kr/main.do?method=loadInitPage&scrnmode=1 """

    #     path = code_path
    #     if not os.path.exists(path):
    #         path = KOREA_CODE_URL
    #     try:
    #         df = pd.read_html(path)[0]
    #         df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    #         df.code = df.code.map('{:06d}'.format)
    #         self.code_df = df.sort_values(by='name',ignore_index=True)

    #     except Exception as e: 
    #         print('=================================================')
    #         print(f'[ERROR] {__name__} : {e}') 
    #         print(f'Cannot fetch to code data. Please check code path or url\npath:{code_path}\nurl:{KOREA_CODE_URL}')
    #         print('=================================================')

