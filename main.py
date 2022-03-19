import argparse
import os
from analyzer.analyzer import Analyzer
from DB.korDB_manager import KoreaDB_manager
from DB.database import DataBase
from utils.visualizer import Visualizer
from utils.section import *



def getArgs():

    parser = argparse.ArgumentParser(description="Stone82")

    parser.add_argument(
        '--img-dir', 
        default='imgs'
    )
    parser.add_argument(
        '--cmd'
    )

    parser.add_argument(
        '--date',
        type=str,
        default='19950502'
    )


    args = parser.parse_args()
    return args


if __name__ == "__main__":

    FLAGS = getArgs()
    visualizer = Visualizer()
    
    manager = KoreaDB_manager(
        host=os.environ.get('MYSQL_HOST'),
        db_name='KOR_DB',
        pwd=os.environ.get('MYSQL_ROOT_PASSWORD'),
        user=os.environ.get('MYSQL_USER'),
    )

    db = DataBase(
        host=os.environ.get('MYSQL_HOST'),
        db_name='KOR_DB',
        pwd=os.environ.get('MYSQL_ROOT_PASSWORD'),
        user=os.environ.get('MYSQL_USER'),
    )


    print(f'[D] cmd: {FLAGS.cmd}')

    if FLAGS.cmd == 'update':
        start_date = FLAGS.date
        funct = manager.asyncUpdateDailyPrice
        manager.runAsyncUpdate(funct, start_date=start_date)

    elif FLAGS.cmd == 'chart':
        
        code = '005930'
        os.makedirs(FLAGS.img_dir,exist_ok=True)
        img_path = os.path.join(FLAGS.img_dir,f"{code}.png")
        data = db.getDailyPrice(code, '2018-01-04', '2018-12-30')
        visualizer.drawCandleStick(
            data,
            title=f"{code}",
        )
        visualizer.save(img_path)
        print(data)
        # print(type(data))
    elif FLAGS.cmd == 'debug':
        data = db.getDailyPrice('*', '2022-01-01', '2022-05-30')
        print( data)

    else:
        print(f'[E] invald cmd: {FLAGS.cmd}')

    # df = manager.crawlDataFromKRX(date)


    # manager.replaceIntoDB(df, date)

    # data = db.getDailyPrice('005930', date, date)
    # print(df)
    # manager.updateDailyPrice(date)

    # # ------------------------  COMPLETE ------------------------- #
    # START = '2021-01-13'
    # END = '2022-01-23'
    # company_list = ['삼성전자', '파크시스템스']  # ['RCL' ,'NCLH']
    # # company_list = ['NCLH'] # ['NCLH', 'rcl', 'ccl', 'cuk']
    # data_dict = {}

    # for company in company_list:

    #     dir_path = os.path.join(FLAGS.img_dir, "test")
    #     print(dir_path)
    #     os.makedirs(dir_path, exist_ok=True)
    #     data_dict[company] = db.getDailyPrice(
    #         company, start_date=START, end_date=END)

    #     # candle stick plot
    #     visualizer.drawCandleStick(
    #         data_dict[company_list[0]],
    #         title=company_list[0] + ' 양봉차트',
    #     )
    #     visualizer.save(dir_path+'/candle.png')
    #     visualizer.clear()

    #     # Maximum Drawn Down
    #     visualizer.drawMDD(data_dict[company_list[0]],
    #                        title=company_list[0] + '최대 손실 낙폭')
    #     visualizer.save(dir_path+'/mdd.png')

    #     visualizer.drawEfficFrnt(data_dict)
    #     visualizer.save(dir_path+'/ef.png')
    #     visualizer.clear()

    #     visualizer.drawTrndBolnBand(
    #         data_dict[company_list[0]], title=company_list[0] + ' 볼린저 밴드 (추세추종)')
    #     visualizer.save(dir_path+'/BB_trend.png')
    #     visualizer.clear()

    #     visualizer.drawRvrsBolnBand(
    #         data_dict[company_list[0]], title=company_list[0] + ' 볼린저 밴드 (반전매매)')
    #     visualizer.save(dir_path + '/BB_reverse.png')
    #     visualizer.clear()

    #     visualizer.drawTrplScrnTrd(
    #         data_dict[company_list[0]],
    #         title=company_list[0] + ' 삼중창 매매')
    #     visualizer.save(dir_path+'/Triple.png')
    #     visualizer.clear()

    #     # # scatter plot
    #     # visualizer.drawScatter(
    #     #     x_data=data_dict[company_list[0]],
    #     #     x_data_name=company_list[0],
    #     #     y_data=data_dict[company_list[1]],
    #     #     y_data_name=company_list[1],
    #     #     title='산점도'
    #     # )
    #     # visualizer.save('./imgs/scatter.png')
    #     # visualizer.clear()

    # # Daily percent changes
    # visualizer.drawDPC(data_dict, title=company_list[0] + ' 관련주식')
    # visualizer.save('./imgs/dpc.png')
    # visualizer.clear()

    # # Index plot
    # visualizer.drawIndex(data_dict, title=company_list[0] + ' 지수화')
    # visualizer.save('./imgs/index.png')
    # visualizer.clear()

    # # momentum
    # df_rltv = db.getRltvMomntm(30, '2021-01-01', '2021-02-21')
    # df_abs = db.getAbsMomntm(df_rltv, '2021-01-01', '2021-02-21')

    # # for company in company_list:
    # #     data = manager.getDataFromYahoo(company,'2017-04-01')
    # #     data_dict[company] = data.rename(columns={'Date':'date','Close':'close',
    # #         'Open':'open','High':'high','Low':'low','Volume':'volume'})
