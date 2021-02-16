# import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


class DataHandler:

    def __init__(self, history_file, MA_1=50, MA_2=350, MA_3=700):
        self.MA_1 = MA_1
        self.MA_2 = MA_2
        self.MA_3 = MA_3
        self.convert_history(history_file)
        # self.calculate_logReg()
        # self.cowen_logReg()
        self.calculate_log_Closes()
        # self.so_logReg()
        # self.nonBubble_logReg()
        self.nonBubble_logReg_curveFit()
        self.calculate_movingAverages(self.MA_1, self.MA_2, self.MA_3)
        self.calculate_quotients([self.MA_1, self.MA_2])
        # self.calculate_logarithmQuotients([self.MA_1, self.MA_2])
        self.calculate_log_priceDivByMA(self.MA_3)
        # self.calculate_priceMinusMA(self.MA_3)
        # self.calculate_logReg()

    def convert_history(self, file_csv_dir):
        df = pd.read_csv(file_csv_dir)
        df['index'] = df.index
        df.set_index('Date', inplace=True)
        df['log_Close'] = np.log10(df.Close)
        self.data = df[['Close', 'log_Close', 'Volume', 'index']]

    def calculate_movingAverages(self, *n_Days):
        for days in n_Days:
            self.data['MA_{}'.format(days)] = self.data.iloc[:, 0].rolling(window=days).mean()
            # self.data['MA_{}'.format(days)] = self.data.iloc[0].rolling(window=days).mean()

    def calculate_quotients(self, *quotient_pairs):
        for pair in quotient_pairs:
            # pair = pair.split('_')
            MA_0 = pair[0]
            MA_1 = pair[1]
            quotient = np.divide(self.data['MA_{}'.format(MA_0)], self.data['MA_{}'.format(MA_1)])
            self.data['quotient_{}_{}'.format(MA_0, MA_1)] = quotient
            # day_max = quotient.idxmax()
            # self.data['quotient_{}_{}'.format(MA_0, MA_1)] = np.divide(quotient, quotient[day_max])
        # print('max quotient {}, dne {}'.format(quotient[day_max], day_max))

    def calculate_logarithmQuotients(self, *quotient_pairs):
        for pair in quotient_pairs:
            # pair = pair.split('_')
            MA_0 = pair[0]
            MA_1 = pair[1]
            quotient = np.log10(np.divide(self.data['MA_{}'.format(MA_0)], self.data['MA_{}'.format(MA_1)]))
            self.data['logarithmQuotient_{}_{}'.format(MA_0, MA_1)] = quotient

    def calculate_log_priceDivByMA(self, moving_average):
        self.data['logarithm_priceByMA_{}'.format(moving_average)] = np.log(np.divide(self.data.Close, self.data['MA_{}'.format(moving_average)]))

    def normalize_vector(self, vector):
        if np.abs(vector.min()) > np.abs(vector.max()):
            normalizator = np.abs(vector.min())
        else:
            normalizator = np.abs(vector.max())
        return np.divide(vector, normalizator)

    def getRisk_1(self):
        risk = np.multiply(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)], self.data['differenceFrom_{}'.format(self.MA_3)])
        if np.abs(risk.min()) > np.abs(risk.max()):
            normalizator = np.abs(risk.min())
        else:
            normalizator = np.abs(risk.max())
        risk = np.divide(risk, normalizator)
        self.data['risk_1'] = (risk + 1)/2

    def getRisk_7(self):
        risk_proto = self.normalize_vector(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)])
        risk_proto = np.multiply(risk_proto, self.data['logarithm_priceByMA_{}'.format(self.MA_3)])
        # self.data['risk_6'] = (risk_proto + 1)/2
        self.data['risk_7'] = risk_proto

    def getRisk_8(self):
        risk_proto = self.normalize_vector(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)])
        risk_proto = np.multiply(risk_proto, self.data['logarithm_priceByMA_{}'.format(self.MA_3)])
        # self.data['risk_6'] = (risk_proto + 1)/2
        self.data['risk_7'] = risk_proto

    def calculate_logReg(self, auto=False):
        # f(x) = a + b*log(x)
        if auto:
            date_bottom = self.data.Close.idmin()
            a = self.data.Close[date_bottom]
        logReg = self.data['index'] + 1
        # logReg = log10(logReg
        a = 19  # usd approx. on 2013-04-28
        b = (10958-19)/np.log10(2802)  # on 2020-12-29
        self.data['logReg'] = a+np.multiply(np.log10(logReg), b)

    def cowen_logReg(self):
        # approx. 0.1 usd in 11-2010 => a = log10(0.1)
        # days from 11-2010 to 2013-04-28 are approx 2y2m = 790days
        # b = (log10(10958)-log10(0.1))/log10(2802+790)
        # f(x) = a + b*log(x)
        logReg = self.data['index'] + 1 + 790
        # logReg = log10(logReg
        a = np.log10(0.1)  # usd approx. on 2010-10
        b = (np.log10(10958)-np.log10(0.1))/np.log10(2802+790)  # on 2020-12-29
        self.data['cowen_logReg'] = a+np.multiply(np.log10(logReg), b)

    def so_logReg(self):
        # https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
        logReg_x = self.data['index'] + 1
        # theFit = np.polyfit(np.log10(logReg), np.log10(self.
        theFit = np.polyfit(np.log10(logReg_x), self.data.log_Close, 1)
        a = theFit[1]
        b = theFit[0]
        self.data['so_logReg'] = a+np.multiply(np.log10(logReg_x), b)

    def nonBubble_logReg(self):
        # https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
        logReg_x = self.data['index'] + 1
        nonBubble_1 = self.data.loc['2015-09-01':'2017-02-01']
        nonBubble_2 = self.data.loc['2018-12-01':'2019-02-01']
        nonBubble = pd.concat([nonBubble_1, nonBubble_2])
        # convert to datetime:
        nonBubble.index = pd.to_datetime(nonBubble.index)

        nonBubble.loc[pd.to_datetime('2010-11-01')] = [0, 0, 0, -1]
        nonBubble = nonBubble.sort_index()
        # nonBubble = nonBubble['log_Close']
        # toFit_x = nonBubble['index'] + 1 + 790
        toFit_x = nonBubble['index'] + 1 + 790
        # toFit_x.set_value(
        # toFit_x.iloc[0]['index'] = [1]
        toFit_x[0] = 1
        # toFit_x = pd.concat([pd.Series([1]), toFit_x])
        # theFit = np.polyfit(np.log10(logReg), np.log10(self.
        theFit = np.polyfit(np.log10(toFit_x), nonBubble.log_Close, 1)
        a = theFit[1]
        b = theFit[0]
        self.data['nonBubble_logReg'] = a+np.multiply(np.log10(logReg_x), b)

    def nonBubble_logReg_curveFit(self):
        def predictor(x, a, b, c):
            return a+b*np.log10(x-c)

        toPlot_x = self.data['index'] + 1
        nonBubble_1 = self.data.loc['2015-09-01':'2017-02-01']
        nonBubble_2 = self.data.loc['2018-12-01':'2019-02-01']
        nonBubble = pd.concat([nonBubble_1, nonBubble_2])
        # convert to datetime:
        nonBubble.index = pd.to_datetime(nonBubble.index)

        nonBubble.loc[pd.to_datetime('2010-11-01')] = [0, 0, 0, -1]
        # nonBubble.loc[pd.to_datetime('2010-11-01')] = [0, 0, 0, 0.1]
        nonBubble = nonBubble.sort_index()
        # nonBubble = nonBubble['log_Close']
        toFit_x = nonBubble['index'] + 1 + 790
        toFit_x[0] = 1
        theFit, something = curve_fit(predictor, toFit_x, nonBubble.log_Close, p0=[0.1, 1, -0.1], bounds=(-np.inf, [np.inf, np.inf, 0]))
        # theFit, something = curve_fit(predictor, toFit_x, nonBubble.log_Close, bounds=([-70, -20, -4000], [70, 20, 0]))
        a, b, c = theFit
        self.data['nonBubble_logReg'] = np.multiply(np.log10(toPlot_x-c+791), b) + a

    def plot_all(self, right_yAxis=None, *data_columns):
        data_columns = [x for x in data_columns]
        self.data.plot(y=data_columns, x_compat=True)
        if right_yAxis:
            self.data.risk_7.plot(secondary_y=True, x_compat=True)
        plt.legend(loc='best')
        plt.show()

    def plot_log(self, right_yAxis=None, *data_columns):
        data_columns = [x for x in data_columns]
        # self.data.plot(y=data_columns, logy=True, x_compat=True).set_ylim(1.8)
        self.data.plot(y=data_columns, x_compat=True).set_ylim(1.8)
        if right_yAxis:
            self.data.risk_7.plot(secondary_y=True, x_compat=True)
        plt.legend(loc='best')
        plt.show()


