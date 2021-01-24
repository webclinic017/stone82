import pandas as pd
from pandas_datareader import data



class KoreaDataLoader:

    def __init__(self, vnet=False):

        self.title = ''  # 그림 제목
        self.stock_type = {
            'kospi': 'stockMkt',
            'kosdaq': 'kosdaqMkt'
            } 
        self.kospi_codes=None
        self.kosdaq_codes=None

    def data_from_yahoo(self, code, start, end):

        return data.get_data_yahoo(code, start, end)


    def get_code(self, df, name):
        code = df.query("name=='{}'".format(name))['code'].to_string(index=False)
        code = code.strip()
        
        return code

    def download_stock_codes(self, market):
        
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

