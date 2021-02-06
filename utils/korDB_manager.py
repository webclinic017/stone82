import os
import pandas as pd
from pandas_datareader import data as pdr_data
from bs4 import BeautifulSoup
from datetime import datetime
import requests



KOREA_CODE_URL='https://dev-kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
NAVER_URL_BASE='https://finance.naver.com/item/sise_day.nhn?code'#068270&page=1'
USER_AGENT='Mozilla/5.0'

class KoreaDB_manager():


    def __init__(self, vnet=False):
        """ constructor: MariaDB connection & code dictionary generation  """
        self.stock_type = {
            'kospi': 'stockMkt',
            'kosdaq': 'kosdaqMkt'
            } 
        self.kospi_codes=None
        self.kosdaq_codes=None

        self.code_df=None


    def __del__(self):
        """ destructor: MariaDB disconnection   """

        pass



    def addCodeList(self, code_path):
        """ data url: https://dev-kind.krx.co.kr/main.do?method=loadInitPage&scrnmode=1 """

        path = code_path
        if not os.path.exists(path):
            path = KOREA_CODE_URL
        try:
            df = pd.read_html(path)[0]
            df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
            df.code = df.code.map('{:06d}'.format)
            self.code_df = df.sort_values(by='name',ignore_index=True)

        except Exception as e: 
            print('=================================================')
            print(f'[ERROR] {__name__} : {e}') 
            print(f'Cannot fetch to code data. Please check code path or url\npath:{code_path}\nurl:{KOREA_CODE_URL}')
            print('=================================================')


        
    def getCodeList(self):
        return self.code_df

    def getCode(self, name):
        return self.code_df.query("name=='{}'".format(name))['code'].to_string(index=False).strip()

    def getName(self, name):
        return self.code_df.query("code=='{}'".format(name))['name'].to_string(index=False).strip()
        

    def getCodeList_beta(self, market):
        
        market_type = self.stock_type[market]
        download_link = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
        download_link = download_link + '?method=download'
        download_link = download_link + '&marketType=' + market_type
        df = pd.read_html(download_link, header=0)[0]

        if market == 'kospi':
            df['종목코드'] = df['종목코드'].map('{:06d}.KS'.format)
            df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
            self.kospi_codes = df

            return self.kospi_codes

        elif market == 'kosdaq':
            df['종목코드'] = df['종목코드'].map('{:06d}.KQ'.format)
            df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
            self.kosdaq_codes = df

            return self.kospi_codes



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

if __name__ == 'main':

    data_loader = KoreaDB_manager()
    data_loader.execute_daily()

