import datetime
import pandas as pd

from automate_fund_correlation import read_data, calculate_correlation, plot_correlation_heatmaps
from investing import clean_investing_data, update_investing

__NAME__TO__FILENANME__ = {
    'aud 4y bond': 'AUD_bond_4Y',
    'aud 10y bond': 'AUD_bond_10Y',
    'audcad': 'AUDCAD',
    'audchf': 'AUDCHF', 
    'audjpy': 'AUDJPY',
    'audusd': 'AUDUSD',
    'brent oil': 'Brent Oil',
    'cad 2y bond': 'CAD_bond_2Y',
    'cad 3y bond': 'CAD_bond_3Y',
    'cad 4y bond': 'CAD_bond_4Y',
    'cad 5y bond': 'CAD_bond_5Y',
    'cad 7y bond': 'CAD_bond_7Y',
    'cad 10y bond': 'CAD_bond_10Y',
    'cadchf': 'CADCHF',
    'cadjpy': 'CADJPY',
    'chfjpy': 'CHFJPY',
    'copper': 'Copper',
    'crb': 'CRB',
    'euraud': 'EURAUD',
    'eurcad': 'EURCAD',
    'eurgbp': 'EURGBP', 
    'eurjpy': 'EURJPY',
    'eurusd': 'EURUSD',
    'eurnzd': 'EURNZD',
    'france 10y bond': 'France 10-Year_Bond',
    'gbp 1m bond': 'GBP_bond_1M',
    'gbp 3y bond': 'GBP_bond_3Y',
    'gbp 6m bond': 'GBP_bond_6M', 
    'gbpchf': 'GBPCHF',
    'gbpjpy': 'GBPJPY',
    'gbpusd': 'GBPUSD',
    'gbpnzd': 'GBPNZD',
    'gbpcad': 'GBPCAD',
    'germany 5y bond': 'Germany 5-Year_Bond',
    'germany 1y bond': 'Germany 10-Year_Bond',
    'gold': 'Gold',
    'heating oil': 'Heating Oil',
    'jpy 8y bond': 'JPY_bond_8Y',
    'jpy 10y bond': 'JPY_bond_10Y',
    'jpy 30y bond': 'JPY_bond_30Y',
    'lumber': 'Lumber',
    'nzd 6m bond': 'NZD_bond_6M',
    'nasdaq': 'NASDAQ',
    'natural gas': 'Natural Gas',
    'nzdusd': 'NZDUSD',
    'silver': 'Silver',
    't-note': 'T-Note',
    'us 30 cash': 'US 30 Cash',
    'usd index': 'US Dollar Index',
    'us wheat': 'US Wheat',
    'usd 2y bond': 'USD_bond_2Y',
    'usd 5y bond': 'USD_bond_5Y',
    'usd 10y bond': 'USD_bond_10Y',
    'usdcad': 'USDCAD',
    'usdchf': 'USDCHF',
    'usdjpy': 'USDJPY', 
    'vix': 'VIX',
    }

if __name__ == "__main__":
    while True:
        choice = input("Do you want to update investing data? [y/n]: ").lower() or 'n'
        
        if choice[0] in ('y', 'n'):
            break
        else:
            print(f"{choice} is invalid. Please enter [y/n]")
            
    if choice[0] == 'y':
        update_investing(method="update-all")

    print(f"Here is the list of features:\n {list(__NAME__TO__FILENANME__.keys())}")

    while True:
        name1 = input("Please select the first feature? [<fx currency> <timeframe> <name>]: ").lower() or 'usd index'
        
        if name1 in list(__NAME__TO__FILENANME__.keys()):
            break
        else:
            print(f"{name1} is not in the list. Please select an available feature.")

    while True:
        name2 = input("Please select the second feature? [<fx currency> <timeframe> <name>]: ").lower() or 'us wheat'
        
        if name2 in list(__NAME__TO__FILENANME__.keys()):
            break
        else:
            print(f"{name2} is not in the list. Please select an available feature.")
    
    while True:
        column = input("Please column to compaire? [Open/High/Low/Close]: ").lower() or 'high'
        
        if column in ["open", "high", "low", "close"]:
            break
        else:
            print(f"{column} is not in the list. Please select from [open, high, low, close].")

    while True:
        start_date = input("Please select the start date of comparison? [YYYY-MM-DD]: ").lower() or '2010-01-01'
        
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            break
        except:
            print("Incorrect data format, should be YYYY-MM-DD")

    while True:
        end_date = input("Please select the end date of comparison? [YYYY-MM-DD]: ").lower() or '2020-01-01'
        
        try:
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            break
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    
    df1 = read_data(path="investing_data/", file_name=__NAME__TO__FILENANME__[name1], column_name_for_corr = column.capitalize())
    df1.dropna(inplace=True)
    df1.drop_duplicates(keep='first', inplace=True)
    df1 = df1[~df1.index.duplicated(keep='last')]
    
    df2 = read_data(path="investing_data/", file_name=__NAME__TO__FILENANME__[name2], column_name_for_corr = column.capitalize())
    df2.dropna(inplace=True)
    df2.drop_duplicates(keep='first', inplace=True)
    df2 = df2[~df2.index.duplicated(keep='last')]
    
    calculate_correlation(df1=df1, df2=df2, start_date=start_date, end_date=end_date)
    plot_correlation_heatmaps(df1=df1, df2=df2, start_date=start_date, end_date=end_date)
    