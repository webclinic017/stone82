import numpy as np
import copy
from datetime import datetime
from analyzer.analyzer import Analyzer
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib
from mplfinance.original_flavor import candlestick2_ohlc
#from mplfinance import candlestick_ohlc
import matplotlib.pyplot as plt
plt.switch_backend('agg')

NUM_D_of_Y = 224

matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['font.size'] = 12
analyzer = Analyzer(NUM_D_of_Y)


class Visualizer:

    def __init__(self, vnet=False):

        self.fig = None
        self.MA_NUMS = [5, 20, 60, 120, NUM_D_of_Y]

    # ------------------------- Plotting funct. ------------------------- #

    def drawCandleStick(self, data,  ma_list=None, title='Candle chart'):
        """ Ploting basic candle stick chart """

        # set fig
        self.fig = plt.figure(figsize=(20, 10))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=3, colspan=4)
        top_axes.get_yaxis().get_major_formatter().set_scientific(False)

        bottom_axes = plt.subplot2grid(
            (4, 4), (3, 0), rowspan=1, colspan=4, sharex=top_axes)
        bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

        # top axes
        if ma_list is not None :
            color_list = ['k', 'y', 'g', 'orange', 'c', 'k']

            for idx, ma in enumerate(ma_list):
                ma_data = analyzer.getMovingAvg(data, ma)

            # dt_range = pd.date_range(start=start_date, end=end_date)
            # data = data[data.index.isin(dt_range)]
            index = data.index.astype('str')

            for idx, ma in enumerate(ma_list):
                moving_avg = 'MA-'+str(ma)
                top_axes.plot(index, data[moving_avg], color_list.pop(
                    0), label=moving_avg, linewidth=0.7+idx*0.4)
            top_axes.legend(loc='best', fontsize=15)

        else:
            # dt_range = pd.date_range(start=start_date, end=end_date)
            # data = data[data.index.isin(dt_range)]
            index = data.index.astype('str')

        candlestick2_ohlc(top_axes, data['open'], data['high'], data['low'],
                          data['close'], width=0.5, colorup='r', colordown='b')
        top_axes.set_title(title, fontsize=30)
        top_axes.grid(True)
        #plt.xticks(rotation = 45)

        # bottom axes
        def color_fuc(x): return 'r' if x >= 0 else 'b'
        color_list = list(data['volume'].diff().fillna(0).apply(color_fuc))
        bottom_axes.xaxis.set_major_locator(ticker.MaxNLocator(10))
        bottom_axes.bar(index, data['volume'], width=0.5,
                        align='center', color=color_list)
        bottom_axes.set_xlabel('Date', fontsize=15)

    def drawMDD(self, data, title='MDD chart'):
        """ ploting maximum draw down chart """

        # set fig
        self.fig = plt.figure(figsize=(20, 15))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=2, colspan=4)
        bottom_axes = plt.subplot2grid(
            (4, 4), (2, 0), rowspan=2, colspan=4, sharex=top_axes)
        bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

        # draw candle stick chart
        data = data[data['volume'] > 0]
        max_high = data['high'].max()
        min_low = data['low'].min()
        top_axes.set_ylim([min_low, max_high])
        candlestick2_ohlc(top_axes, data['open'], data['high'], data['low'],
                          data['close'], width=0.5, colorup='r', colordown='b')
        index = data.index.astype('str')  # 캔들스틱 x축이 str로 들어감

        # draw MDD chart
        dd, max_dd = analyzer.getDrawDown(data)
        bottom_axes.plot(index, dd, c='blue', label='DD')
        bottom_axes.plot(index, max_dd,  c='red', label='MDD')

        # title setup
        top_axes.set_title(title, fontsize=30)
        top_axes.xaxis.set_major_locator(ticker.MaxNLocator(10))
        top_axes.grid(True)

        bottom_axes.set_xlabel('Date', fontsize=15)
        bottom_axes.grid(True)
        bottom_axes.legend(loc='best', fontsize=20)

        plt.tight_layout()

    def drawIndex(self, data_dict, title='Index'):
        """ ploting index  """

        # assert (len(data_dict) <= len(self.COLORS))
        #color_list = copy.deepcopy(self.COLORS)
        color_list = ['r', 'b', 'g', 'c', 'k', 'y']

        # set fig
        self.fig = plt.figure(figsize=(20, 10))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=4, colspan=4)

        # draw DPC chart
        for name, data in data_dict.items():
            index_data = analyzer.getIndex(data)
            top_axes.plot(data.index, index_data,
                          color_list.pop(0), label=name)

        # title
        top_axes.set_title(title, fontsize=30)
        top_axes.set_xlabel('Date', fontsize=15)
        top_axes.set_ylabel('Index', fontsize=15)
        top_axes.grid(True)
        top_axes.legend(loc='best', fontsize=15)

    def drawScatter(self, x_data, x_data_name, y_data, y_data_name, title='Scattor plot'):
        """ ploting index  """

        # # set fig
        self.fig = plt.figure(figsize=(10, 10))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=4, colspan=4)

        df = pd.DataFrame({'X': x_data['close'], 'Y': y_data['close']})
        df = df.fillna(method='bfill')
        df = df.fillna(method='ffill')

        regress = analyzer.getLinearRegress(df['X'], df['Y'])
        regress_line = f'Y = {regress.slope:.2f} * X + {regress.intercept:.2f}'

        top_axes.set_title(title + f' (R = {regress.rvalue:.2f})', fontsize=30)
        top_axes.scatter(df['X'], df['Y'], marker='.')
        top_axes.plot(df['X'], regress.slope *
                      df['X'] + regress.intercept, 'r')
        top_axes.set_xlabel(x_data_name, fontsize=15)
        top_axes.set_ylabel(y_data_name, fontsize=15)
        top_axes.legend(
            [regress_line, f'{x_data_name} x {y_data_name}'], loc='best', fontsize=15)

    def drawDPC(self, data_dict, title='Daily Percent Changes'):
        """ ploting daily percent changes """

        # set fig
        self.fig = plt.figure(figsize=(20, 10))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=4, colspan=4)
        color_list = ['r', 'b', 'g', 'c', 'k', 'y']

        # draw DPC chart
        for name, data in data_dict.items():
            data_dpc_cs = analyzer.getDailyPercChanges(data)
            top_axes.plot(data.index, data_dpc_cs,
                          color_list.pop(0), label=name)

        # title
        top_axes.set_title(title, fontsize=30)
        top_axes.set_xlabel('Date', fontsize=15)
        top_axes.set_ylabel('Changes (%)', fontsize=15)
        top_axes.grid(True)
        top_axes.legend(loc='best', fontsize=15)

    def drawEfficFrnt(self, data_dict, title='Efficient Frontier'):
        """ ploting efficient frontier """

        # set fig
        self.fig = plt.figure(figsize=(20, 10))
        top_axes = plt.subplot2grid((4, 4), (0, 0), rowspan=4, colspan=4)

        df = analyzer.getEfficFront(data_dict)

        max_sharpe = df.loc[df['sharpe'] == df['sharpe'].max()]
        min_risk = df.loc[df['risk'] == df['risk'].min()]

        top_axes.set_title(title, fontsize=30)
        top_axes.scatter(x=df['risk'], y=df['returns'], c=df['sharpe'],
                         cmap='viridis', edgecolors='k', marker='.')
        top_axes.grid(True)
        top_axes.scatter(
            x=max_sharpe['risk'], y=max_sharpe['returns'], c='r', marker='*', s=300)
        top_axes.scatter(
            x=min_risk['risk'], y=min_risk['returns'], c='r', marker='X', s=300)
        top_axes.set_xlabel('Risk', fontsize=15)
        top_axes.set_ylabel('Expected returns', fontsize=15)
        top_axes.legend(['porfoilo', 'max_sharpe', 'min_risk'],
                        loc='best', fontsize=15)

    def drawTrndBolnBand(self, data, MA_num=20, MFI_num=10, title='Bollinger Band'):
        """ ploting Bollinger Band """

        moving_avg = 'MA-' + str(MA_num)
        MFI = 'MFI-' + str(MFI_num)

        df = analyzer.getTrndBolnBand(data, MA_num, MFI_num=10)

        # set fig
        self.fig = plt.figure(figsize=(20, 15))
        top_axes = plt.subplot2grid((5, 5), (0, 0), rowspan=3, colspan=5)
        mid_axes = plt.subplot2grid((5, 5), (3, 0), rowspan=1, colspan=5)
        mid_axes.get_yaxis().get_major_formatter().set_scientific(False)
        bottom_axes = plt.subplot2grid((5, 5), (4, 0), rowspan=1, colspan=5)
        bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

        # top axis
        top_axes.plot(df.index, df['close'], color='#0000ff', label='Close')
        top_axes.plot(df.index, df['upper'], 'r--', label='Upper Band')
        top_axes.plot(df.index, df[moving_avg], 'k--', label=moving_avg)
        top_axes.plot(df.index, df['lower'], 'c--', label='Lower Band')
        top_axes.fill_between(df.index, df['upper'], df['lower'], color='0.9')
        top_axes.set_title(title, fontsize=30)
        top_axes.set_ylabel('Price', fontsize=15)
        top_axes.legend(loc='best', fontsize=15)

        # mid axis
        mid_axes.plot(df.index, df['PB'] * 100, color='b', label='%B x 100')
        mid_axes.plot(df.index, df[MFI], 'g--', label=f'MFI({MFI_num} day)')
        mid_axes.grid(True)
        mid_axes.set_ylabel('%B x 100', fontsize=10)
        mid_axes.legend(loc='best', fontsize=10)

        # bottom axis
        bottom_axes.plot(df.index, df['BW'], color='m', label='Bandwidth')
        bottom_axes.grid(True)
        bottom_axes.set_ylabel('Bandwidth (%)', fontsize=15)
        bottom_axes.set_xlabel('Date', fontsize=15)

        # sell & buy
        for i in range(len(df.close)):
            if df['PB'].values[i] > 0.8 and df[MFI].values[i] > 80:
                top_axes.plot(df.index.values[i], df['close'].values[i], 'r^')
                mid_axes.plot(df.index.values[i], df[MFI].values[i], 'r^')
                bottom_axes.plot(df.index.values[i], df['BW'].values[i], 'r^')
            elif df['PB'].values[i] < 0.2 and df[MFI].values[i] < 20:
                top_axes.plot(df.index.values[i], df['close'].values[i], 'bv')
                mid_axes.plot(df.index.values[i], df[MFI].values[i], 'bv')
                bottom_axes.plot(df.index.values[i], df['BW'].values[i], 'bv')

    def drawRvrsBolnBand(self, data, MA_num=20, IIP_num=21, title='Bollinger Band'):
        """ ploting Bollinger Band """

        moving_avg = 'MA-' + str(MA_num)
        IIP = 'IIP-' + str(IIP_num)

        df = analyzer.getRvrsdBolnBand(data, MA_num, IIP_num)

        # set fig
        self.fig = plt.figure(figsize=(20, 15))
        top_axes = plt.subplot2grid((5, 5), (0, 0), rowspan=3, colspan=5)
        mid_axes = plt.subplot2grid((5, 5), (3, 0), rowspan=1, colspan=5)
        mid_axes.get_yaxis().get_major_formatter().set_scientific(False)
        bottom_axes = plt.subplot2grid((5, 5), (4, 0), rowspan=1, colspan=5)
        bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

        # top axis
        top_axes.plot(df.index, df['close'], color='#0000ff', label='Close')
        top_axes.plot(df.index, df['upper'], 'r--', label='Upper Band')
        top_axes.plot(df.index, df[moving_avg], 'k--', label=moving_avg)
        top_axes.plot(df.index, df['lower'], 'c--', label='Lower Band')
        top_axes.fill_between(df.index, df['upper'], df['lower'], color='0.9')
        top_axes.set_title(title, fontsize=30)
        top_axes.set_ylabel('Price', fontsize=15)
        top_axes.legend(loc='best', fontsize=15)

        # mid axis
        mid_axes.plot(df.index, df['PB'] * 100, color='b', label='%B x 100')
        mid_axes.grid(True)
        mid_axes.set_ylabel('%B x 100', fontsize=10)

        # bottom axis
        bottom_axes.bar(df.index, df[IIP], color='g', label='Bandwidth')
        bottom_axes.grid(True)
        bottom_axes.set_ylabel(f'II {IIP_num}day (%)', fontsize=15)
        bottom_axes.set_xlabel('Date', fontsize=15)

        # strategy of sell & buy
        for i in range(len(df.close)):
            if df['PB'].values[i] < 0.05 and df[IIP].values[i] > 0:
                top_axes.plot(df.index.values[i], df['close'].values[i], 'r^')
                mid_axes.plot(df.index.values[i], df['PB'].values[i], 'r^')
                bottom_axes.plot(df.index.values[i], df[IIP].values[i], 'r^')
            elif df['PB'].values[i] > 0.95 and df[IIP].values[i] < 0:
                top_axes.plot(df.index.values[i], df['close'].values[i], 'bv')
                mid_axes.plot(df.index.values[i], df['PB'].values[i], 'bv')
                bottom_axes.plot(df.index.values[i], df[IIP].values[i], 'bv')

    def drawTrplScrnTrd(self, data, title='Triple Screen Trading System'):

        # set fig
        self.fig = plt.figure(figsize=(20, 25))
        top_axes = plt.subplot2grid((8, 8), (0, 0), rowspan=3, colspan=8)
        top_axes.get_yaxis().get_major_formatter().set_scientific(False)
        mid_axes = plt.subplot2grid(
            (8, 8), (3, 0), rowspan=2, colspan=8, sharex=top_axes)
        bottom_axes = plt.subplot2grid(
            (8, 8), (5, 0), rowspan=2, colspan=8, sharex=top_axes)
        volume_axes = plt.subplot2grid(
            (8, 8), (7, 0), rowspan=1, colspan=8, sharex=top_axes)

        df = analyzer.getMACD(data)
        index = df.index.astype('str')

        # top axis
        top_axes.plot(index, df['ema130'], color='c', label='EMA130')
        candlestick2_ohlc(top_axes, df['open'], df['high'], df['low'],
                          df['close'], width=0.5, colorup='r', colordown='b')
        top_axes.legend(loc='best', fontsize=15)
        top_axes.set_title(title, fontsize=30)
        top_axes.set_ylabel('Price', fontsize=15)
        top_axes.legend(loc='best', fontsize=15)
        top_axes.grid(True)

        # mid axis
        mid_axes.bar(index, df['macdhist'], color='m', label='MACD-hist')
        mid_axes.plot(index, df['macd'], color='b', label='MACD')
        mid_axes.plot(index, df['signal'], 'g--', label='MACD-signal')
        mid_axes.grid(True)
        mid_axes.legend(loc='best', fontsize=15)

        # bottom axis
        bottom_axes.plot(index, df['fast_k'], color='c', label='FAST-K (%)')
        bottom_axes.plot(index, df['slow_d'], color='k', label='SLOW-D (%)')
        bottom_axes.set_yticks([0, 20, 80, 100])
        bottom_axes.grid(True)
        bottom_axes.legend(loc='best', fontsize=15)

        # bottom axes
        def color_fuc(x): return 'r' if x >= 0 else 'b'
        color_list = list(df['volume'].diff().fillna(0).apply(color_fuc))
        volume_axes.xaxis.set_major_locator(ticker.MaxNLocator(10))
        volume_axes.bar(index, df['volume'], width=0.5,
                        align='center', color=color_list)
        volume_axes.set_xlabel('Date', fontsize=15)

        # strategy of sell & buy
        ref = 'slow_d'
        for i in range(1, len(df['close'])):
            if df['ema130'].values[i-1] < df['ema130'].values[i] and df[ref].values[i-1] >= 20 and df[ref].values[i] < 20:
                top_axes.plot(index[i], df['ema130'].values[i], 'r^')
                mid_axes.plot(index[i], df['macd'].values[i], 'r^')
                bottom_axes.plot(index[i], df[ref].values[i], 'r^')

            elif df['macdhist'].values[i-1] >= 0 and df['macdhist'].values[i] <= 0:
                top_axes.plot(index[i], df['ema130'].values[i], 'bv')
                mid_axes.plot(index[i], df['macd'].values[i], 'bv')
                bottom_axes.plot(index[i], df[ref].values[i], 'bv')

            elif df['macdhist'].values[i-1] <= 0 and df['macdhist'].values[i] >= 0:
                top_axes.plot(index[i], df['ema130'].values[i], 'rv')
                mid_axes.plot(index[i], df['macd'].values[i], 'rv')
                bottom_axes.plot(index[i], df[ref].values[i], 'rv')

            # elif df['ema130'].values[i-1] > df['ema130'].values[i] and  df[ref].values[i-1] <= 80 and df[ref].values[i] > 80:
                # top_axes.plot(index[i], df['ema130'].values[i], 'bv')
                # mid_axes.plot(index[i], df['macd'].values[i], 'bv')
                # bottom_axes.plot(index[i], df[ref].values[i], 'bv')

        bottom_axes.xaxis.set_major_locator(ticker.MaxNLocator(10))

    # ------------------------- Additional funct. ------------------------- #

    def add_MA_line(self, num_MA):
        """ Adding movie average line """
        moving_avg = 'MA-' + str(num_MA)
        self.ma_list.add(moving_avg)
        self.data[moving_avg] = self.data['Close'].rolling(int(num_MA)).mean()
        self.top_axes.plot(
            self.index, self.data[moving_avg], label=moving_avg, linewidth=0.7)
        self.top_axes.legend()

    def add_ref_line(self, ref_data, name='Reference'):

        # fitted = min_max_scaler.fit(ref_data)
        # output = min_max_scaler.transform(ref_data)
        # output = pd.DataFrame(output, columns=ref_data.columns, index=list(ref_data.index.values))
        # ref_data = output

        mean = (ref_data.mean(axis=0))
        std = (ref_data.std(axis=0))
        ref_data = (ref_data - mean)/std
        self.data['Reference'] = ref_data['Close']

        self.top_axes.plot(
            self.index, self.data['Reference'], label=name, linewidth=0.7)
        self.top_axes.legend()

    def clear(self):

        del self.fig
        self.fig = None

        # _axes = self.top_axes.tolist()
        # for ax in _axes[1:]:
        #     ax.cla()  # 그린 차트 지우기
        #     ax.relim()  # limit를 초기화
        #     ax.autoscale()  # 스케일 재설정

        # _axes = self.bottom_axes.tolist()
        # for ax in _axes[1:]:
        #     ax.cla()  # 그린 차트 지우기
        #     ax.relim()  # limit를 초기화
        #     ax.autoscale()  # 스케일 재설정

        # with lock:
        #     _axes = self.axes.tolist()
        #     for ax in _axes[1:]:
        #         ax.cla()  # 그린 차트 지우기
        #         ax.relim()  # limit를 초기화
        #         ax.autoscale()  # 스케일 재설정
        #     # y축 레이블 재설정
        #     self.axes[1].set_ylabel('Agent')
        #     self.axes[2].set_ylabel('V')
        #     self.axes[3].set_ylabel('P')
        #     self.axes[4].set_ylabel('PV')
        #     for ax in _axes:
        #         ax.set_xlim(xlim)  # x축 limit 재설정
        #         ax.get_xaxis().get_major_formatter() \
        #             .set_scientific(False)  # 과학적 표기 비활성화
        #         ax.get_yaxis().get_major_formatter() \
        #             .set_scientific(False)  # 과학적 표기 비활성화
        #         # x축 간격을 일정하게 설정
        #         ax.ticklabel_format(useOffset=False)

    def save(self, path):
        self.fig.savefig(path)

    if __name__ == '__main__':
        print('hello world')

        # # self.fig = plt.figure(figsize=(20, 10))
        # # self.axes = self.fig.add_subplot(111)
        # # index = data.index.astype('str') # 캔들스틱 x축이 str로 들어감
        # # data['MA5'] = data['Close'].rolling(5).mean()
        # # data['MA15'] = data['Close'].rolling(15).mean()
        # # data['MA30'] = data['Close'].rolling(30).mean()
        # # data['MA60'] = data['Close'].rolling(60).mean()
        # # data['MA120'] = data['Close'].rolling(120).mean()

        # # self.axes.plot(index, data['MA5'], label='MA5', linewidth=0.7)
        # # self.axes.plot(index, data['MA15'], label='MA15', linewidth=0.7)
        # # self.axes.plot(index, data['MA30'], label='MA30', linewidth=0.7)
        # # self.axes.plot(index, data['MA60'], label='MA60', linewidth=0.7)
        # # self.axes.plot(index, data['MA120'], label='MA120', linewidth=0.7)

        # self.axes.xaxis.set_major_locator(ticker.FixedLocator(data.index))
        # self.axes.xaxis.set_major_locator(ticker.MaxNLocator(10))

        # # ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

        # candlestick2_ohlc(self.axes, data['Open'], data['High'], data['Low'], data['Close'], width=0.5, colorup='r', colordown='b')
        # #plt.xticks(rotation = 45)
        # self.axes.legend()

        # with lock:
        #     self.fig.savefig(path)

    # def prepare(self, chart_data, title):

    #     self.title = title
    #     with lock:
    #         # 캔버스를 초기화하고 5개의 차트를 그릴 준비
    #         self.fig, self.axes = plt.subplots(
    #             nrows=5, ncols=1, facecolor='w', sharex=True)
    #         for ax in self.axes:
    #             # 보기 어려운 과학적 표기 비활성화
    #             ax.get_xaxis().get_major_formatter() \
    #                 .set_scientific(False)
    #             ax.get_yaxis().get_major_formatter() \
    #                 .set_scientific(False)
    #             # y axis 위치 오른쪽으로 변경
    #             ax.yaxis.tick_right()
    #         # 차트 1. 일봉 차트
    #         self.axes[0].set_ylabel('Env.')  # y 축 레이블 표시
    #         x = np.arange(len(chart_data))
    #         # open, high, low, close 순서로된 2차원 배열
    #         ohlc = np.hstack((
    #             x.reshape(-1, 1), np.array(chart_data)[:, 1:-1]))
    #         # 양봉은 빨간색으로 음봉은 파란색으로 표시
    #         candlestick_ohlc(
    #             self.axes[0], ohlc, colorup='r', colordown='b')
    #         # 거래량 가시화
    #         ax = self.axes[0].twinx()
    #         volume = np.array(chart_data)[:, -1].tolist()
    #         ax.bar(x, volume, color='b', alpha=0.3)

    # def plot(self, epoch_str=None, num_epoches=None, epsilon=None,
    #         action_list=None, actions=None, num_stocks=None,
    #         outvals_value=[], outvals_policy=[], exps=None,
    #         learning_idxes=None, initial_balance=None, pvs=None):

    #     with lock:
    #         x = np.arange(len(actions))  # 모든 차트가 공유할 x축 데이터
    #         actions = np.array(actions)  # 에이전트의 행동 배열
    #         # 가치 신경망의 출력 배열
    #         outvals_value = np.array(outvals_value)
    #         # 정책 신경망의 출력 배열
    #         outvals_policy = np.array(outvals_policy)
    #         # 초기 자본금 배열
    #         pvs_base = np.zeros(len(actions)) + initial_balance

    #         # 차트 2. 에이전트 상태 (행동, 보유 주식 수)
    #         for action, color in zip(action_list, self.COLORS):
    #             for i in x[actions == action]:
    #                 # 배경 색으로 행동 표시
    #                 self.axes[1].axvline(i, color=color, alpha=0.1)
    #         self.axes[1].plot(x, num_stocks, '-k')  # 보유 주식 수 그리기

    #         # 차트 3. 가치 신경망
    #         if len(outvals_value) > 0:
    #             max_actions = np.argmax(outvals_value, axis=1)
    #             for action, color in zip(action_list, self.COLORS):
    #                 # 배경 그리기
    #                 for idx in x:
    #                     if max_actions[idx] == action:
    #                         self.axes[2].axvline(idx,
    #                             color=color, alpha=0.1)
    #                 # 가치 신경망 출력의 tanh 그리기
    #                 self.axes[2].plot(x, outvals_value[:, action],
    #                     color=color, linestyle='-')

    #         # 차트 4. 정책 신경망
    #         # 탐험을 노란색 배경으로 그리기
    #         for exp_idx in exps:
    #             self.axes[3].axvline(exp_idx, color='y')
    #         # 행동을 배경으로 그리기
    #         _outvals = outvals_policy if len(outvals_policy) > 0 \
    #             else outvals_value
    #         for idx, outval in zip(x, _outvals):
    #             color = 'white'
    #             if np.isnan(outval.max()):
    #                 continue

    #             self.axes[3].axvline(idx, color=color, alpha=0.1)
    #         # 정책 신경망의 출력 그리기
    #         if len(outvals_policy) > 0:
    #             for action, color in zip(action_list, self.COLORS):
    #                 self.axes[3].plot(
    #                     x, outvals_policy[:, action],
    #                     color=color, linestyle='-')

    #         # 차트 5. 포트폴리오 가치
    #         self.axes[4].axhline(
    #             initial_balance, linestyle='-', color='gray')
    #         self.axes[4].fill_between(x, pvs, pvs_base,
    #             where=pvs > pvs_base, facecolor='r', alpha=0.1)
    #         self.axes[4].fill_between(x, pvs, pvs_base,
    #             where=pvs < pvs_base, facecolor='b', alpha=0.1)
    #         self.axes[4].plot(x, pvs, '-k')
    #         # 학습 위치 표시
    #         for learning_idx in learning_idxes:
    #             self.axes[4].axvline(learning_idx, color='y')

    #         # 에포크 및 탐험 비율
    #         self.fig.suptitle('{} \nEpoch:{}/{} e={:.2f}'.format(
    #             self.title, epoch_str, num_epoches, epsilon))
    #         # 캔버스 레이아웃 조정
    #         self.fig.tight_layout()
    #         self.fig.subplots_adjust(top=0.85)

    # def clear(self, xlim):
    #     with lock:
    #         _axes = self.axes.tolist()
    #         for ax in _axes[1:]:
    #             ax.cla()  # 그린 차트 지우기
    #             ax.relim()  # limit를 초기화
    #             ax.autoscale()  # 스케일 재설정
    #         # y축 레이블 재설정
    #         self.axes[1].set_ylabel('Agent')
    #         self.axes[2].set_ylabel('V')
    #         self.axes[3].set_ylabel('P')
    #         self.axes[4].set_ylabel('PV')
    #         for ax in _axes:
    #             ax.set_xlim(xlim)  # x축 limit 재설정
    #             ax.get_xaxis().get_major_formatter() \
    #                 .set_scientific(False)  # 과학적 표기 비활성화
    #             ax.get_yaxis().get_major_formatter() \
    #                 .set_scientific(False)  # 과학적 표기 비활성화
    #             # x축 간격을 일정하게 설정
    #             ax.ticklabel_format(useOffset=False)
