from tracemalloc import start
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import re


class DataBase:

    def __init__(
        self,
        host,
        db_name,
        pwd,
        user='root',
        port=3306,
        autocommit=True
    ):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""

        self.connection = pymysql.connect(
            host=host,
            port=port,
            db=db_name,
            user=user,
            passwd=pwd,
            autocommit=autocommit
        )
        self.code_dict = dict()
        self.getCompanyInfo()

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.connection.close()

    def checkDateFormat(self, date):
        date_lst = re.split('\D+', date)

        if date_lst[0] == '':
            date_lst = date_lst[1:]
        year = int(date_lst[0])
        month = int(date_lst[1])
        day = int(date_lst[2])

        if year < 1900 or year > 2200:
            raise ValueError(f"year: {year:d} is wrong.")

        if month < 1 or month > 12:
            raise ValueError(f"month: {month:d} is wrong.")

        if day < 1 or day > 31:
            raise ValueError(f"day: {day:d} is wrong.")
        

    def getCode(self, target_name):
        for code, name in self.code_dict.items():
            if name == target_name:
                return code
            else:
                "Can't find code! please check company name again"

    def getName(self, code):
        return self.code_dict[code]

    def getCompanyInfo(self):
        """ company_info 테이블에서 읽어와서 companyData와 codes에 저장 """
        sql = "SELECT * FROM company_info"
        companyInfo = pd.read_sql(sql, self.connection)
        for idx in range(len(companyInfo)):
            self.code_dict[companyInfo['code'].values[idx]
                           ] = companyInfo['company'].values[idx]

    def getDailyPrice(self, target, start_date=None, end_date=None):
        """ KRX 종목의 일별 시세를 데이터프레임 형태로 반환
            - code       : KRX 종목코드('005930') 또는 상장기업명('삼성전자')
            - start_date : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
            - end_date   : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """

        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d')
            print(f"[I] start_date is initialized to '{start_date}'")
        
        self.checkDateFormat(start_date)              

        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
            print(f"[I] end_date is initialized to '{end_date}'")

        self.checkDateFormat(end_date)

        if target == '*':
            sql = f"SELECT * FROM daily_price WHERE date >= '{start_date}' and date <= '{end_date}'"
            df = pd.read_sql(sql, self.connection)
            df.index = df['date']
            df = df.drop(['date'], axis=1)
            return df
        
        elif isinstance(target,list):
            result = {}
            for code in target:
                sql = f"SELECT * FROM daily_price WHERE code = '{code}' and date >= '{start_date}' and date <= '{end_date}'"
                df = pd.read_sql(sql, self.connection)
                df.index = df['date']
                df = df.drop(['code', 'date'], axis=1)
                result[code] = df
            
            return result

        else:
            sql = f"SELECT * FROM daily_price WHERE code = '{target}' and date >= '{start_date}' and date <= '{end_date}'"
            # sql = f"SELECT * FROM daily_price WHERE date >= '{start_date}' and date <= '{end_date}'"

            df = pd.read_sql(sql, self.connection)
            df.index = df['date']
            df = df.drop(['code', 'date'], axis=1)
            return df

            # code_list = list(self.code_dict.keys())
        # name_list = list(self.code_dict.values())

        # if code in code_list:
        #     pass
        # elif code in name_list:
        #     idx = name_list.index(code)
        #     code = code_list[idx]
        # else:
        #     print(f"ValueError: Code({code}) doesn't exist.")
        # sql = f"SELECT * FROM daily_price WHERE code = '{code}'"\
        #     f" and date >= '{start_date}' and date <= '{end_date}'"
        # df = pd.read_sql(sql, self.connection)
        # df.index = df['date']
        # df = df.drop(['code', 'date'], axis=1)
        # return df

    def getRltvMomntm(self, stock_count, start_date, end_date):
        """특정 기간 동안 수익률이 제일 높았던 stock_count 개의 종목들 (상대 모멘텀)
            - start_date  : 상대 모멘텀을 구할 시작일자 ('2020-01-01')   
            - end_date    : 상대 모멘텀을 구할 종료일자 ('2020-12-31')
            - stock_count : 상대 모멘텀을 구할 종목수
        """

        # 사용자가 입력한 시작일자를 DB에서 조회되는 일자로 보정
        cursor = self.connection.cursor()
        sql = f"SELECT max(date) FROM daily_price WHERE date <= '{start_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print("start_date : {} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')

        # 사용자가 입력한 종료일자를 DB에서 조회되는 일자로 보정
        sql = f"SELECT max(date) FROM daily_price WHERE date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print("end_date : {} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')

        print(start_date, end_date)
        # KRX 종목별 수익률을 구해서 2차원 리스트 형태로 추가
        rows = []
        columns = ['code', 'company', 'old_price', 'new_price', 'returns']

        for code, company in self.code_dict.items():
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([code, company, old_price, new_price,
                         returns])

        # 상대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'company', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        df = df.head(stock_count)
        df.index = pd.Index(range(stock_count))
        print(df)
        print(f"\nRelative momentum ({start_date} ~ {end_date}) : "
              f"{df['returns'].mean():.2f}% \n")
        return df

    def getAbsMomntm(self, rltv_momentum, start_date, end_date):
        """특정 기간 동안 상대 모멘텀에 투자했을 때의 평균 수익률 (절대 모멘텀)
            - rltv_momentum : get_rltv_momentum() 함수의 리턴값 (상대 모멘텀)
            - start_date    : 절대 모멘텀을 구할 매수일 ('2020-01-01')   
            - end_date      : 절대 모멘텀을 구할 매도일 ('2020-12-31')
        """
        stockList = list(rltv_momentum['code'])

        # 사용자가 입력한 매수일을 DB에서 조회되는 일자로 변경
        sql = f"select max(date) from daily_price "\
            f"where date <= '{start_date}'"
        cursor = self.connection.cursor()
        cursor.execute(sql)

        result = cursor.fetchone()
        if (result[0] is None):
            print("{} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')

        # 사용자가 입력한 매도일을 DB에서 조회되는 일자로 변경
        sql = f"select max(date) from daily_price "\
            f"where date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print("{} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')

        # 상대 모멘텀의 종목별 수익률을 구해서 2차원 리스트 형태로 추가
        rows = []
        columns = ['code', 'company', 'old_price', 'new_price', 'returns']

        for code, company in self.code_dict.items():
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price "\
                f"where code='{code}' and date='{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([code, company, old_price, new_price,
                         returns])

        # 절대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['code', 'company', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by='returns', ascending=False)
        print(df)
        print(f"\nAbasolute momentum ({start_date} ~ {end_date}) : "
              f"{df['returns'].mean():.2f}%")
        return df
