from korDB_manager import KoreaDB_manager
import argparse
import os
from datetime import datetime
import dart_fss as dart


def getArgs():

    parser = argparse.ArgumentParser(
        description=""" DB manager """)
    parser.add_argument(
        '--update-num',
        type=int,
        default=1
    )

    args = parser.parse_args()
    return args


def getDataFromDARTtoCSV(self, code):
    fsdata_dir = 'fsdata'
    bgn_de = 20000101
    os.makedirs(fsdata_dir, exist_ok=True)

    dart.set_api_key(api_key="8ba06a012b644df0819f3035d024f905c71e0165")
    corp_list = dart.get_corp_list()
    data = corp_list.find_by_stock_code(code)

    print(f"[D] code: {code}")
    print(f"[D] type(data): {type(data)}")

    tp_list = ['bs', 'is', 'cis', 'cf']
    try:
        fs = data.extract_fs(
            bgn_de=20000101, report_tp='quarter')
    except:
        pass

    for tp in tp_list:
        filepath = os.path.join(
            fsdata_dir, f"{code}_{tp}.csv")
        df = fs[tp]
        if df is not None:
            df.to_csv(filepath, encoding="euc-kr")
            print(f"[D] save file : {filepath}")
        else:
            print(f"[E] skip file: {filepath}")


if __name__ == '__main__':

    FLAGS = getArgs()

    kor_db = KoreaDB_manager(
        host='localhost', db_name="KOR_DB", pwd=os.environ['MYSQL_ROOT_PASSWORD'])

    code_list = list(kor_db.code_dict.keys())
    for i, code in enumerate(code_list):
        df = kor_db.crawlDataFromNaver(code=code)
        if df is not None:
            kor_db.replaceIntoDB(df, i, code, 'temp')
        # corp_code = kor_db.stockCode2corpCode("000020")
        # print(corp_code)
        # kor_db.loadDARTData()
        # kor_db.getDataFromDARTtoCSV("000020")
        # kor_db.updateFS("process", 8)

        # kor_db.updateFS(bgn_de=20000101)

        # update_time = str(datetime.today().strftime('%Y%m%d'))

        # api_key = os.environ['DART_KEY']

        # dart.set_api_key(api_key=api_key)

        # crop_list = dart.get_corp_list()

        # code_dict = kor_db.getCodes()
        # print(code_dict)
        # code = "000020"
        # data = crop_list.find_by_stock_code(code)
        # # fs = data.extract_fs(
        # #     bgn_de=20210101, report_tp='quarter', cumulative=False)
        # fs = data.extract_fs(
        #     bgn_de=20210101, report_tp='annual')

        # df_fs = fs['bs']
        # # 연결재무상태표 추출에 사용된 Label 정보
        # # print(f"[D] labels_fs: {labels_fs}")
        # # print("-----------------------------")
        # # print(f"[D] df_fs: {df_fs}")
        # # print(f"[D] df_fs type: {type(df_fs)}")
        # df_fs.to_csv(f"fsdata/{code}_bs.csv", encoding="euc-kr")
        # print(f"[D] save to : fsdata/{code}_bs.csv")

        # # 연결손익계산서
        # df_is = fs['is']  # 또는 df = fs[1] 또는 df = fs.show('is')
        # # 연결손익계산서 추출에 사용된 Label 정보
        # df_is.to_csv(f"fsdata/{code}_is.csv", encoding="euc-kr")
        # print(f"[D] save to : fsdata/{code}_is.csv")

        # # 연결포괄손익계산서
        # df_cis = fs['cis']  # 또는 df = fs[2] 또는 df = fs.show('cis')
        # # 연결포괄손익계산서 추출에 사용된 Label 정보
        # df_cis.to_csv(f"fsdata/{code}_cis.csv", encoding="euc-kr")
        # print(f"[D] save to : fsdata/{code}_cis.csv")

        # # 현금흐름표
        # df_cf = fs['cf']  # 또는 df = fs[3] 또는 df = fs.show('cf')
        # # 현금흐름표 추출에 사용된 Label 정보
        # labels_cf = fs.labels['cf']
        # # # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
        # df_cf.to_csv(f"fsdata/{code}_cf.csv", encoding="euc-kr")
        # print(f"[D] save to : fsdata/{code}_cf.csv")

        # print(data.info)
        # fs.save()

        # for i, code in enumerate(code_dict.keys()):
        #     try:
        #         data = crop_list.find_by_stock_code(code)
        #         # fs = data.extract_fs(bgn_de=20000101)
        #         fs = data.extract_fs(
        #             bgn_de=20000101, report_tp='quarter', cumulative=False)
        #         df_fs = fs['bs']
        #         # 연결재무상태표 추출에 사용된 Label 정보
        #         labels_fs = fs.labels['bs']
        #         # print(f"[D] labels_fs: {labels_fs}")
        #         # print("-----------------------------")
        #         # print(f"[D] df_fs: {df_fs}")
        #         # print(f"[D] df_fs type: {type(df_fs)}")
        #         df_fs.to_csv(f"fsdata/{code}_bs.csv")
        #         print(f"[D] save to : fsdata/{code}_bs.csv")

        #         # 연결손익계산서
        #         df_is = fs['is']  # 또는 df = fs[1] 또는 df = fs.show('is')
        #         # 연결손익계산서 추출에 사용된 Label 정보
        #         labels_is = fs.labels['is']
        #         df_fs.to_csv(f"fsdata/{code}_is.csv")
        #         print(f"[D] save to : fsdata/{code}_is.csv")

        #         # 연결포괄손익계산서
        #         df_ci = fs['cis']  # 또는 df = fs[2] 또는 df = fs.show('cis')
        #         # 연결포괄손익계산서 추출에 사용된 Label 정보
        #         labels_ci = fs.labels['cis']
        #         df_fs.to_csv(f"fsdata/{code}_cis.csv")
        #         print(f"[D] save to : fsdata/{code}_cis.csv")

        #         # 현금흐름표
        #         df_cf = fs['cf']  # 또는 df = fs[3] 또는 df = fs.show('cf')
        #         # 현금흐름표 추출에 사용된 Label 정보
        #         labels_cf = fs.labels['cf']
        #         # # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
        #         df_fs.to_csv(f"fsdata/{code}_bs.csv")
        #         print(f"[D] save to : fsdata/{code}_bs.csv")
        #     except:
        #         print(f"[E] pass : {code}")
