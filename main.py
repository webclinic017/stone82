

import argparse
import os
from utils.data_manager import DataManager
from utils.data_load import KoreaDataLoader
from datetime import datetime
from data.section import *


start = datetime(2019,1,1)
end = datetime(2021,1,24)



def getArgs():
    
    parser = argparse.ArgumentParser(description="CSJ Dataset creation.")
    parser.add_argument('--ver', choices=['v1', 'v2'], default='v2')
    parser.add_argument('--data_path', default='data')
    parser.add_argument('--market_type', default='kospi')
    args = parser.parse_args()
    return args 





def get_charts(data_manager, data_loader, company_dict, img_dir):

    KOSPI_data = data_loader.data_from_yahoo('^KS11', start, end)
    for code,name in company_dict.items():
        if code == 'type' : continue
        print(f'processing {code}:{name}. . .')
        try:
            data = data_loader.data_from_yahoo(code, start, end)
            data_manager.load_data(data)
            data_manager.plot(name, code)
            data_manager.add_MA_line('5')
            data_manager.add_MA_line('20')
            data_manager.add_MA_line('60')
            data_manager.add_MA_line('224')
            data_manager.add_ref_line(KOSPI_data, name='KOSPI')
            save_path = os.path.join(img_dir, name +'.png')
            data_manager.save(save_path)
            data_manager.clear()
        except:
            print(f'[ERROR!] please check name: {code}')




if __name__ == "__main__":


    FLAGS = getArgs()



    # ------------------------ Preprocess -------------------- #
    data_manager = DataManager()
    data_loader =  KoreaDataLoader()
    # kospi_codes = data_loader.download_stock_codes('kospi')
    # kosdaq_codes = data_loader.download_stock_codes('kosdaq')
    kospi_img_dir='./img/kospi'
    kosdaq_img_dir='./img/kosdaq'
    os.system(
        "mkdir -p {kospi_dir} {kosdaq_dir}".format(
            kospi_dir=kospi_img_dir, kosdaq_dir=kosdaq_img_dir)
    )


    # ----------------------- main ------------------------- #
    target_dict = battery_dict
    section_dir = os.path.join('img',target_dict['type'])
    os.system("mkdir -p {dir}".format(dir=section_dir))
    # get_charts(data_manager, data_loader, target_dict, section_dir)


    # ------------------------------------------------- #
    KOSPI_data = data_loader.data_from_yahoo('^KS11', start, end)
    img_dir = kospi_img_dir
    for code, name in target_dict.items():
        print(code,name)
        if code == 'type' : continue
        data = data_loader.data_from_yahoo(code, start, end)
        data_manager.load_data(data)
        data_manager.plot(name, code)
        data_manager.add_ref_line(KOSPI_data, name='KOSPI')
        save_path = os.path.join(img_dir, name +'.png')
        data_manager.save(save_path)