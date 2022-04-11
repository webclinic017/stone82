import time
from urllib.request import Request, urlopen
import asyncio
import aiohttp
from aiohttp import request
from io import BytesIO
import pandas as pd
from datetime import datetime, timedelta
import aiomysql
import os

SLEEP_TIME = 0.1

async def fetch(date):

    date = date.replace('-','')

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
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}

    async with aiohttp.ClientSession() as session:
        async with session.get(gen_otp_url, headers=headers,params=gen_otp_data) as res_otp:
            code = await res_otp.text()

        async with session.post(down_url, data={'code':code}, headers=headers) as res_down:
            content = await res_down.content.read()

        df = pd.read_csv(BytesIO(content), encoding='EUC-KR')
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

        df['date'] = datetime.strptime(date,'%Y%m%d').date()
        df = df[['code','date', 'name', 'market', 'close', 'diff', 'open', 'high', 'low', 'volume', 'amount', 'stock_num', 'cap']]
    
        df = df.dropna()
        return df

  


        # try:
            
        #     if df.shape[0] != 0:
        #         df = df[['code','date', 'name', 'market', 'close', 'diff', 'open', 'high', 'low', 'volume', 'amount', 'stock_num', 'cap']]
        
        #         df = df.dropna()
        #         return df
        #     else:
        #         print(f"[{date}]: skipped!")
        # except :
        #     raise ValueError(f'[{date}] wrong dataframe: {df}')

     
async def main(TABLE='daily_price'):

    start_year='19950502'
    START = datetime.strptime(start_year,'%Y%m%d') # 1
    TODAY = datetime.today()
    DAYS = (TODAY - START).days 
    # DAYS = 30

    df_list = []
    for day in range(DAYS):
        date = (START + timedelta(days=day)).strftime('%Y-%m-%d')
        future = asyncio.ensure_future(fetch(date))
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
 

    for i, df in enumerate(df_list) :
        for r in df.itertuples():
            sql = f"""
                REPLACE INTO {TABLE} (
                    code, date, name, open, high, low, close, diff, volume, market, amount, stock_num, cap
                ) VALUES (
                    '{str(r.code).zfill(6)}', '{r.date}', '{r.name}', '{r.open}', '{r.high}', '{r.low}', '{r.close}', '{r.diff}', '{r.volume}', '{r.market}', '{r.amount}', '{r.stock_num}', '{r.cap}'
                )
            """
            await cur.execute(sql)
        if i % 100 == 0:
            print(f'progress is [{i}/{len(df_list)}]')

    await connect.commit()
    await cur.close()
    connect.close()
    



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
# asyncio.run(main())


    # loop = asyncio.get_event_loop()
    # feature = loop.run_in_executor(None,requests.get, gen_otp_url, headers, gen_otp_data)
    # response = await feature

    # r = requests.get(gen_otp_url, headers=headers, params=gen_otp_data)
    # code = r.text

    # down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    # # requests Module의 post함수를 이용하여 해당 url에 접속하여 otp코드를 제출함
    # down_sector_KS  = requests.post(down_url, {'code':code}, headers=headers)
    # # 다운 받은 csv파일을 pandas의 read_csv 함수를 이용하여 읽어 들임. 
    # # read_csv 함수의 argument에 적합할 수 있도록 BytesIO함수를 이용하여 바이너 스트림 형태로 만든다.
    # df =  pd.read_csv(BytesIO(down_sector_KS.content), encoding='EUC-KR')    
    # df = df.rename(columns={
    #             '종목코드': 'code',
    #             '종목명': 'name',
    #             '시장구분': 'market',
    #             '날짜': 'date',
    #             '종가': 'close',
    #             '대비': 'diff',
    #             '시가': 'open',
    #             '고가': 'high',
    #             '저가': 'low',
    #             '거래량': 'volume',
    #             '거래대금': 'amount',
    #             '상장주식수': 'stock_num',
    #             '시가총액': 'cap'})
    # df = df[['code', 'name', 'market', 'close', 'diff', 'open', 'high', 'low', 'volume', 'amount', 'stock_num', 'cap']]
    # df = df.dropna()
    
    # return df

# begin = time()
# loop = asyncio.get_event_loop()          # 이벤트 루프를 얻음
# a = loop.run_until_complete(crawlDataFromKRX('20000105'))          # main이 끝날 때까지 기다림
# loop.close()                             # 이벤트 루프를 닫음
# end = time()
# print('실행 시간: {0:.3f}초'.format(end - begin))



# data =  crawlDataFromKRX('20000105')
# print(data)
# urls = ['https://www.google.co.kr/search?q=' + i
#         for i in ['apple', 'pear', 'grape', 'pineapple', 'orange', 'strawberry']]
 




# async def fetch(url):
#     request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})    # UA가 없으면 403 에러 발생
#     response = await loop.run_in_executor(None, urlopen, request)    # run_in_executor 사용
#     page = await loop.run_in_executor(None, response.read)           # run in executor 사용
#     return len(page)
 
# async def main():
#     futures = [asyncio.ensure_future(fetch(url)) for url in urls]
#                                                            # 태스크(퓨처) 객체를 리스트로 만듦
#     result = await asyncio.gather(*futures)                # 결과를 한꺼번에 가져옴
#     print(result)
 




