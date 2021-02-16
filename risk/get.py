#!/home/admin/envs_py/services/bin/python3.8

"""Docstring."""

import json
import pandas as pd


def archive_risk(path, name, date, risk):
    try:
        risk.to_csv(f'{path}/archive_risks/{name}_upTo_{date}')
    except Exception as e:
        # logger.exception(e)
        print(e)
        from os import mkdir
        mkdir(f'{path}/archive_risks')
        risk.to_csv(f'{path}/archive_risks/{name}_upTo_{date}')


def print_csv(risk_dataFrame, filepath):
    risk_dataFrame.to_csv(filepath)


def read_written(filepath):
    return pd.read_csv(filepath, index_col=0)  # .dropna(axis=0, how='all').dropna(axis=1, how='all')


def read_variables(filepath):
    with open(filepath) as json_file:
        variables = json.load(json_file)
    return variables


def get_gSheet(key, gid):
    try:
        raw = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{key}/export?gid={gid}&format=csv')
    except Exception:
        return None
    else:
        return raw  # raw.iloc[:, 3:5].dropna(axis=0, how='all')


def crop_gSheet(gsheet, location):
    return gsheet.iloc[2:, location:(location+2)].dropna(axis=0, how='all')


def format_cropped(df):
    df.iloc[:, 0] = df.iloc[:, 0].str.replace('$', '').str.replace(',', '').astype(float)
    return df


def get_all(saveRaw=False):
    '''Reads the key and gids for google sheets from variables.json, then
    downloads, crops? and writes risks for all ASSETS into data/rawRisk_ASSET.'''

    VARS = read_variables('variables.json')
    key = VARS.pop('key')
    for ASSET in VARS:
        new = get_gSheet(key, VARS[ASSET]['gid'])
        print_csv(new, f'data/rawrisk_{ASSET}') if saveRaw else None
        if new is not None:
            if ASSET != 'btc':
                if ASSET != 'eth':
                    for risk in [(0, 'usd'), (6, 'btc'), (9, 'eth')]:
                        result = format_cropped(crop_gSheet(new, risk[0]))
                        print_csv(result, f'data/{ASSET}_{risk[1]}')
                else:  # ASSET == 'eth'
                    for risk in [(0, 'usd'), (6, 'btc')]:
                        result = format_cropped(crop_gSheet(new, risk[0]))
                        print_csv(result, f'data/eth_{risk[1]}')
            else:  # ASSET == 'btc'
                result = format_cropped(crop_gSheet(new, 0))
                print_csv(result, 'data/btc_usd')
        else:
            raise Exception('could not get csv from url')
#             if new is not None:
#                 try:
#                     diff = pd.concat([old, new]).drop_duplicates(keep=False)
#                 except Exception as e:
#                     print(e)
#                 else:
#                     if not diff.empty:
#                         # print_csv(new, f'data/rawRisk_{ASSET}')
#                         print_csv(new, f'rawRisk_{ASSET}')
#             else:
#                 raise Exception('could not get csv from url')

# date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

# print(read_variables('variables.json'))
# print(read_rawRisk('data/rawRisk_btc'))


if __name__ == '__main__':
    get_all()
