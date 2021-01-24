

import argparse, glob
import os
import pandas as pd
from pandas_datareader import data, wb
from utils.visualizer import Visualizer
from datetime import datetime
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick2_ohlc

import matplotlib.pyplot as plt



def getArgs():
    
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="CSJ Dataset creation.")
    parser.add_argument('--ver', choices=['v1', 'v2'], default='v2')
    args = parser.parse_args()
    return args 


def get_code(df, name):
    code = df.query("name=='{}'".format(name))['code'].to_string(index=False)
    code = code.strip()
    
    return code

def get_download_stock(market_type=None):
    market_type = stock_type[market_type]
    download_link = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
    download_link = download_link + '?method=download'
    download_link = download_link + '&marketType=' + market_type
    df = pd.read_html(download_link, header=0)[0]
    return df


def get_download_kospi():
    df = get_download_stock('kospi')
    df.종목코드 = df.종목코드.map('{:06d}.KS'.format)
    return df

def get_download_kosdaq():
    df = get_download_stock('kosdaq')
    df.종목코드 = df.종목코드.map('{:06d}.KQ'.format)
    return df

def get_group_charts(df, start, end, MA_list, img_dir):

    visualizer = Visualizer()

    for i in range(len(df))[50:]:
        name = df['name'][i].replace(' ','_')
        code = df['code'][i]
        try:
            target_data = data.get_data_yahoo(code, start, end)
            visualizer.plot_basic(target_data, code)
            for ma in MA_list:
                visualizer.add_moving_avg(ma)
            save_path = os.path.join(img_dir, name)
            visualizer.save(save_path+'.png')

            print(f"[SUCCESS!] to store {name}:{code} data .. path: {save_path+'.png'} ")
        except:
            print(f"[FAILED!] to get {name}:{code} data from yahoo finence ")
            continue



        


if __name__ == "__main__":


    FLAGS = getArgs()

    start = datetime(2019,1,1)
    end = datetime(2020,12,1)
    MA_list=['60']

    stock_type = {
    'kospi': 'stockMkt',
    'kosdaq': 'kosdaqMkt'
    }

    kospi_df = get_download_kospi()
    kospi_df = kospi_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

    img_dir='./img/kospi'
    os.system(
        "mkdir -p {dir}".format(dir=img_dir)
    )
    #get_group_charts(kospi_df, start, end, MA_list, img_dir)


    SAMSUNG_code = get_code(kospi_df,'삼성전자')
    SAMSUNG_data = data.get_data_yahoo(SAMSUNG_code, start, end)
    KOSPI_data = data.get_data_yahoo('^KS11', start, end)

    # --------------------------- preprocess ---------------------------- #
    SAMSUNG_data = SAMSUNG_data[SAMSUNG_data['Volume'] > 0]

    # MEAN=(SAMSUNG_data.mean(axis=0))
    # STD=(SAMSUNG_data.std(axis=0))
    # MEAN=(SAMSUNG_data.mean(axis=0))
    # SAMSUNG_data = ((SAMSUNG_data - MEAN)/STD + 1) * 100
    # print(MEAN)
    visualizer = Visualizer()

    visualizer.plot_basic(SAMSUNG_data,SAMSUNG_code)
    # visualizer.add_moving_avg('5')
    # visualizer.add_moving_avg('15')
    # visualizer.add_moving_avg_line('30')
    # visualizer.add_moving_avg_line('60')
    # visualizer.add_moving_avg_line('90')
    #visualizer.add_ref_line(KOSPI_data)
    visualizer.save('./img/temp.png')


    # xdate = SAMSUNG_data.index[0]

    # for i in range(len(xdate)): 
    #     xdate[i] = xdate[i][2:]
    #     print(xdate[i] )


    # visualizer = Visualizer()
    # visualizer.prepare(SAMSUNG_data, '삼성전자')
    # visualizer.save('./temp.png')
    # print(SAMSUNG_data)


    # kosdaq_df = get_download_kosdaq()
    # kosdaq_df = kosdaq_df.rename(columns={'회사명': 'name', '종목코드': 'code'})



    # for i in range(len(kospi_df))[:50]:
    #     name = kospi_df['name'][i]
    #     code = kospi_df['code'][i]
    #     try:
    #         print(code,name)
    #         df = data.get_data_yahoo(code,start,end)
    #         kospi_df['yahoo_exist']='True'
    #         print("True")

    #         break
    #     except:
    #         kospi_df['yahoo_exist']='False'
    #         print("False")
    #         continue











