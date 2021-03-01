# import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


class DataHandler:

    def __init__(self, history_file, movingAverages):
        self.movingAverages = movingAverages
        self.convert_history(history_file)
        # self.calculate_log_Closes()
        # self.logReg_curveFit(logReg_accuracy)
        self.movingAverages_get(movingAverages)
        self.calculate_quotients([[movingAverages[0], movingAverages[1]]])
        # self.calculate_logarithmQuotients([self.MA_1, self.MA_2])
        # self.calculate_log_priceDivByMA(movingAverages[2])

    # def predictor_log(self, x, a, b, c, d):
    #     return a+b*np.log10(x-c)/np.log10(d)
    #
    def predictor_log(self, x, a, b, c):
        return a+b*np.log10(x-c)
        # return a+b*np.log(x-c)

    def predictor_lin(self, x, k, n):
        return k*x+n

    def predictor_exp(self, x, a, b, c):
        return a*np.exp(x-b)+c

    def convert_history(self, file_csv_dir):
        history = pd.read_csv(file_csv_dir, comment='#')
        # df['index'] = df.index
        # df.set_index('Date', inplace=True)
        history['day'] = history.Timestamp
        # history['day_sinceD1'] = (pd.Timestamp(history.day)-pd.Timestamp(history.day.iloc[0,:])).days
        history['close'] = history.Close
        history['close_log'] = np.log10(history.close)
        self.history = history[['day', 'close', 'close_log']]

    def movingAverages_get(self, movingAverages):
        for days_n in movingAverages:
            self.history['MA_{}'.format(days_n)] = self.history.close.astype(float).rolling(window=days_n).mean()
            # self.data['MA_{}'.format(days)] = self.data.iloc[0].rolling(window=days).mean()

    def calculate_quotients(self, quotient_pairs, plusLog=True):
        for pair in quotient_pairs:
            # pair = pair.split('_')
            MA_0 = pair[0]
            MA_1 = pair[1]
            quotient = np.divide(self.history['MA_{}'.format(MA_0)], self.history['MA_{}'.format(MA_1)])
            self.history['quotient_{}_{}'.format(MA_0, MA_1)] = quotient
            # day_max = quotient.idxmax()
            # self.data['quotient_{}_{}'.format(MA_0, MA_1)] = np.divide(quotient, quotient[day_max])
            # print('max quotient {}, dne {}'.format(quotient[day_max], day_max))
            if plusLog:
                self.history['quotient_{}_{}_log'.format(MA_0, MA_1)] = np.log10(quotient)

    def cowen_relInd_1(self, plot=False):
        # indicator = (self.history.close_log-self.history.LR_bottom)/abs(self.history.LR_bottom)
        indicator = (self.history.close-np.power(10, self.history.LR_bottom))/np.power(10, self.history.LR_bottom)
        self.history['indicator_1'] = np.log10(abs(indicator))
        if plot:
            self.plot_log(['indicator_1'])

    def normalize_vector(self, vector):
        if np.abs(vector.min()) > np.abs(vector.max()):
            normalizator = np.abs(vector.min())
        else:
            normalizator = np.abs(vector.max())
        return np.divide(vector, normalizator)

    def getRisk_00(self, plot=False):
        risk = self.history['quotient_{}_{}'.format(self.movingAverages[0], self.movingAverages[1])]
        risk = np.multiply(risk, self.history.indicator_1)
        self.history['risk00'] = risk
        if plot:
            self.plot_log(right_yAxis=True, right_columns=['risk00'])
        # risk_proto = self.normalize_vector(self.history['quotient_{}_{}'.format(MA_1, MA_2)])
        # risk_proto = np.multiply(risk_proto, self.history['logarithm_priceByMA_{}'.format(MA_3)])
        # # self.history['risk_6'] = (risk_proto + 1)/2
        # self.history['risk_00'] = risk_proto

    def LR_basic(self, accuracy=0.001, approx4cowen=False, plot=False):
        theFit, something = curve_fit(self.predictor_log, self.history.index, self.history.close_log, bounds=(-np.inf, [np.inf, np.inf, 0]))
        a, b, c = theFit
        a_bu, b_bu, c_bu = a, b, c
        LR_first = np.multiply(np.log10(self.history.index-c), b) + a
        norm = 1
        LR_last = LR_first
        while norm > accuracy:
            history_new = self.history.loc[self.history['close_log'] < LR_last]
            theFit, something = curve_fit(self.predictor_log, history_new.index, history_new.close_log, p0=[a, b, c], bounds=(-np.inf, [np.inf, np.inf, 0]))
            a, b, c = theFit
            LR_new = np.multiply(np.log10(self.history.index-c), b) + a
            norm = abs((LR_new - LR_last)).max()
            # print('NORM (bottom): {}'.format(norm))
            LR_last = LR_new
        self.history['LR_bottom'] = LR_last
        norm = 1
        LR_last = LR_first
        a, b, c = a_bu, b_bu, c_bu
        while norm > accuracy:
            history_new = self.history.loc[self.history['close_log'] > LR_last]
            theFit, something = curve_fit(self.predictor_log, history_new.index, history_new.close_log, p0=[a, b, c], bounds=(-np.inf, [np.inf, np.inf, 0]))
            a, b, c = theFit
            LR_new = np.multiply(np.log10(self.history.index-c), b) + a
            norm = abs((LR_new - LR_last)).max()
            # print('NORM (top): {}'.format(norm))
            LR_last = LR_new
        self.history['LR_top'] = LR_last
        if approx4cowen:
            x = 1./5.1
            y = 1-x
            self.history['LR_cowen'] = x*self.history['LR_top']+y*self.history['LR_bottom']
        if plot:
            self.plot_log(['close_log', 'LR_bottom', 'LR_top'])

    def LR_lowHigh(self, accuracy=0.001, plot=False):
        theFit, something = curve_fit(self.predictor_log, self.history.index, self.history.close_log, bounds=(-np.inf, [np.inf, np.inf, 0]))
        a, b, c = theFit
        a_bu, b_bu, c_bu = a, b, c
        LR_first = np.multiply(np.log10(self.history.index-c), b) + a
        norm = 1
        LR_last = LR_first
        # y_toFit = np.log10(self.history.low)
        while norm > accuracy:
            # y_toFit = y_toFit.loc[y_toFit['low'] < LR_last]
            history_new = self.history.loc[self.history['close_log'] < LR_last]
            theFit, something = curve_fit(self.predictor_log, history_new.index, history_new.close_log, p0=[a, b, c], bounds=(-np.inf, [np.inf, np.inf, 0]))
            a, b, c = theFit
            LR_new = np.multiply(np.log10(self.history.index-c), b) + a
            norm = abs((LR_new - LR_last)).max()
            # print('NORM (bottom): {}'.format(norm))
            LR_last = LR_new
        self.history['LR_bottom'] = LR_last
        norm = 1
        LR_last = LR_first
        a, b, c = a_bu, b_bu, c_bu
        while norm > accuracy:
            history_new = self.history.loc[self.history['close_log'] > LR_last]
            theFit, something = curve_fit(self.predictor_log, history_new.index, history_new.close_log, p0=[a, b, c], bounds=(-np.inf, [np.inf, np.inf, 0]))
            a, b, c = theFit
            LR_new = np.multiply(np.log10(self.history.index-c), b) + a
            norm = abs((LR_new - LR_last)).max()
            # print('NORM (top): {}'.format(norm))
            LR_last = LR_new
        self.history['LR_top'] = LR_last
        if plot:
            self.plot_log(['close_log', 'LR_bottom', 'LR_top'])

    def LR_cowen(self, nonBubble_fit=True, plot=False):
        if nonBubble_fit:
            history = self.history
            history['index_bu'] = history.index
            history.day = pd.to_datetime(history.day)
            history = history.set_index(['day'], inplace=False)
            history = history.sort_index()
            h1 = history.loc['2010-07-25':'2010-10-07']  # aug-sep start is 2010-07-18
            h2 = history.loc['2010-12-05':'2011-04-22']  # nov
            # h3 = history.loc['2011-03-01':'2011-04-01']  # mar
            # h4 = history.loc['2011-08-01':'2011-12-01']  # aug-nov
            h4 = history.loc['2011-11-18':'2011-12-19']  # aug-nov
            # h5 = history.loc['2012-02-01':'2013-04-01']  # feb_12-mar_13
            h5 = history.loc['2012-02-19':'2013-02-13']  # feb_12-mar_13
            # h6 = history.loc['2015-01-14':'2017-06-01']  # jan_15-may_17
            h6 = history.loc['2015-01-14':'2017-06-01']  # jan_15-may_17
            # h7 = history.loc['2018-07-01':'2019-05-01']  # jul_18-apr_19
            h7 = history.loc['2018-12-15':'2019-05-01']  # jul_18-apr_19
            # h8 = history.loc['2019-08-01':'2020-10-01']  # aug_19-sep_20
            # h8 = history.loc['2019-12-17':'2019-02-13']  # korona
            h8 = history.loc['2020-03-12':'2020-11-05']
            history = pd.concat([h1, h2, h4, h5, h6, h7, h8])
            # history = pd.concat([h5, h6, h7, h8])
            theFit, something = curve_fit(self.predictor_log, history.index_bu, history.close_log, bounds=(-np.inf, [np.inf, np.inf, 0]))
            a, b, c = theFit
            LR_last = np.multiply(np.log10(self.history.index-c), b) + a
            del self.history['index_bu']
        else:
            LR_last = self.history['close_log']+1
            for i in range(2):
                history_new = self.history.loc[self.history['close_log'] < LR_last]
                theFit, something = curve_fit(self.predictor_log, history_new.index, history_new.close_log, bounds=(-np.inf, [np.inf, np.inf, 0]))
                a, b, c = theFit
                LR_last = np.multiply(np.log10(self.history.index-c), b) + a
        self.history['LR_cowen'] = LR_last
        if plot:
            self.plot_log(['close_log', 'LR_cowen'])

    def normalizeByDescendingFit(self, column):
        pass

    def plot_log(self, data_columns=['close_log'], right_yAxis=False, right_columns=['risk00']):
        months = pd.to_datetime(self.history.day, format='%Y-%m-%d %H:%M:%S.%f')
        history_toPlot = self.history.set_index(months, inplace=False)
        for column in data_columns:
            history_toPlot[column].plot()
        if right_yAxis:
            for column in right_columns:
                history_toPlot[column].plot(secondary_y=True, x_compat=True)
        plt.legend(loc='best')
        plt.show()


if __name__ == '__main__':
    dataHandler = DataHandler('usd_btc.csv', [50, 350])
    dataHandler.LR_basic()  # approx4cowen=True)
    # dataHandler.LR_cowen()  # nonBubble_fit=True)  # , plot=True)
    print(dataHandler.history)
    dataHandler.cowen_relInd_1()  # plot=True)
    dataHandler.getRisk_00(plot=True)