if __name__ == '__main__':
    dataHandler = DataHandler('dbBtcUsd_since2013.csv', 50, 350)
    # dataHandler = DataHandler('BTC_USD_recent.csv', 50, 350, 140)
    print(dataHandler.data)
    dataHandler.getRisk_7()
    # dataHandler.plot_all(False, 'Close', 'MA_50', 'MA_350')
    dataHandler.plot_log(False, 'log_Close', 'nonBubble_logReg')

    # with open('variables.json', 'r') as constants:
    #     data = json.load(constants)
    # high_1 = data['max_quotient_1']['quotient']
    # high_2 = data['max_quotient_2']['quotient']
    # self.data['quotient_normalized'] = quotient / (high_1*0.45 + high_2*0.55)

    # def calculate_priceMinusMA(self, moving_average):
    #     self.data['differenceFrom_{}'.format(moving_average)] = self.data.Close - self.data['MA_{}'.format(moving_average)]
    #     # self.data['differenceFrom_{}'.format(moving_average)].idxmin()
    #     # self.data['differenceFrom_{}'.format(moving_average)].idxmax()

    # def getRisk_2(self):
    #     normalQuotient = self.normalize_vector(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)])
    #     normalDifference = self.normalize_vector(self.data['differenceFrom_{}'.format(self.MA_3)])
    #     # risk = np.multiply(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)], self.data['differenceFrom_{}'.format(self.MA_3)])
    #     # if np.abs(risk.min()) > np.abs(risk.max()):
    #     #     normalizator = np.abs(risk.min())
    #     # else:
    #     #     normalizator = np.abs(risk.max())
    #     # risk = np.divide(risk, normalizator)
    #     self.data['risk_2'] = (np.multiply(normalQuotient, normalDifference) + 1)/2

    # def getRisk_3(self):
    #     normalQuotient = self.normalize_vector(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)])
    #     normalDifference = self.normalize_vector(self.data['differenceFrom_{}'.format(self.MA_3)])
    #     # risk = np.multiply(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)], self.data['differenceFrom_{}'.format(self.MA_3)])
    #     # if np.abs(risk.min()) > np.abs(risk.max()):
    #     #     normalizator = np.abs(risk.min())
    #     # else:
    #     #     normalizator = np.abs(risk.max())
    #     # risk = np.divide(risk, normalizator)
    #     self.data['risk_3'] = (np.multiply(normalQuotient, normalDifference) + 1)/2

    # def getRisk_4(self):
    #     normalQuotient = self.normalize_vector(self.data['quotient_{}_{}'.format(self.MA_1, self.MA_2)])
    #     normalLogarithm = self.normalize_vector(self.data['logarithm_priceByMA_{}'.format(self.MA_3)])
    #     self.data['risk_4'] = (np.multiply(normalQuotient, normalLogarithm) + 1)/2

    # def getRisk_5(self):
    #     normalLogQuotient = self.normalize_vector(self.data['logarithmQuotient_{}_{}'.format(self.MA_1, self.MA_2)])
    #     normalLogarithm = self.normalize_vector(self.data['logarithm_priceByMA_{}'.format(self.MA_3)])
    #     self.data['risk_5'] = (np.multiply(normalLogQuotient, normalLogarithm) + 1)/2

    # def getRisk_6(self):
    #     risk_proto = self.normalize_vector(np.multiply(self.data['logarithmQuotient_{}_{}'.format(self.MA_1, self.MA_2)],
    #                                                    self.data['logarithm_priceByMA_{}'.format(self.MA_3)]))
    #     # self.data['risk_6'] = (risk_proto + 1)/2
    #     self.data['risk_6'] = risk_proto
