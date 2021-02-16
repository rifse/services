import time
import pandas as pd
from os import getcwd

PATH = getcwd().split('/')
PATH = f'/{PATH[1]}/{PATH[2]}/localRepo' if 'topkomp' in PATH else f'/{PATH[1]}/{PATH[2]}'

def print_data(tickers_bool, resolution):
    if tickers_bool:
        with open(f'{PATH}/privat_hetzner/tickers.csv', 'r') as tickers_file:
            tickers_pd = pd.read_csv(tickers_file)
        # print(chr(27) + "[2J")
        print("\033c")
        print(tickers_pd)
    time.sleep(resolution)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', default=True, type=bool)
    parser.add_argument('--resolution', default=1, type=int)
    args = parser.parse_args()

    while True:
        print_data(args.tickers, args.resolution)
