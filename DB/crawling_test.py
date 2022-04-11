import dart_fss as dart
import time
import asyncio
import os

dart.set_api_key(api_key="8ba06a012b644df0819f3035d024f905c71e0165")


code_list = ["005930", "376190", "377220", "383800", "388790"]


def proxy_func(data, bgn_de, report_tp):
    return data.extract_fs(bgn_de=bgn_de, report_tp=report_tp)


async def getDataFromDARTtoCSV(code):
    fsdata_dir = 'fsdata'
    bgn_de = 20000101
    os.makedirs(fsdata_dir, exist_ok=True)

    corp_list = dart.get_corp_list()
    data = await loop.run_in_executor(None, corp_list.find_by_stock_code, code)

    # print(f"[D] code: {code}")
    # print(f"[D] type(data): {type(data)}")

    tp_list = ['bs', 'is', 'cis', 'cf']
    fs = await loop.run_in_executor(None, proxy_func,
                                    data, bgn_de, 'quarter')

    return fs
    # if fs is not None:
    #     for tp in tp_list:
    #         filepath = os.path.join(
    #             fsdata_dir, f"{code}_{tp}.csv")
    #         df = fs[tp]
    #         if df is not None:
    #             df.to_csv(filepath, encoding="euc-kr")
    #             print(f"[D] save file : {filepath}")
    #         else:
    #             print(f"[E] skip file: {filepath}")


async def main():

    futures = [asyncio.ensure_future(
        getDataFromDARTtoCSV(code)) for code in code_list]
    result = await asyncio.gather(*futures)
    print(result)
if __name__ == '__main__':

    begin = time.time()
    loop = asyncio.get_event_loop()          # 이벤트 루프를 얻음
    loop.run_until_complete(main())          # main이 끝날 때까지 기다림
    loop.close()
    end = time.time()
    print('실행 시간: {0:.3f}초'.format(end - begin))
    # process_sync()

    # asyncio.run(process_async(corp_list))

    # # Open DART API KEY 설정
    # api_key = os.environ['DART_KEY']

    # dart.set_api_key(api_key=api_key)

    # crop_list = dart.get_corp_list()

    # code = "000020"

    # data = crop_list.find_by_stock_code(code)

    # print(data.info)

    # # try:

    # fs = data.extract_fs(bgn_de=20000101)

    # # except:
    # #     print("??")
    # df_fs = fs['bs']
    # # 연결재무상태표 추출에 사용된 Label 정보
    # labels_fs = fs.labels['bs']
    # # print(f"[D] labels_fs: {labels_fs}")
    # # print("-----------------------------")
    # # print(f"[D] df_fs: {df_fs}")
    # # print(f"[D] df_fs type: {type(df_fs)}")
    # df_fs.to_csv(f"fsdata/{code}_bs.csv")
    # print(f"[D] save to : fsdata/{code}_bs.csv")

    # # 연결손익계산서
    # df_is = fs['is']  # 또는 df = fs[1] 또는 df = fs.show('is')
    # # 연결손익계산서 추출에 사용된 Label 정보
    # labels_is = fs.labels['is']
    # df_fs.to_csv(f"fsdata/{code}_is.csv")
    # print(f"[D] save to : fsdata/{code}_is.csv")

    # # 연결포괄손익계산서
    # df_ci = fs['cis']  # 또는 df = fs[2] 또는 df = fs.show('cis')
    # # 연결포괄손익계산서 추출에 사용된 Label 정보
    # labels_ci = fs.labels['cis']
    # df_fs.to_csv(f"fsdata/{code}_cis.csv")
    # print(f"[D] save to : fsdata/{code}_cis.csv")

    # # 현금흐름표
    # df_cf = fs['cf']  # 또는 df = fs[3] 또는 df = fs.show('cf')
    # # 현금흐름표 추출에 사용된 Label 정보
    # labels_cf = fs.labels['cf']
    # # # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
    # df_fs.to_csv(f"fsdata/{code}_bs.csv")
    # print(f"[D] save to : fsdata/{code}_bs.csv")
