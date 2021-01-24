import threading
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import matplotlib.ticker as ticker

from mplfinance.original_flavor import candlestick2_ohlc

lock = threading.Lock()


class Visualizer:
    COLORS = ['r', 'b', 'g']

    def __init__(self, vnet=False):

        self.title = ''  # 그림 제목
        self.data = None

        # set grid 
        self.fig = plt.figure(figsize=(20, 10))
        self.top_axes = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
        self.bottom_axes = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4, sharex=self.top_axes)
        self.bottom_axes.get_yaxis().get_major_formatter().set_scientific(False)

    def plot_basic(self, data, name):

        self.title = name
        self.data = data


        index = data.index.astype('str') # 캔들스틱 x축이 str로 들어감

        # draw candle stick chart
        max_high = self.data['High'].max()
        min_low = self.data['Low'].min()

        self.top_axes.set_ylim([min_low, max_high])
        candlestick2_ohlc(self.top_axes, self.data['Open'], self.data['High'], self.data['Low'], self.data['Close'], width=0.5, colorup='r', colordown='b')
        
        # draw volume chart
        color_fuc = lambda x : 'r' if x >= 0 else 'b'
        color_list = list(self.data['Volume'].diff().fillna(0).apply(color_fuc))
        self.bottom_axes.bar(index, self.data['Volume'], width=0.5, 
                        align='center',
                        color=color_list)

        # title name
        self.top_axes.set_title(self.title, fontsize=22)
        self.bottom_axes.set_xlabel('Date', fontsize=15)
        #self.top_axes.xaxis.set_major_locator(ticker.FixedLocator(data.index))
        self.top_axes.xaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.tight_layout()
        #plt.xticks(rotation = 45)



    def add_moving_avg_line(self, num_MA):
        moving_avg = 'MA-'+ num_MA
        self.data[moving_avg] = self.data['Close'].rolling(int(num_MA)).mean()
        index = self.data.index.astype('str') # 캔들스틱 x축이 str로 들어감

        self.top_axes.plot(index, self.data[moving_avg], label=moving_avg, linewidth=0.7)
        self.top_axes.legend()

    def add_ref_line(self, ref_data):
        # draw candle stick chart
        max_high = self.data['High'].max()
        min_low = self.data['Low'].min()
        data_gap = max_high - min_low

        max_ref_high = ref_data['High'].max()
        min_ref_low = ref_data['Low'].min()
        data_ref_gap = max_ref_high - min_ref_low

        self.data['Reference'] = ref_data['Close']*(data_gap/data_ref_gap)
        index = self.data.index.astype('str') # 캔들스틱 x축이 str로 들어감

        self.top_axes.plot(index, self.data['Reference'], label='Reference', linewidth=0.7)
        self.top_axes.legend()

    def clear(self, xlim):
        with lock:
            _axes = self.axes.tolist()
            for ax in _axes[1:]:
                ax.cla()  # 그린 차트 지우기
                ax.relim()  # limit를 초기화
                ax.autoscale()  # 스케일 재설정
            # y축 레이블 재설정
            self.axes[1].set_ylabel('Agent')
            self.axes[2].set_ylabel('V')
            self.axes[3].set_ylabel('P')
            self.axes[4].set_ylabel('PV')
            for ax in _axes:
                ax.set_xlim(xlim)  # x축 limit 재설정
                ax.get_xaxis().get_major_formatter() \
                    .set_scientific(False)  # 과학적 표기 비활성화
                ax.get_yaxis().get_major_formatter() \
                    .set_scientific(False)  # 과학적 표기 비활성화
                # x축 간격을 일정하게 설정
                ax.ticklabel_format(useOffset=False)


    def save(self, path):
        with lock:
            self.fig.savefig(path)


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
