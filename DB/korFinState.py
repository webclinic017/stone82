import numpy as np
import pymysql
import os
import re
import requests
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

SLEEP_TIME = 60


class KorFinStateModel():

    def __init__(
            self, db, pwd, dart_key, host='localhost', user='root', port=3306, autocommit=True, vnet=False) -> None:

        self.dart_key = dart_key
        self.code_dict = dict()

        self.connection = pymysql.connect(
            host=host,
            port=port,
            db=db,
            user=user,
            passwd=pwd,
            autocommit=autocommit
        )
        self.sql_init()
        self.getCompanyInfo()
        self.corp_df = self.getCorpCodes(self.dart_key)

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.connection.close()

    def sql_init(self):
        with self.connection.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS finance_state (
                stock_code VARCHAR(20),
                name VARCHAR(40),
                report_code VARCHAR(20),
                year VARCHAR(20),
                quarter VARCHAR(20),
                total_num VARCHAR(20),
                normal_num VARCHAR(20),
                prior_num VARCHAR(20),
                price VARCHAR(20),
                revenue VARCHAR(20),
                gp VARCHAR(20),
                op_income VARCHAR(20),
                profit VARCHAR(20),
                assets VARCHAR(20),
                liability VARCHAR(20),
                equity VARCHAR(20),
                curr_assets VARCHAR(20),
                noncurr_assets VARCHAR(20),
                curr_liability VARCHAR(20),
                capital VARCHAR(20),
                op_cashflow VARCHAR(20),
                invest_cashflow VARCHAR(20),
                fin_cashflow VARCHAR(20),
                capex VARCHAR(20),
                FCF VARCHAR(20),
                op_income_ratio VARCHAR(20),
                total_income_ratio VARCHAR(20),
                EV_EBIT VARCHAR(20),
                ROE VARCHAR(20),
                ROA VARCHAR(20),
                ROC VARCHAR(20),
                liability_ratio VARCHAR(20),
                reserve_ratio VARCHAR(20),
                EPS VARCHAR(20),
                PER VARCHAR(20),
                BPS VARCHAR(20),
                PSR VARCHAR(20),
                PBR VARCHAR(20),
                GP_A VARCHAR(20),
                last_update DATE,
                PRIMARY KEY (stock_code,report_code,year))
            """
            cursor.execute(sql)

        self.connection.commit()

    def getCompanyInfo(self):
        """company_info 테이블에서 읽어와서 companyData와 codes에 저장"""
        sql = "SELECT * FROM company_info"
        companyInfo = pd.read_sql(sql, self.connection)
        for idx in range(len(companyInfo)):
            self.code_dict[companyInfo['code'].values[idx]
                           ] = companyInfo['company'].values[idx]

    def getDailyPrice(self, code, start_date=None, end_date=None):
        """KRX 종목의 일별 시세를 데이터프레임 형태로 반환
            - code       : KRX 종목코드('005930') 또는 상장기업명('삼성전자')
            - start_date : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
            - end_date   : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """

        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d')
            print("start_date is initialized to '{}'".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            if start_lst[0] == '':
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                print(f"ValueError: start_year({start_year:d}) is wrong.")
                return
            if start_month < 1 or start_month > 12:
                print(f"ValueError: start_month({start_month:d}) is wrong.")
                return
            if start_day < 1 or start_day > 31:
                print(f"ValueError: start_day({start_day:d}) is wrong.")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"

        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("end_date is initialized to '{}'".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            if end_lst[0] == '':
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1800 or end_year > 2200:
                print(f"ValueError: end_year({end_year:d}) is wrong.")
                return
            if end_month < 1 or end_month > 12:
                print(f"ValueError: end_month({end_month:d}) is wrong.")
                return
            if end_day < 1 or end_day > 31:
                print(f"ValueError: end_day({end_day:d}) is wrong.")
                return
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"

        code_list = list(self.code_dict.keys())
        name_list = list(self.code_dict.values())

        if code in code_list:
            pass
        elif code in name_list:
            idx = name_list.index(code)
            code = code_list[idx]
        else:
            print(f"ValueError: Code({code}) doesn't exist.")
        sql = f"SELECT * FROM daily_price WHERE code = '{code}'"\
            f" and date >= '{start_date}' and date <= '{end_date}'"
        df = pd.read_sql(sql, self.connection)
        df.index = df['date']
        df = df.drop(['code', 'date'], axis=1)
        return df

    # Function list
    def stockCode2corpCode(self, stock_code):
        """ 주식 종목 코드 --> 재무제표 기업코드 변환 """
        result = self.corp_df[self.corp_df['stock_code']
                              == stock_code]['corp_code'].to_numpy()
        return result[0] if len(result) == 1 else None

    def getTotalStock(self, corp_code, bsns_year, report_code):
        """ 전체 주식수 반환 함수 """
        URL = "https://opendart.fss.or.kr/api/stockTotqySttus.json"
        params = {
            'crtfc_key': self.dart_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': report_code
        }

        res = requests.get(URL, params=params).json()

        if 'list' not in res:
            return None
        return pd.DataFrame(res['list'])

    def getCorpCodes(self, api_key, xml_path='CORPCODE.xml'):
        """ 기업 고유 코드 불러오는 함수 """

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

        xml_path = os.path.abspath(xml_path)
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

    def getFinState(self, corp_code, bsns_year, report_code='11011'):
        """ DART API로 부터 재무제표 불러오는 함수 """
        URL = 'https://opendart.fss.or.kr/api/'
        URL += 'fnlttMultiAcnt.json' if ',' in corp_code else 'fnlttSinglAcnt.json'

        params = {
            'crtfc_key': self.dart_key,
            'corp_code': corp_code,
            'bsns_year':  bsns_year,   # 사업년도
            'reprt_code': report_code,  # "11011": 사업보고서
        }

        res = requests.get(URL, params=params).json()

        if 'list' not in res:
            return None
        return pd.DataFrame(res['list'])

    def getFinStateAll(self, corp_code, bsns_year, report_code='11011', fs_div='CFS'):
        """ DART API로 부터 전체 재무제표 불러오는 함수 """

        URL = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
        """
        report_code:
            - "11013": 1분기보고서
            - "11012": 반기보고서
            - "11014": 3분기보고서
            - "11011": 사업보고서
        fs_div:
            - CFS: 연결재무제표
            - OFS: 재무제표
        """
        params = {
            'crtfc_key': self.dart_key,
            'corp_code': corp_code,
            'bsns_year':  bsns_year,
            'reprt_code': report_code,
            'fs_div': fs_div,
        }

        res = requests.get(URL, params=params).json()

        if 'list' not in res:
            return None
        return pd.DataFrame(res['list'])

    def showFinState(self, state):
        for key, val in state.items():
            print(f"{key}:\t{val}")

    def checkIsNum(self, string: str) -> bool:
        string = str(string)
        if re.match(r"\-?[0-9\.]+", string):
            return True
        else:
            return False

    def checkLen(self, df: pd.DataFrame) -> bool:
        return True if len(df) == 1 else False

    def rmDupl(self, data: list) -> list:
        """ 중복인자 제거 """
        return list(set(data))

    def doCheck(self, data, name="data"):

        if self.checkLen(data):
            data = data[0]
        else:
            print(f"[E] {name} len : {len(data)}")
            return None

        if self.checkIsNum(data):
            data = int(data)
            print(f"[D] {name}: {data}")

        else:
            print(f"[E] {name}: None")

            return None

        return data

    def getStockNum(self, df):
        """ 주식수 반환 함수 """

        total_stocks = df.loc[
            df['se'].isin(['합계'])
        ]['distb_stock_co'].to_numpy()[0].replace(',', '')
        try:
            searchfor = ['보통주', '의결권 있는']
            normal_stocks = df.loc[
                df['se'].str.contains("|".join(searchfor))
            ]['distb_stock_co'].to_numpy()[0].replace(',', '')  # 보통주
        except:
            normal_stocks = None

        try:
            searchfor = ['우선주', '의결권 없는']

            prior_stocks = df.loc[
                df['se'].str.contains("|".join(searchfor))
            ]['distb_stock_co'].to_numpy()[0].replace(',', '')
        except:
            prior_stocks = None

        total_stocks = int(total_stocks) if self.checkIsNum(
            total_stocks) else 0
        normal_stocks = int(normal_stocks) if self.checkIsNum(
            normal_stocks) else 0
        prior_stocks = int(prior_stocks) if self.checkIsNum(
            prior_stocks) else 0

        print(f"[D] 주식수(합계): {total_stocks}")
        print(f"[D] 보통주: {normal_stocks}")
        print(f"[D] 우선주: {prior_stocks}")

        if prior_stocks == None:
            prior_stocks = 0

        return total_stocks, normal_stocks, prior_stocks

    def getEquity(self, df):
        """ 자본 총계 반환 함수 """
        data = df.loc[
            df['sj_div'].isin(['BS']) &
            (df['account_id'].isin(['ifrs-full_Equity']) |
             df['account_id'].isin(['ifrs_Equity'])),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 자본 len: {len(data)}")
            print(f"[I] serching other equity value step 1 ..")

            data = df.loc[
                df['sj_div'].isin(['BS']) &
                df['account_id'].isin(
                    ['ifrs-full_EquityAttributableToOwnersOfParent']),
                'thstrm_amount'
            ].to_numpy()

        # condition 2
        if not self.checkLen(data):
            print(f"[W] 자본 len: {len(data)}")
            print(f"[I] serching other equity value step 2 ..")

            searchfor = ['^([^가-힣]+)?자본([^부채].)*총계']

            data = df.loc[
                df['sj_div'].isin(['BS']) &
                df['account_nm'].str.contains("|".join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '자본')

    def getLiability(self, df):
        """ 부체총계 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_Liabilities']) |
            df['account_id'].isin(['ifrs_Liabilities']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 부채 len: {len(data)}")
            print(f"[I] serching other liability value step 1 ..")

            searchfor = ['^([^가-힣]+)?부채(.)*총계']

            data = df.loc[
                df['sj_div'].isin(['BS']) &
                df['account_nm'].str.contains("|".join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '부채')

    def getProfit(self, df):
        """ 당기순이익 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_ProfitLossAttributableToOwnersOfParent']) |
            df['account_id'].isin(
                ['ifrs_ProfitLossAttributableToOwnersOfParent']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 당기순이익 len: {len(data)}")
            print(f"[I] serching other profit value step 1 ..")

            searchfor = ['^당기(.)*순이익', '^연결당기순이익']

            index = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor)) |
                 df['account_id'].isin(['ifrs-full_ProfitLoss'])) &
                df['sj_div'].isin(['CIS'])
            ].index.to_numpy()

            temp = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor)) |
                 df['account_id'].isin(['ifrs-full_ProfitLoss'])) &
                df['sj_div'].isin(['CIS'])
            ]
            print(temp)
            if self.checkLen(index):
                index = index[0]
                searchfor = ['지배기업']

                sub_df = df.loc[[index+1, index+2]]
                data = sub_df.loc[
                    df['account_nm'].str.contains('|'.join(searchfor)),
                    'thstrm_amount'
                ].to_numpy()
        # condition 2
        if not self.checkLen(data):
            print(f"[W] 당기순이익 len: {len(data)}")
            print(f"[I] serching other profit value step 2 ..")

            searchfor_nm = ['^([^가-힣]+)?당기(.)*순이익(\(손실\))?$',
                            '^([^가-힣]+)?연결당기순이익(\(손실\))?$']
            searchfor_id = ['^ifrs_ProfitLoss$', '^ifrs-full_ProfitLoss$']

            data = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor_nm)) |
                 df['account_id'].str.contains('|'.join(searchfor_id))) &
                df['sj_div'].isin(['CIS']),
                'thstrm_amount'
            ].to_numpy()
            temp = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor_nm)) |
                 df['account_id'].str.contains('|'.join(searchfor_id))) &
                df['sj_div'].isin(['CIS'])
            ]
            print(temp)
            data = self.rmDupl(data)

        # condition 3
        if not self.checkLen(data):
            print(f"[W] 당기순이익 len: {len(data)}")
            print(f"[I] serching other profit value step 3 ..")

            searchfor_nm = ['^([^가-힣]+)?당기(.)*순이익(\(손실\))?$',
                            '^([^가-힣]+)?연결당기순이익(\(손실\))?$']
            searchfor_id = ['^dart_ProfitLossForStatementOfCashFlows$', ]

            data = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor_nm)) |
                 df['account_id'].str.contains('|'.join(searchfor_id))) &
                df['sj_div'].isin(['CF']),
                'thstrm_amount'
            ].to_numpy()
            temp = df.loc[
                (df['account_nm'].str.contains('|'.join(searchfor_nm)) |
                 df['account_id'].str.contains('|'.join(searchfor_id))) &
                df['sj_div'].isin(['CF'])
            ]
            print(temp)
            data = self.rmDupl(data)

        return self.doCheck(data, '당기순이익')

    def getRevenue(self, df):
        """ 매출액 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_Revenue']) |
            df['account_id'].isin(['ifrs_Revenue']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 매출액 len: {len(data)}")
            print(f"[I] serching other revenue value step 1 ..")
            searchfor = ['^([^가-힣]+)?매출액']
            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        # condition 2
        if not self.checkLen(data):
            print(f"[W] 매출액 len: {len(data)}")
            print(f"[I] serching other revenue value step 2 ..")
            searchfor = ['^([^가-힣]+)?영업수익']
            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '매출액')

    def getGP(self, df):
        """ 매출총이익 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_GrossProfit']) |
            df['account_id'].isin(['ifrs_GrossProfit']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, '매출총이익')

    def getOpIncome(self, df):
        """ 영업이익 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['dart_OperatingIncomeLoss']),
            'thstrm_amount'
        ].to_numpy()

        if not self.checkLen(data):
            print(f"[W] opIncome len: {len(data)}")
            print(f"[I] serching other op_income value step 1 ..")
            searchfor = ['^([^가-힣]+)?영업이익$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '영업이익')

    def getCurrAssets(self, df):
        """ 유동자산 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CurrentAssets']) |
            df['account_id'].isin(['ifrs_CurrentAssets']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, "유동자산")

    def getNonCurrAssets(self, df):
        """ 비유동자산 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_NoncurrentAssets']) |
            df['account_id'].isin(['ifrs_NoncurrentAssets']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, "비유동부채")

    def getCurrLiability(self, df):
        """ 유동부채 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CurrentLiabilities']) |
            df['account_id'].isin(['ifrs_CurrentLiabilities']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, "유동부채")

    def getCashAssets(self, df):
        """ 현금성 자산 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CashAndCashEquivalents']) |
            df['account_id'].isin(['ifrs_CashAndCashEquivalents']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, "현금및현금성자산")

    def getTaxCost(self, df):
        """ 법인세비용차감전순이익 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_ProfitLossBeforeTax']) |
            df['account_id'].isin(['ifrs_ProfitLossBeforeTax']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 법인세비용차감전순이익 len: {len(data)}")
            print(f"[I] serching other op_cash_flow value step 1 ..")
            searchfor = ['(.)*법인세비용차감전순이익']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '법인세비용차감전순이익')

    def getFinIncome(self, df):
        """ 금융수익 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_FinanceIncome']) |
            df['account_id'].isin(['ifrs_FinanceIncome']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 금융수익 len: {len(data)}")
            print(f"[I] serching other capital value step 1 ..")
            searchfor = ['^([^가-힣]+)?금융수익$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '금융수익')

    def getFinCost(self, df):
        """ 금융비용 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_FinanceCosts']) |
            df['account_id'].isin(['ifrs_FinanceCosts']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 금융비용 len: {len(data)}")
            print(f"[I] serching other capital value step 1 ..")
            searchfor = ['^([^가-힣]+)?금융비용$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '금융비용')

    def getCap(self, df):
        """ 자본금 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_IssuedCapital']) |
            df['account_id'].isin(['ifrs_IssuedCapital']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 자본금 len: {len(data)}")
            print(f"[I] serching other capital value step 1 ..")
            searchfor = ['^([^가-힣]+)?자본금$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)) &
                df['sj_div'].isin(['BS']),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '자본금')

    def getOpCashFlow(self, df):
        """ 영업현금흐름 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CashFlowsFromUsedInOperatingActivities']) |
            df['account_id'].isin(
                ['ifrs_CashFlowsFromUsedInOperatingActivities']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 영업활동현금흐름 len: {len(data)}")
            print(f"[I] serching other op_cash_flow value step 1 ..")
            searchfor = ['(.)*영업활동(.)*현금흐름$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)) &
                df['sj_div'].isin(['CF']),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '영업활동현금흐름')

    def getInvestCashFlow(self, df):
        """ 투자활동 현금흐름 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CashFlowsFromUsedInInvestingActivities']) |
            df['account_id'].isin(
                ['ifrs_CashFlowsFromUsedInInvestingActivities']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 투자활동현금흐름 len: {len(data)}")
            print(f"[I] serching other capital value step 1 ..")
            searchfor = ['(.)*투자활동(.)*현금흐름$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)) &
                df['sj_div'].isin(['CF']),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '투자활동현금흐름')

    def getFinCashFlow(self, df):
        """ 재무활동 현금흐름 반환 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_CashFlowsFromUsedInFinancingActivities']) |
            df['account_id'].isin(
                ['ifrs_CashFlowsFromUsedInFinancingActivities']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 재무활동현금흐름 len: {len(data)}")
            print(f"[I] serching other capital value step 1 ..")
            searchfor = ['(.)*재무활동(.)*현금흐름$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)) &
                df['sj_div'].isin(['CF']),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '재무활동현금흐름')

    def getCAPEX(self, df):
        """ 유형자산의 취득 반환 함수 """

        data = df.loc[
            df['account_id'].isin(
                ['ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 유형자산의취득 len: {len(data)}")
            print(f"[I] serching other CAPEX step 1 ..")
            searchfor = ['유형자산(.)*취득']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)) &
                df['sj_div'].isin(['CF']),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '유형자산의취득')

    def getFCF(self, df):
        """ FCF 반환 함수 """

        data = df.loc[
            df['sj_div'].isin(['CF']) &
            df['account_id'].isin(
                ['ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities']),
            'thstrm_amount'
        ].to_numpy()

        return self.doCheck(data, 'FCF')

    def getCapSurpl(self, df):
        """ 자본잉여금 함수 """

        data = df.loc[
            df['account_id'].isin(['dart_CapitalSurplus']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 자본잉여금 len: {len(data)}")
            print(f"[I] serching other capital surplus value step 1 ..")
            searchfor = ['^([^가-힣]+)?자본잉여금$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '자본잉여금')

    def getIncomeSurpl(self, df):
        """ 이익잉여금 함수 """

        data = df.loc[
            df['account_id'].isin(['ifrs-full_RetainedEarnings']) |
            df['account_id'].isin(['ifrs_RetainedEarnings']),
            'thstrm_amount'
        ].to_numpy()

        # condition 1
        if not self.checkLen(data):
            print(f"[W] 이익잉여금 len: {len(data)}")
            print(f"[I] serching other income surplus value step 1 ..")
            searchfor = ['^([^가-힣]+)?이익잉여금$']

            data = df.loc[
                df['account_nm'].str.contains('|'.join(searchfor)),
                'thstrm_amount'
            ].to_numpy()

        return self.doCheck(data, '이익잉여금')

    def prepFinState(self, stock_code, year, report_code, fsdatadir="fsdata"):
        """  DART 홈페이지에서 재무재표를 받아와서 DB에 저장할 수 있는 포맷으로 만들어줌  """
        result = {}
        base_dir = os.path.join(fsdatadir, year)
        os.makedirs(f"{base_dir}", exist_ok=True)
        filename = os.path.join(base_dir, f"{stock_code}.csv")

        corpCode = self.stockCode2corpCode(stock_code)
        df_stock_num = self.getTotalStock(corpCode, year, report_code)
        df_fin_state = self.getFinStateAll(corpCode, year, report_code)

        if (df_fin_state is not None) & (df_stock_num is not None):

            df_fin_state.to_csv(filename, encoding='euc-kr')

            # preprocess
            df_fin_state.replace('', np.nan, inplace=True)
            df_fin_state.dropna(subset=['thstrm_amount'], inplace=True)
            df_fin_state = df_fin_state.reset_index(drop=True)
            # result = prepFinState(code, YEAR)

            # showFinState(result)

            # print("--------------------------")
            # if i%60 == 30:
            #     print(f"[I] sleep 10 sec ..")
            #     time.sleep(10)

            total_num, normal_num, prior_num = self.getStockNum(
                df_stock_num)  # 총 발행 주식 수
            equity = self.getEquity(df_fin_state)  # 자본
            liability = self.getLiability(df_fin_state)  # 부채
            assets = equity + liability  # 자산
            profit = self.getProfit(df_fin_state)  # 당기순이익
            revenue = self.getRevenue(df_fin_state)  # 매출액
            # revenue = getRevenue(data_fin_state) # 매출액
            gp = self.getGP(df_fin_state)  # 매출 총 이익
            op_income = self.getOpIncome(df_fin_state)  # 영업이익
            curr_assets = self.getCurrAssets(df_fin_state)  # 유동자산
            noncurr_assets = self.getNonCurrAssets(df_fin_state)  # 비유동자산
            curr_liability = self.getCurrLiability(df_fin_state)  # 유동부채
            cash_asset = self.getCashAssets(df_fin_state)  # 현금성 자산
            tax_cost = self.getTaxCost(df_fin_state)  # 법인세 비용
            fin_income = self.getFinIncome(df_fin_state)  # 금융수익
            fin_cost = self.getFinCost(df_fin_state)  # 금융비용
            capital = self.getCap(df_fin_state)  # 자본금
            op_cashflow = self.getOpCashFlow(df_fin_state)  # 영업활동현금흐름
            invest_cashflow = self.getInvestCashFlow(df_fin_state)  # 투자활동현금흐름
            fin_cashflow = self.getFinCashFlow(df_fin_state)  # 재무활동현금흐름
            capex = self.getCAPEX(df_fin_state)  # 유형자산의 취득
            cap_surpl = self.getCapSurpl(df_fin_state)  # 자본 잉여금
            income_surpl = self.getIncomeSurpl(df_fin_state)  # 이익 잉여금

            last_data = self.getDailyPrice(
                stock_code, start_date=f"{year}-12-20", end_date=f"{year}-12-31")

            if not last_data.empty:
                print(f"[D] last_data: {last_data}")

                last_stock_price = last_data.iloc[-1]['close']
                print(f"[D] last_stock_price: {last_stock_price}")
            else:
                print(f"[E] last_data is empty!")
                last_stock_price = None

            # EPS
            if self.checkIsNum(profit) & self.checkIsNum(total_num):
                EPS = profit / total_num
            else:
                print(f"[D] EPS --")
                print(f"profit: {self.checkIsNum(profit)}")
                print(f"total_stocks: {self.checkIsNum(total_num)}")
                EPS = None

            # PER
            if self.checkIsNum(last_stock_price) & self.checkIsNum(EPS):
                PER = last_stock_price / EPS    # 시가총액 / 당기순이익
            else:
                print(f"[D] PER --")
                print(f"last_stock_price: {self.checkIsNum(last_stock_price)}")
                print(f"EPS: {self.checkIsNum(EPS)}")
                PER = None

            # BPS
            if self.checkIsNum(equity) & self.checkIsNum(total_num):
                BPS = equity / total_num     # 자본총계 / 주식수
            else:
                print(f"[D] BPS --")
                print(f"equity: {self.checkIsNum(equity)}")
                print(f"total_stocks: {self.checkIsNum(total_num)}")
                BPS = None

            # PBR
            if self.checkIsNum(last_stock_price) & self.checkIsNum(BPS):
                PBR = last_stock_price / BPS    # 시가총액 / 자본
            else:
                print(f"[D] PBR --")
                print(f"last_stock_price: {self.checkIsNum(last_stock_price)}")
                print(f"BPS: {self.checkIsNum(BPS)}")
                PBR = None

            # ROE
            if self.checkIsNum(PBR) & self.checkIsNum(PER):
                ROE = PBR / PER * 100           # 당기순이익 / 자본
            else:
                print(f"[D] ROE --")
                print(f"PBR: {self.checkIsNum(PBR)}")
                print(f"PER: {self.checkIsNum(PER)}")
                ROE = None

            # ROA
            if self.checkIsNum(profit) & self.checkIsNum(assets):
                ROA = profit / assets * 100     # 당기순이익 / 자산
            else:
                print(f"[D] ROA --")
                print(f"profit: {self.checkIsNum(profit)}")
                print(f"assets: {self.checkIsNum(assets)}")
                ROA = None

            # PSR
            if self.checkIsNum(last_stock_price) & self.checkIsNum(revenue) & self.checkIsNum(total_num):
                PSR = last_stock_price / (revenue / total_num)  # 시가총액 /매출
            else:
                print(f"[D] PSR --")
                print(f"last_stock_price: {self.checkIsNum(last_stock_price)}")
                print(f"revenue: {self.checkIsNum(revenue)}")
                print(f"total_stocks: {self.checkIsNum(total_num)}")
                PSR = None

            # ROC
            if self.checkIsNum(op_income) & self.checkIsNum(assets) & self.checkIsNum(curr_liability):
                ROC = op_income / (assets-curr_liability) * 100
            else:
                print(f"[D] ROC --")
                print(f"op_income: {self.checkIsNum(op_income)}")
                print(f"assets: {self.checkIsNum(assets)}")
                print(f"curr_liability: {self.checkIsNum(curr_liability)}")
                ROC = None

            # FCF
            if self.checkIsNum(op_cashflow) & self.checkIsNum(capex):
                FCF = op_cashflow - capex
            else:
                print(f"[D] FCF --")
                print(f"opcash_flow: {self.checkIsNum(op_cashflow)}")
                print(f"capex: {self.checkIsNum(capex)}")
                FCF = None

            # EV_EBIT
            if self.checkIsNum(last_stock_price) & self.checkIsNum(total_num) & self.checkIsNum(liability) \
                & self.checkIsNum(cash_asset) & self.checkIsNum(fin_cost) & self.checkIsNum(tax_cost) & self.checkIsNum(fin_income) \
                    & self.checkIsNum(profit):
                EBIT = profit + tax_cost - fin_income + fin_cost
                EV = last_stock_price * total_num + liability - \
                    cash_asset  # 시가총액 + 부채 - (현금 + 비영업자산)
                EV_EBIT = EV / EBIT
            else:
                print(f"[D] EV_EBIT --")
                print(f"cash_asset: {self.checkIsNum(cash_asset)}")
                print(f"fin_cost: {self.checkIsNum(fin_cost)}")
                print(f"tax_cost: {self.checkIsNum(tax_cost)}")
                print(f"fin_income: {self.checkIsNum(fin_income)}")
                EV_EBIT = None

            # GP/A
            if self.checkIsNum(gp) & self.checkIsNum(assets):
                GP_A = gp / assets * 100
            else:
                print(f"[D] GP_A --")
                print(f"gp: {self.checkIsNum(gp)}")
                print(f"assets: {self.checkIsNum(assets)}")
                GP_A = None

            # 유보율
            if self.checkIsNum(cap_surpl) & self.checkIsNum(income_surpl) & self.checkIsNum(capital):
                reserve_ratio = (cap_surpl+income_surpl)/capital * 100
            else:
                print(f"[D] reserve_ratio --")
                print(f"cap_surpl: {self.checkIsNum(cap_surpl)}")
                print(f"income_surpl: {self.checkIsNum(income_surpl)}")
                print(f"cap: {self.checkIsNum(capital)}")
                reserve_ratio = None

            # 부채율
            if self.checkIsNum(liability) & self.checkIsNum(equity):
                liability_ratio = liability / equity * 100
            else:
                print(f"[D] liability_ratio --")
                print(f"cap_surpl: {self.checkIsNum(cap_surpl)}")
                print(f"income_surpl: {self.checkIsNum(income_surpl)}")
                print(f"cap: {self.checkIsNum(capital)}")
                liability_ratio = None

            # 영업이익률
            if self.checkIsNum(op_income) & self.checkIsNum(revenue):
                op_income_ratio = op_income / revenue * 100
            else:
                print(f"[D] op_income_ratio --")
                print(f"op_income: {self.checkIsNum(op_income)}")
                print(f"revenue: {self.checkIsNum(revenue)}")
                op_income_ratio = None

            # 순이익률
            if self.checkIsNum(profit) & self.checkIsNum(revenue):
                total_income_ratio = profit / revenue * 100
            else:
                print(f"[D] profit ratio --")
                print(f"op_income: {self.checkIsNum(op_income)}")
                print(f"revenue: {self.checkIsNum(revenue)}")
                total_income_ratio = None

            if report_code == "11013":
                quarter = "Q1"  # 1분기 보고서
            elif report_code == "11012":
                quarter = "Q2"  # 반기 보고서
            elif report_code == "11014":
                quarter = "Q3"  # 3분기 보고서
            elif report_code == "11011":
                quarter = "annual"  # 사업보고서 (1년 단위)

            result['year'] = year
            result['stock_code'] = stock_code
            result['name'] = self.code_dict[stock_code]
            result['report_code'] = report_code
            result['quarter'] = quarter
            result['revenue'] = revenue
            result['price'] = last_stock_price
            result['gp'] = gp
            result['op_income'] = op_income
            result['profit'] = profit
            result['assets'] = assets
            result['liability'] = liability
            result['equity'] = equity
            result['curr_assets'] = curr_assets
            result['noncurr_assets'] = noncurr_assets
            result['curr_liability'] = curr_liability
            result['capital'] = capital
            result['op_cashflow'] = op_cashflow
            result['invest_cashflow'] = invest_cashflow
            result['fin_cashflow'] = fin_cashflow
            result['capex'] = capex
            result['FCF'] = FCF
            result['op_income_ratio'] = f"{op_income_ratio:.8f}" if op_income_ratio is not None else None
            result['total_income_ratio'] = f"{total_income_ratio:.8f}" if total_income_ratio is not None else None
            result['EV_EBIT'] = f"{EV_EBIT:.8f}" if EV_EBIT is not None else None
            result['ROE'] = f"{ROE:.8f}" if ROE is not None else None
            result['ROA'] = f"{ROA:.8f}" if ROA is not None else None
            result['ROC'] = f"{ROC:.8f}" if ROC is not None else None
            result['liability_ratio'] = f"{liability_ratio:.8f}" if liability_ratio is not None else None
            result['reserve_ratio'] = f"{reserve_ratio:.8f}" if reserve_ratio is not None else None
            result['EPS'] = f"{EPS:.8f}" if EPS is not None else None
            result['PER'] = f"{PER:.8f}" if PER is not None else None
            result['BPS'] = f"{BPS:.8f}" if BPS is not None else None
            result['PSR'] = f"{PSR:.8f}" if PSR is not None else None
            result['PBR'] = f"{PBR:.8f}" if PBR is not None else None
            result['GP_A'] = f"{GP_A:.8f}" if GP_A is not None else None
            result['total_num'] = total_num
            result['normal_num'] = normal_num
            result['prior_num'] = prior_num
            result['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return result

        else:
            print(f"[E] there is no date [code]:{stock_code}")
            return None

    def replaceIntoDB(self, data):
        """ 데이터를 DB에 저장하는 함수  """
        with self.connection.cursor() as curs:
            sql = f"""
                REPLACE INTO finance_state (
                    stock_code, 
                    name,
                    report_code,
                    year,
                    quarter,
                    total_num,
                    normal_num,
                    prior_num,
                    price,
                    revenue,
                    gp,
                    op_income,
                    profit,
                    assets,
                    liability,
                    equity,
                    curr_assets,
                    noncurr_assets,
                    curr_liability,
                    capital,
                    op_cashflow,
                    invest_cashflow,
                    fin_cashflow,
                    capex,
                    FCF,
                    op_income_ratio,
                    total_income_ratio,
                    EV_EBIT,
                    ROE,
                    ROA,
                    ROC,
                    liability_ratio,
                    reserve_ratio,
                    EPS,
                    PER,
                    BPS,
                    PSR,
                    PBR,
                    GP_A,
                    last_update
                ) values (
                    '{data["stock_code"]}',
                    '{data["name"]}',
                    '{data["report_code"]}',
                    '{data["year"]}',
                    '{data["quarter"]}',
                    '{data["total_num"]}',
                    '{data["normal_num"]}',
                    '{data["prior_num"]}',
                    '{data["price"]}',
                    '{data["revenue"]}',
                    '{data["gp"]}',
                    '{data["op_income"]}',
                    '{data["profit"]}',
                    '{data["assets"]}',
                    '{data["liability"]}',
                    '{data["equity"]}',
                    '{data["curr_assets"]}',
                    '{data["noncurr_assets"]}',
                    '{data["curr_liability"]}',
                    '{data["capital"]}',
                    '{data["op_cashflow"]}',
                    '{data["invest_cashflow"]}',
                    '{data["fin_cashflow"]}',
                    '{data["capex"]}',
                    '{data["FCF"]}',
                    '{data["op_income_ratio"]}',
                    '{data["total_income_ratio"]}',
                    '{data["EV_EBIT"]}',
                    '{data["ROE"]}',
                    '{data["ROA"]}',
                    '{data["ROC"]}',
                    '{data["liability_ratio"]}',
                    '{data["reserve_ratio"]}',
                    '{data["EPS"]}',
                    '{data["PER"]}',
                    '{data["BPS"]}',
                    '{data["PSR"]}',
                    '{data["PBR"]}',
                    '{data["GP_A"]}',
                    '{data["last_update"]}'
                ) 
            """
            curs.execute(sql)
            self.connection.commit()
            print(
                f"[I] [code: {data['stock_code']} | year:{data['year']} | report_code: {data['report_code']}] -> success to push data into DB")

    def getFinStateFromDB(self, stock_code, year, report_code):
        """ DB로 부터 재무제표 불러오는 함수 """
        if stock_code not in self.code_dict:
            print(f"[E] Invalid code: {stock_code}")
            return None
        else:
            sql = f"""
                SELECT * FROM finance_state WHERE stock_code = '{stock_code}'
                and year = '{year}' and report_code = '{report_code}'
            """
            df = pd.read_sql(sql, self.connection)
            return df

    def getFinStateFromDB_all(self, year, report_code):
        """ DB로 부터 연도 및 보고서 코드를 기준으로 재무제표 불러오는 함수 """

        sql = f"""
            SELECT * FROM finance_state WHERE year = '{year}' and report_code = '{report_code}'
        """
        df = pd.read_sql(sql, self.connection)
        return df

    def updateFinStateToDB(self, year, report_code):
        """ DART --> DB에 저장하는 코드
            * 1분당 maximum request 60으로 제한 
            * 어길 시 24시간동안 해당 IP차단
            TODO:
            - DART -> CSV -> DB 순서로 저장해서 최대한 API에 의존성 없애기
        """

        code_list = list(self.code_dict.keys())
        for i, code in enumerate(code_list):
            result = self.prepFinState(code, year, report_code)
            if result is not None:
                self.replaceIntoDB(result)
            else:
                print(f"[E] Invalid code: {code}")
            if i % 60 == 0:
                print(f"[I] sleep {SLEEP_TIME} sec ..")
                time.sleep(SLEEP_TIME)


if __name__ == '__main__':

    host = os.environ.get('MYSQL_HOST')
    user = os.environ.get('MYSQL_USER')
    pwd = os.environ.get('MYSQL_ROOT_PASSWORD')
    dart_key = os.environ.get('DART_KEY')
    port = os.environ.get('MYSQL_PORT')

    print(f"[D] host: {host}")
    print(f"[D] user: {user}")
    print(f"[D] pwd: {pwd}")
    print(f"[D] dart_key: {dart_key}")

    kor_model = KorFinStateModel(
        host=host,
        port=int(port),
        db="KOR_DB",
        user=user,
        pwd=pwd,
        dart_key=dart_key
    )
    # test = kor_model.getFinStateFromDB_all("2019", "11011")
    # test.to_csv("2019_11011_all.csv", encoding="euc-kr")
    # print(test)
    # kor_model.updateFinStateToDB("2019", "11011")
    result = kor_model.prepFinState("005380", "2019", "11011")
    print(result)
    kor_model.replaceIntoDB(result)
    # test = kor_model.getFinStateFromDB("005380", "2019", "11011")
    # print(test)
    # test = os.environ.get('MYSQL_ROOT_PASSWORD')
