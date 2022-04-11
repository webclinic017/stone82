from matplotlib.pyplot import table
import pandas as pd
from bs4 import BeautifulSoup
from pandas_datareader import data as pdr_data
import urllib
import pymysql
import calendar
import time
import json
import os
import requests
import sys
import dart_fss as dart
from datetime import datetime, timedelta
import concurrent.futures
from tqdm import tqdm
import time
import asyncio
import aiohttp
import aiomysql
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
from io import BytesIO


KRX_URL = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
NAVER_URL_BASE = 'https://finance.naver.com/item/sise_day.nhn?code'  # 068270&page=1'
USER_AGENT = 'Mozilla/5.0'
SLEEP_TIME = 0.1


class KoreaDB_manager():

    def __init__(
        self, host, db_name, pwd,
        user='root',
        port=3306,
        autocommit=True,
        vnet=False
    ):
        """ constructor: MariaDB connection & code dictionary generation  """

        self.connection = pymysql.connect(
            host=host,
            port=port,
            db=db_name,
            user=user,
            passwd=pwd,
            autocommit=autocommit
        )
        self.start_date = '19950502'
        self.code_dict = dict()
        # self.updateCompanyInfo()

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

    def getCorpCodes(self, api_key, xml_path='CORPCODE.xml'):

        if not os.path.isfile(xml_path):

            URL_BASE = "https://opendart.fss.or.kr/api/corpCode.xml"

            params = {
                'crtfc_key': api_key
            }

            res = requests.get(URL_BASE, params=params)

            pwd = os.getcwd()

            corp_zip_file = os.path.join(pwd, 'corp_code.zip')
            with open(corp_zip_file, 'wb') as fp:
                fp.write(res.content)
            zf = zipfile.ZipFile(corp_zip_file, 'r')
            zf.extractall()

        xml_path = os.path.abspath('./CORPCODE.xml')
        tree = ET.parse(xml_path)
        root = tree.getroot()
        tags_list = root.findall('list')

        def convert(tag: ET.Element) -> dict:
            conv = {}
            for child in list(tag):
                conv[child.tag] = child.text

            return conv

        tags_list_dict = [convert(x) for x in tags_list]
        df = pd.DataFrame(tags_list_dict)

        return df

    def stockCode2corpCode(self, stock_code):
        result = self.corp_df[self.corp_df['stock_code']
                              == stock_code]['corp_code'].to_numpy()
        return result[0] if len(result) == 1 else None

    async def asyncUpdateCompanyInfo(self, params: dict, start_date: str = '19950502'):

        """ 종목코드를 company_info 테이블에 업데이트 한 후 딕셔너리에 저장 """

        with self.connection.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')

            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                start_date = params['start_date'] if 'start_date' in params else start_date
                price_table = params['price_table'] if 'price_table' in params else 'daily_price'
                info_table = params['info_table'] if 'info_table' in params else 'company_info'

                start_date = datetime.strptime(start_date, '%Y%m%d')
                print(f"[D] asyncUpdateCompanyInfo -> update company info .. ")
                print(
                    f"[D] asyncUpdateCompanyInfo -> start_date: {start_date}")
                print(
                    f"[D] asyncUpdateCompanyInfo -> price_table: {price_table}")
                print(
                    f"[D] asyncUpdateCompanyInfo -> info_table: {info_table}")

                sql = f""" SELECT code,market,name FROM {price_table} WHERE date >= '{start_date}' """
                df = pd.read_sql(sql, self.connection)
                df = df.drop_duplicates()
                print(f"[D] asyncUpdateCompanyInfo -> total df len: {len(df)}")

                connect = await aiomysql.connect(
                    host=os.environ.get('MYSQL_HOST'),
                    db='KOR_DB',
                    password=os.environ.get('MYSQL_ROOT_PASSWORD'),
                    user=os.environ.get('MYSQL_USER'),
                )
                cur = await connect.cursor()
                for r in df.itertuples():
                    sql = f"""
                    REPLACE INTO {info_table} (code, name, market, last_update) VALUES ('{r.code}', '{r.name}', '{r.market}', '{today}') 
                    """
                    await cur.execute(sql)
                    print(f"[{today}] {r.code} REPLACE INTO {info_table}")

                await connect.commit()
                await cur.close()
                connect.close()
                print(f"[D] asyncUpdateCompanyInfo -> done!")

    async def calAdjPrice(self, code, connect, start_date, end_date):
        # await sem.acquire()

        cur = await connect.cursor()
        sql = f"""
            SELECT ref_close, ref_open, close, adj_close, split_coefficient, date
            FROM daily_price 
            WHERE code = '{code}'
            AND date BETWEEN '{start_date}' AND '{end_date}'
        """
        data = pd.read_sql(sql, self.connection)
        if data['ref_close'].iloc[0] == 0:
            data['ref_close'].iloc[0] = data['ref_open'].iloc[1]
        data['split_coefficient'] = (
            data['ref_close'] / data['ref_open'].shift(-1)).fillna(1)
        data['split_coefficient'] = data['split_coefficient'].iloc[::-
                                                                   1].cumprod().iloc[::-1]
        data['adj_close'] = data['close'] / data['split_coefficient']

        is_null = data['adj_close'].isna().values.any()
        if not is_null and data.shape[0] != 0:
            for r in data.itertuples():
                sql = f"""
                UPDATE daily_price SET 
                    adj_close = '{r.adj_close}', 
                    split_coefficient = '{r.split_coefficient}'
                WHERE 
                    code = '{code}' and date = '{r.date}'
                """
                await cur.execute(sql)

            print(f"[I] code: {code} applied!")
            # print(f"[E] code: {code} had wrong value -> skipped!")

        else:
            print(
                f"[W] code: {code} invalid -> [ shape: {data.shape} / is_null: {is_null} ] skipped!")

        await connect.commit()
        await cur.close()
        # sem.release()

    async def asyncUpdateAdjPrice(self, params: dict):

        start_date = params['start_date'] if 'start_date' in params else '2000-01-01'
        end_date = params['end_date'] if 'end_date' in params else str(
            datetime.today().date())

        print(f"[D] start_date: {start_date}")
        print(f"[D] end_date: {end_date}")

        with self.connection.cursor() as curs:
            sql = f""" SELECT (code) FROM company_info"""
            df = pd.read_sql(sql, self.connection)

        # sem = asyncio.Semaphore(50)
        connect = await aiomysql.connect(
            host=os.environ.get('MYSQL_HOST'),
            db='KOR_DB',
            password=os.environ.get('MYSQL_ROOT_PASSWORD'),
            user=os.environ.get('MYSQL_USER'),
        )

        code_list = df['code'].to_list()
        future = [asyncio.ensure_future(self.calAdjPrice(
            code, connect, start_date, end_date)) for code in code_list]
        await asyncio.gather(*future)
        connect.close()

    def getCodes(self):
        return self.code_dict

    # -------------------------------------------------
    # Data crawling modules
    # ------------------------------------------------

    def getDataFromDARTtoCSV(self, code):
        fsdata_dir = 'fsdata'
        bgn_de = 20000101
        os.makedirs(fsdata_dir, exist_ok=True)

        dart.set_api_key(api_key="8ba06a012b644df0819f3035d024f905c71e0165")
        corp_list = dart.get_corp_list()
        data = corp_list.find_by_stock_code(code)

        print(f"[D] code: {code}")
        print(f"[D] type(data): {type(data)}")

        tp_list = ['bs', 'is', 'cis', 'cf']
        try:
            fs = data.extract_fs(
                bgn_de=20000101, report_tp='quarter')
        except:
            pass

        for tp in tp_list:
            filepath = os.path.join(
                fsdata_dir, f"{code}_{tp}.csv")
            df = fs[tp]
            if df is not None:
                df.to_csv(filepath, encoding="euc-kr")
                print(f"[D] save file : {filepath}")
            else:
                print(f"[E] skip file: {filepath}")

    async def asyncFetchDataFromKRX(self, date):
        date = date.replace('-', '')

        gen_otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
        down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

        gen_otp_data = {
            'locale': 'ko_KR',
            'mktId': 'ALL',
            'trdDd': date,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false',
            'name': 'fileDown',
            'url': 'dbms/MDC/STAT/standard/MDCSTAT01501'
        }

        gen_otp_ref_data = {
            'locale': 'ko_KR',
            'mktId': 'STK',
            'strtDd': date,
            'endDd': date,
            'adjStkPrc_check': 'Y',
            'adjStkPrc': '2',
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false',
            'name': 'fileDown',
            'url': 'dbms/MDC/STAT/standard/MDCSTAT01602'
        }

        headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

        async with aiohttp.ClientSession() as session:
            async with session.get(gen_otp_url, headers=headers, params=gen_otp_data) as res_otp:
                base_code = await res_otp.text()

            async with session.get(gen_otp_url, headers=headers, params=gen_otp_ref_data) as res_otp:
                ref_code = await res_otp.text()

            async with session.post(down_url, data={'code': base_code}, headers=headers) as res_down:
                base_content = await res_down.content.read()

            async with session.post(down_url, data={'code': ref_code}, headers=headers) as res_down:
                ref_content = await res_down.content.read()

            df = pd.read_csv(BytesIO(base_content), encoding='EUC-KR')
            ref_df = pd.read_csv(BytesIO(ref_content), encoding='EUC-KR')
            ref_df = ref_df[['종목코드', '시작일 기준가', '종료일 종가']]
            df = pd.merge(left=df, right=ref_df, how='left', on='종목코드')
            df = df.rename(columns={
                '종목코드': 'code',
                '종목명': 'name',
                '시장구분': 'market',
                '날짜': 'date',
                '종가': 'close',
                '대비': 'diff',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume',
                '거래대금': 'amount',
                '상장주식수': 'stock_num',
                '시가총액': 'cap',
                '시작일 기준가': 'ref_open',
                '종료일 종가': 'ref_close'})

            df['date'] = datetime.strptime(date, '%Y%m%d').date()

            df = df[['code', 'date', 'name', 'market', 'close', 'diff', 'open', 'high',
                     'low', 'volume', 'amount', 'stock_num', 'cap', 'ref_open', 'ref_close']]
            df = df.dropna(subset=['code', 'date', 'name', 'market', 'close', 'diff',
                           'open', 'high', 'low', 'volume', 'amount', 'stock_num', 'cap'])

            df = df.fillna(1)

            return df

    def crawlDataFromKRX(self, date):

        date = date.replace('-', '')
        # STEP 01: Generate OTP
        gen_otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"

        gen_otp_data = {
            'locale': 'ko_KR',
            'mktId': 'ALL',
            'trdDd': date,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false',
            'name': 'fileDown',
            'url': 'dbms/MDC/STAT/standard/MDCSTAT01501'
        }
        headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
        r = requests.get(gen_otp_url, headers=headers, params=gen_otp_data)
        code = r.text

        down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
        # requests Module의 post함수를 이용하여 해당 url에 접속하여 otp코드를 제출함
        down_sector_KS = requests.post(
            down_url, {'code': code}, headers=headers)
        # 다운 받은 csv파일을 pandas의 read_csv 함수를 이용하여 읽어 들임.
        # read_csv 함수의 argument에 적합할 수 있도록 BytesIO함수를 이용하여 바이너 스트림 형태로 만든다.
        df = pd.read_csv(BytesIO(down_sector_KS.content), encoding='EUC-KR')
        df = df.rename(columns={
            '종목코드': 'code',
                    '종목명': 'name',
                    '시장구분': 'market',
                    '날짜': 'date',
                    '종가': 'close',
                    '대비': 'diff',
                    '시가': 'open',
                    '고가': 'high',
                    '저가': 'low',
                    '거래량': 'volume',
                    '거래대금': 'amount',
                    '상장주식수': 'stock_num',
                    '시가총액': 'cap'})
        df = df[['code', 'name', 'market', 'close', 'diff', 'open',
                 'high', 'low', 'volume', 'amount', 'stock_num', 'cap']]
        df = df.dropna()

        return df

    # DEPRECATED
    def crawlDataFromYahoo(self, code, start, end=None):

        return pdr_data.get_data_yahoo(code, start, end)

    # DEPRECATED
    def crawlDataFromNaver(self, code=None, name=None, pages_to_fetch=9999):
        """ crawling data from Naver - update: 2021-01-31 """

        # if name == None:
        #     name = self.getName(code)

        # if code == None:
        #     code = self.getCode(name)

        try:
            url = f'{NAVER_URL_BASE}={code}'
            html = BeautifulSoup(requests.get(
                url, headers={'User-agent': USER_AGENT}).text, 'lxml')
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

                df = df.append(
                    pd.read_html(
                        requests.get(pg_url, headers={'User-agent': USER_AGENT}).text)[0]
                )
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                print('[{}] {} ({}) : {:04d}/{:04d} pages are downloading...'.
                      format(tmnow, name, code, page, pages), end="\r")

            df = df.rename(
                columns={
                    '날짜': 'date',
                    '종가': 'close',
                    '전일비': 'diff',
                    '시가': 'open',
                    '고가': 'high',
                    '저가': 'low',
                    '거래량': 'volume'})
            df['date'] = df['date'].str.replace('.', '-')
            df = df.dropna()
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[[
                'close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)

            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]

            return df

        except Exception as e:
            print('=================================================')
            print(f'[ERROR] {__name__} : {e}')
            print(
                f'Cannot fetch to Naver data. Please check code or url\ncode:{code}\nurl:{url}')
            print('=================================================')
            return None

    def replaceIntoDB(self, df, date, TABLE='daily_price'):
        """ DataFrame --> DB 에 REPLACE """

        with self.connection.cursor() as curs:
            for r in df.itertuples():
                sql = f"""
                    REPLACE INTO {TABLE} (
                        code, date, name, open, high, low, close, diff, volume, market, amount, stock_num, cap
                    ) VALUES (
                        '{str(r.code).zfill(6)}', '{date}', '{r.name}', '{r.open}', '{r.high}', '{r.low}', '{r.close}', '{r.diff}', '{r.volume}', '{r.market}', '{r.amount}', '{r.stock_num}', '{r.cap}'
                    )
                """
                curs.execute(sql)
            self.connection.commit()
            print(
                f'[{date}]: {len(df)} rows > REPLACE INTO daily_price [OK]')

    def call_back(self, x):
        if x is not None:
            self.df = self.df.append(x, ignore_index=True)
            print(x)

        self.n += 1
        sys.stdout.write('\r%s/%s' % (self.n, '?'))

    def updateDailyPrice(self, date):
        """ KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트 """

        # TODO: need to make parallel processing
        df = self.crawlDataFromKRX(date)
        if df.shape[0] != 0:
            self.replaceIntoDB(df, date)
        else:
            print(f"[{date}]: skipped!")

    async def asyncUpdateDailyPrice(self, params: dict):
        """
            params list:
            - start_date: crawling date since {start_date} (default: '19950502')
            - table: mysql database table name (default: daily_price)
        """
        start_date = params['start_date'] if 'start_date' in params else '19950502'
        table = params['table'] if 'table' in params else 'daily_price'
        print(f"[D] asyncUpdateDailyPrice -> start_date: {start_date}")
        print(f"[D] asyncUpdateDailyPrice -> table_name: {table}")

        START = datetime.strptime(start_date, '%Y%m%d')  # 1
        TODAY = datetime.today()
        DAYS = (TODAY - START).days
        # DAYS = 10 # DEBUG
        df_list = []

        for day in range(DAYS):
            date = (START + timedelta(days=day)).strftime('%Y-%m-%d')
            future = asyncio.ensure_future(self.asyncFetchDataFromKRX(date))
            df = await asyncio.gather(future)
            await asyncio.sleep(SLEEP_TIME)

            if df[0].shape[0] != 0:
                df_list.append(df[0])
            else:
                print(f"[{date}]: skipped!")

            if day % 100 == 0:
                print(f'days .. [{day}/{DAYS}]')

        connect = await aiomysql.connect(
            host=os.environ.get('MYSQL_HOST'),
            db='KOR_DB',
            password=os.environ.get('MYSQL_ROOT_PASSWORD'),
            user=os.environ.get('MYSQL_USER'),
        )

        cur = await connect.cursor()

        for i, df in enumerate(df_list):
            for r in df.itertuples():
                # if str(r.code).zfill(6) == '950210':
                #     print(r)
                sql = f"""
                REPLACE INTO {table} (
                    code, date, name, open, high, low, close, diff, volume, market, amount, stock_num, cap, ref_open, ref_close
                ) VALUES (
                    '{str(r.code).zfill(6)}', '{r.date}', '{r.name}', '{r.open}', '{r.high}', '{r.low}', '{r.close}', '{r.diff}', '{r.volume}', '{r.market}', '{r.amount}', '{r.stock_num}', '{r.cap}', '{r.ref_open}', '{r.ref_close}'
                )
                """
                await cur.execute(sql)
            if i % 100 == 0:
                print(f'progress is [{i}/{len(df_list)}]')

        await connect.commit()
        await cur.close()
        connect.close()

    def runAsyncUpdate(self, funct, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(funct(kwargs))

    def updateDailyPriceAll(self, start_year='19950502'):

        START = datetime.strptime(start_year, '%Y%m%d')  # 1
        TODAY = datetime.today()
        DAYS = (TODAY - START).days
        DAYS = 30

        for i in range(DAYS):
            date = (START + timedelta(days=i)).strftime('%Y-%m-%d')
            self.updateDailyPrice(date)

    # DEPRECATED
    def updateDailyPrice_(self, pages_to_fetch):
        """KRX 상장법인의 주식 시세를 네이버로부터 읽어서 DB에 업데이트"""

        # TODO: need to make parallel processing

        t_stamp01 = time.time()
        for idx, code in enumerate(self.code_dict):
            df = self.crawlDataFromNaver(
                code, self.code_dict[code], pages_to_fetch)
            if df is None:
                continue
            self.replaceIntoDB(df, idx, code, self.code_dict[code])
        t_stamp02 = time.time()

    # DEPRECATED
    def executeDaily(self, config_path):
        """ 실행 즉시 및 매일 오후 다섯시에 daily_price 테이블 업데이트 """
        self.updateCompanyInfo()

        try:
            with open(config_path, 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:

            with open('config/korDB_base.json', 'w') as out_file:
                pages_to_fetch = 100
                config = {'pages_to_fetch': 1}
                json.dump(config, out_file)
        self.updateDailyPrice(pages_to_fetch)

        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year=tmnow.year+1, month=1, day=1,
                                   hour=17, minute=0, second=0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace(month=tmnow.month+1, day=1, hour=17,
                                   minute=0, second=0)
        else:
            tmnext = tmnow.replace(day=tmnow.day+1, hour=17, minute=0,
                                   second=0)
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds
        t = Timer(secs, self.execute_daily)
        print("Waiting for next update ({}) ... ".format(tmnext.strftime
                                                         ('%Y-%m-%d %H:%M')))
        t.start()
