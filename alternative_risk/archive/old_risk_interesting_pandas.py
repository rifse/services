# import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class DataHandler:

    def __init__(self, history_file):
        self.convert_history(history_file)
        self.calculate_movingAverages(50, 350, 700)
        self.calculate_quotients([50, 350])
        self.calculate_priceMinusMA(700)
        # self.calculate_logReg()

    def convert_history(self, file_csv_dir):
        df = pd.read_csv(file_csv_dir)
        df.set_index('Date', inplace=True)
        self.data = df[['Close', 'Volume']]

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
            day_max = quotient.idxmax()
            self.data['quotient_{}_{}'.format(MA_0, MA_1)] = np.divide(quotient, quotient[day_max])
        # print('max quotient {}, dne {}'.format(quotient[day_max], day_max))

    def calculate_priceMinusMA(self, moving_average):
        self.data['differenceFrom_{}'.format(moving_average)] = self.data.Close - self.data['MA_{}'.format(moving_average)]
        # self.data['differenceFrom_{}'.format(moving_average)].idxmin()
        # self.data['differenceFrom_{}'.format(moving_average)].idxmax()

    def getRisk_1(self):
        risk = self.data

    def calculate_logReg(self, start=0):
        # f(x) = a + b*log(x)
        print(self.data.index)

    def plot_all(self, right_yAxis=None, *data_columns):
        data_columns = [x for x in data_columns]
        self.data.plot(y=data_columns, x_compat=True)
        if right_yAxis:
            self.data.quotient_normalized.plot(secondary_y=True, x_compat=True)
        plt.legend(loc='best')
        plt.show()


if __name__ == '__main__':
    dataHandler = DataHandler('BTC_USD_since2012.csv')
    print(dataHandler.data)
    dataHandler.plot_all(None, 'Close', 'MA_50', 'MA_350', 'MA_700')

    # with open('variables.json', 'r') as constants:
    #     data = json.load(constants)
    # high_1 = data['max_quotient_1']['quotient']
    # high_2 = data['max_quotient_2']['quotient']
    # self.data['quotient_normalized'] = quotient / (high_1*0.45 + high_2*0.55)
