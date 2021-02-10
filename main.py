import argparse
import os
from utils.analyzer import Analyzer
from utils.korDB_manager import KoreaDB_manager
from utils.visualizer import Visualizer
from utils.database import DataBase
from utils.section import *

from datetime import datetime


start = datetime(2019,1,1)
end = datetime(2021,1,24)



def getArgs():
    
    parser = argparse.ArgumentParser(description="CSJ Dataset creation.")
    parser.add_argument('--ver', choices=['v1', 'v2'], default='v2')
    parser.add_argument('--nation', default='korea')
    args = parser.parse_args()
    return args 





# def get_charts(data_manager, data_loader, company_dict, img_dir):

#     KOSPI_data = data_loader.data_from_yahoo('^KS11', start, end)
#     for code,name in company_dict.items():
#         if code == 'type' : continue
#         print(f'processing {code}:{name}. . .')
#         try:
#             data = data_loader.data_from_yahoo(code, start, end)
#             data_manager.load_data(data)
#             data_manager.plot(name, code)
#             data_manager.add_MA_line('5')
#             data_manager.add_MA_line('20')
#             data_manager.add_MA_line('60')
#             data_manager.add_MA_line('224')
#             data_manager.add_ref_line(KOSPI_data, name='KOSPI')
#             save_path = os.path.join(img_dir, name +'.png')
#             data_manager.save(save_path)
#             data_manager.clear()
#         except:
#             print(f'[ERROR!] please check name: {code}')




if __name__ == "__main__":


    FLAGS = getArgs()

    visualizer = Visualizer()
    manager = KoreaDB_manager()
    db = DataBase()



    # company_list = ['RCL', 'NCLH', 'CCL', 'CUK']
    # data_list=[]

    # for company in company_list:

    #     data= manager.getDataFromYahoo(company,'2020-03-01','2021-02-01')
    #     data = data.rename(columns={'Date':'date','Close':'close',
    #         'Open':'open','High':'high','Low':'low','Volume':'volume'})
    #     data_list.append(data)

    # visualizer.drawCandleStick(data_list[0], company_list[0])
    # visualizer.save('./imgs/CANDLE.png')
    # visualizer.clear()

    # visualizer.drawDPC(data_list, company_list, title=company_list[0] +'관련주식')
    # visualizer.save('./imgs/DPC.png')





    # ------------------------  COMPLETE ------------------------- #    
    company_list = ['', 'SK하이닉스']
    data_list=[]


    for company in company_list:
        data = db.getDailyPrice(company, start_date='2018-06-01',end_date='2020-12-01')
        data_list.append(data)


    visualizer.drawCandleStick(
        data_list[0], 
        start_date=None, 
        end_date=None, 
        title=company_list[0]+ ' 양봉차트', 
        add_ma=True
    )
    visualizer.save('./imgs/CANDLE.png')
    visualizer.clear()


    visualizer.drawDPC(data_list, company_list, title=company_list[0] + ' 관련주식')
    visualizer.save('./imgs/DPC.png')
    visualizer.clear()

    visualizer.drawMDD(data_list[0], title=company_list[0] + '최대 손실 낙폭')
    visualizer.save('./imgs/MDD.png')











    # data_loader.addCodeList('./data/korea/code.xls')

    # name = '삼성전자'
    # code = data_loader.getCode(name)
 
    # #data = data_loader.getDataFromNaver(code=code,pages_to_fetch=3)
    # data = data_loader.getDataFromNaver(code=code,pages_to_fetch=3)

    # print(data)




    # kospi_img_dir='./img/kospi'
    # kosdaq_img_dir='./img/kosdaq'
    # os.system(
    #     "mkdir -p {kospi_dir} {kosdaq_dir}".format(
    #         kospi_dir=kospi_img_dir, kosdaq_dir=kosdaq_img_dir)
    # )


    # # ----------------------- main ------------------------- #
    # target_dict = battery_dict
    # section_dir = os.path.join('img',target_dict['type'])
    # os.system("mkdir -p {dir}".format(dir=section_dir))
    # get_charts(data_manager, data_loader, target_dict, section_dir)


    # # ------------------------------------------------- #
    # KOSPI_data = data_loader.data_from_yahoo('^KS11', start, end)
    # img_dir = kospi_img_dir
    # for code, name in target_dict.items():
    #     print(code,name)
    #     if code == 'type' : continue
    #     data = data_loader.data_from_yahoo(code, start, end)
    #     data_manager.load_data(data)
    #     data_manager.plot(name, code)
    #     data_manager.add_ref_line(KOSPI_data, name='KOSPI')
    #     save_path = os.path.join(img_dir, name +'.png')
    #     data_manager.save(save_path)