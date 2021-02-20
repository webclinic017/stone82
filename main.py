import argparse
import os
from utils.analyzer import Analyzer
from utils.korDB_manager import KoreaDB_manager
from utils.visualizer import Visualizer
from utils.database import DataBase
from utils.section import *


# START = datetime(2019,1,1)
# END = datetime(2021,1,24)


def getArgs():
    
    parser = argparse.ArgumentParser(description="CSJ Dataset creation.")
    parser.add_argument('--ver', choices=['v1', 'v2'], default='v2')
    parser.add_argument('--nation', default='korea')
    args = parser.parse_args()
    return args 





if __name__ == "__main__":


    FLAGS = getArgs()

    visualizer = Visualizer()
    manager = KoreaDB_manager()
    db = DataBase()




    # ------------------------  COMPLETE ------------------------- #  
    START='2019-06-01'
    END='2021-02-21'
    company_list = ['휴먼엔','엔씨소프트'] # ['RCL' ,'NCLH']
    #company_list = ['NCLH'] #['NCLH', 'rcl', 'ccl', 'cuk']
    data_dict = {}

    # data prepare
    for company in company_list:
        data_dict[company] = db.getDailyPrice(company, start_date=START,end_date=END)

    df_rltv = db.getRltvMomntm(30, '2021-01-01','2021-02-21')

#    df_abs = db.getAbsMomntm(df_rltv, '2021-01-01', '2021-02-21')

    # for company in company_list:
    #     data = manager.getDataFromYahoo(company,'2017-04-01')
    #     data_dict[company] = data.rename(columns={'Date':'date','Close':'close',
    #         'Open':'open','High':'high','Low':'low','Volume':'volume'})
        


    # # candle stick plot
    # visualizer.drawCandleStick(
    #     data_dict[company_list[0]], 
    #     title=company_list[0]+ ' 양봉차트', 
    #     add_ma=True
    # )
    # visualizer.save('./imgs/candle.png')
    # visualizer.clear()

    # # scatter plot
    # visualizer.drawScatter(
    #     x_data=data_dict[company_list[0]], 
    #     x_data_name=company_list[0], 
    #     y_data=data_dict[company_list[1]],
    #     y_data_name=company_list[1],
    #     title='산점도'
    # )
    # visualizer.save('./imgs/scatter.png')
    # visualizer.clear()

    # # Daily percent changes
    # visualizer.drawDPC(data_dict, title=company_list[0] + ' 관련주식')
    # visualizer.save('./imgs/dpc.png')
    # visualizer.clear()

    # # Index plot
    # visualizer.drawIndex(data_dict, title=company_list[0] + ' 지수화')
    # visualizer.save('./imgs/index.png')
    # visualizer.clear()

    # # Maximum Drawn Down
    # visualizer.drawMDD(data_dict[company_list[0]], title=company_list[0] + '최대 손실 낙폭')
    # visualizer.save('./imgs/mdd.png')

    # visualizer.drawEfficFrnt(data_dict)
    # visualizer.save('./imgs/ef.png')
    # visualizer.clear()

    visualizer.drawTrndBolnBand(data_dict[company_list[0]], title=company_list[0] +' 볼린저 밴드 (추세추종)')
    visualizer.save('./imgs/BB_trend.png')
    visualizer.clear()


    visualizer.drawRvrsBolnBand(data_dict[company_list[0]], title=company_list[0] +' 볼린저 밴드 (반전매매)')
    visualizer.save('./imgs/BB_reverse.png')
    visualizer.clear()

    visualizer.drawTrplScrnTrd(
        data_dict[company_list[0]], 
        title=company_list[0] +' 삼중창 매매')
    visualizer.save('./imgs/Triple.png')
    visualizer.clear()
