from tokenize import String
from tracemalloc import start
from unicodedata import category
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import logging
import aiohttp
import asyncio
from io import BytesIO
from tqdm import tqdm
import zarr
import os
import re
SLEEP_TIME = 0.1


class DataManager():

    def __init__(self):
        """
        filesystem based data manager

        """
        # self.zarr_path = zarr_path
        # self.async_loop = asyncio.get_event_loop()

    def getTodayDate(self) -> String:
        return str(datetime.today().date().strftime('%Y%m%d'))

    def getValidDate(self, date: str):

        if re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            return date
        elif re.match(r"^[0-9]{4}[0-9]{2}[0-9]{2}$", date):
            return f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        else:
            raise ValueError(f"Invalid date format: {date}")


class KorDataManager(DataManager):
    """
    filesystem based korean data manager
    """

    def __init__(self):

        super().__init__()
        self.start_date = '1995-05-02'

    def getDailyPriceFromZarr(self, zarr_path, **kwargs):

        start_date = self.getValidDate(
            kwargs.get('start_date', self.start_date))
        end_date = self.getValidDate(
            kwargs.get('end_date', self.getTodayDate()))

        with zarr.open(zarr_path, 'r') as zr:
            date_arr = zr['date'][:]

        start_date = max(date_arr[0], np.datetime64(start_date))
        end_date = min(date_arr[-1], np.datetime64(end_date))

        start_idx = date_arr.searchsorted(start_date)
        end_idx = date_arr.searchsorted(end_date)

        with zarr.open(zarr_path, 'r') as zr:
            date_arr = zr['date'][start_idx:end_idx+1]
            value = zr['value'][start_idx:end_idx+1, :, :]
            code_arr = zr['code'][:].astype(str)
            column_arr = zr['column'][:].astype(str)

        return self.checkSanity(value, date_arr, code_arr, column_arr)

    def checkSanity(self, value, date_arr, code_arr, column_arr):
        date_len = min(value.shape[0], date_arr.shape[0])
        code_len = min(value.shape[1], code_arr.shape[0])
        column_len = min(value.shape[2], column_arr.shape[0])

        date_arr = date_arr[:date_len]
        code_arr = code_arr[:code_len]
        column_arr = column_arr[:column_len]
        value = value[:date_len, :code_len, :column_len]

        data = pd.DataFrame()
        for i, date in enumerate(date_arr[:]):

            df = pd.DataFrame(value[i], code_arr, column_arr)
            df['date'] = date
            data = pd.concat([data, df])
        data['code'] = data.index
        return data.reset_index(drop=True)

    async def getDayPriceFromKRX(self, date: str) -> pd.DataFrame:
        """
        date: format: '%Y%m%d' or '%Y-%m-%d' ex) 19950101, 1995-01-01

        """

        date = date.replace('-', '')

        otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
        down_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"

        otp_base_key = {
            'locale': 'ko_KR',
            'mktId': 'ALL',
            'trdDd': date,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false',
            'name': 'fileDown',
            'url': 'dbms/MDC/STAT/standard/MDCSTAT01501'
        }

        otp_ref_key = {
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

        async with aiohttp.ClientSession() as sess:
            async with sess.get(otp_url, headers=headers, params=otp_base_key) as res_otp_base, sess.get(otp_url, headers=headers, params=otp_ref_key) as res_otp_ref:

                base_code = await res_otp_base.text()
                ref_code = await res_otp_ref.text()

            async with sess.post(down_url, data={'code': base_code}, headers=headers) as res_down_base, sess.post(down_url, data={'code': ref_code}, headers=headers) as res_down_ref:
                base_content = await res_down_base.content.read()
                ref_content = await res_down_ref.content.read()

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
            df['code'] = df['code'].astype(str).apply(lambda x: x.zfill(6))

            df = df[['code', 'date', 'name', 'market', 'close', 'diff', 'open', 'high',
                     'low', 'volume', 'amount', 'stock_num', 'cap', 'ref_open', 'ref_close']]
            df = df.dropna(subset=['code', 'date', 'name', 'market', 'close', 'diff',
                                   'open', 'high', 'low', 'volume', 'amount', 'stock_num', 'cap'])

            df = df.fillna(np.nan)

            return df

    async def _getDailyPriceFromKRX(self, **kwargs):
        """
        Parameters
        --------------
        - start_date : String
        - end_date : String
        """
        start_date = self.getValidDate(
            kwargs.get('start_date', self.start_date))
        end_date = self.getValidDate(
            kwargs.get('end_date', self.getTodayDate()))
        START = datetime.strptime(start_date, '%Y-%m-%d')
        END = datetime.strptime(end_date, '%Y-%m-%d')
        DAYS = (END - START).days
        SLEEP_TIME = kwargs.get('SLEEP', 0.1)

        logging.debug(f"START: {START}")
        logging.debug(f"END: {END}")
        logging.debug(f"SLEEP_TIME: {SLEEP_TIME}")

        df = pd.DataFrame()

        for day in tqdm(range(DAYS)):
            date = (START + timedelta(days=day)).strftime('%Y-%m-%d')
            future = asyncio.ensure_future(self.getDayPriceFromKRX(date))
            result = await asyncio.gather(future)
            await asyncio.sleep(SLEEP_TIME)

            if result[0].shape[0] != 0:
                df = pd.concat([df, result[0]])

        return df

    def getDailyPriceFromKRX(self, **kwargs) -> list:

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._getDailyPriceFromKRX(**kwargs))

    def saveDataframeToZarr(self, df: pd.DataFrame, zarr_path, chunks=(720, 360, 10), **kwargs):
        result = []
        if kwargs['category'] == 'daily_price':
            column_list = [
                'open', 'close', 'high', 'low', 'ref_open', 'ref_close', 'volume', 'amount', 'stock_num', 'cap'
            ]

            date_arr = df['date'].unique().astype(np.datetime64)
            column_arr = np.array(column_list).astype(str)
            code_arr = df['code'].unique().astype(str)
            value = self.extractDailyPriceValue(
                df, date_arr, code_arr, column_arr)

            with zarr.open(zarr_path, 'w') as zr:
                zr.create_dataset('date', data=date_arr, shape=(
                    None, ), chunks=(chunks[0], ), dtype='M8[D]')
                zr.create_dataset('code', data=code_arr, shape=(
                    None, ), chunks=(chunks[1], ), dtype='|S12')
                zr.create_dataset('column', data=column_arr, shape=(
                    None, ), chunks=(chunks[2], ), dtype='|S20')
                zr.create_dataset('value', data=value, shape=(
                    None, None, None), chunks=chunks, dtype=float, fillvalue=np.nan)
                logging.info(f"updated value shape: {value.shape}")

    def extractDailyPriceValue(self, df: pd.DataFrame, date_arr, code_arr, column_arr):
        result = []
        for date in date_arr:
            sub_df = df.loc[df['date'] == date]
            sub_df = sub_df.set_index(sub_df['code'])
            value = sub_df.reindex(code_arr, axis=0)[
                column_arr].fillna(np.nan).values.astype('<U20')
            result.append(value)

        return np.stack(result, axis=0)

    def saveDailyPriceToZarr(self, df: pd.DataFrame, zarr_path, chunks=(720, 360, 10), **kwargs):

        if df.shape[0] == 0:
            return False

        # initial data save
        if not os.path.exists(zarr_path):
            logging.info(f"data not exist on: '{zarr_path}' -> save new data")
            self.saveDataframeToZarr(df, zarr_path, chunks=(
                720, 360, 10), category='daily_price')
            return True

        date_arr = df['date'].unique().astype(np.datetime64)
        code_arr = df['code'].unique().astype(str)

        with zarr.open(zarr_path, 'r') as zr:
            old_date_arr = zr['date'][:]
            old_code_arr = zr['code'][:].astype(str)
            old_value_arr = zr['value'][:]
            column_arr = zr['column'][:].astype(str)

        # check update data
        last_date = old_date_arr[-1]
        new_date_arr = date_arr[date_arr > last_date]
        new_code_list = list(set(code_arr) - set(old_code_arr))
        new_date_len = new_date_arr.shape[0]
        new_code_len = len(new_code_list)
        column_len = column_arr.shape[0]
        logging.debug(f"last update: {last_date}")

        # update date & code & value
        if new_date_len > 0 and new_code_len > 0:
            logging.debug(f"update date: {new_date_arr[-1]}")
            logging.debug(
                f"update new code & new date -> # of code: {new_code_len} | # of date: {new_date_len}")
            with zarr.open(zarr_path, 'a') as zr:
                full_date_len = zr['date'].shape[0] + new_date_len
                full_code_len = old_code_arr.shape[0] + new_code_len
                full_code_list = list(old_code_arr) + new_code_list
                logging.debug(
                    f"full_date_len: {full_date_len} / full_code_len: {full_code_len} ")

                zr['date'].resize((full_date_len,))
                zr['date'][-new_date_len:] = new_date_arr
                zr['code'].resize((full_code_len, ))
                zr['code'][-new_code_len:] = new_code_list
                zr['value'].resize(
                    (full_date_len, full_code_len, column_len))
                new_value = self.extractDailyPriceValue(
                    df, new_date_arr, full_code_list, column_arr)
                zr['value'][-new_date_len:] = new_value

        # update date value
        elif new_date_len > 0:
            logging.debug(f"update date: {new_date_arr[-1]}")
            logging.debug(f"update new date -> # of date: {new_date_len}")
            with zarr.open(zarr_path, 'a') as zr:
                full_date_len = zr['date'].shape[0] + new_date_len
                logging.debug(f"full_date_len: {full_date_len}")

                zr['date'].resize((full_date_len,))
                zr['date'][-new_date_len:] = new_date_arr
                zr['value'].resize(
                    (full_date_len, old_code_arr.shape[0], column_len))
                new_value = self.extractDailyPriceValue(
                    df, new_date_arr, old_code_arr, column_arr)
                zr['value'][-new_date_len:] = new_value

        elif new_code_len > 0:
            raise ValueError(f"Datetime not updated!")
        else:
            logging.info(
                f"Nothing to update! last date (new): {date_arr[-1]} / last update: {last_date}")

            return False

        logging.debug(f"old value shape: {old_value_arr.shape}")
        logging.debug(f"new value shape: {new_value.shape}")
        logging.debug(f"updated value shape: {zr['value'].shape}")

        return True
