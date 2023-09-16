
"""
investing.py

Script to download and process investing.com data


Usage:
    - how to update all data  (takes 45 minutes)
        update_investing(method='update-all')
    
    - how to update a country data  (takes less than 10 minutes)
        update_investing(method='update-country', country='USD')
        X, y = get_investing(country='USD', timeframe='1w')
    
    - how to update a single series (takes less than 1 minutes)
        update_investing(method=None, name='US Dollar Index')  
        dxy =pd.read_csv("investing_data/US Dollar Index.csv")
        dxy = clean_investing_data(dxy, timeframe)
"""



## Import Libraries
import os
import io
from time import sleep
import shutil

from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.service import Service 
from selenium import webdriver 
import pandas as pd 
import numpy as np

import logging 
import warnings
warnings.filterwarnings('ignore')



# Configure logger
logger = logging.getLogger(__name__)


# Helper functions

def make_folder(path):
    """Create folder if it doesn't exist"""
    if not os.path.exists(path):
        os.mkdir(path)

def delete_folder(path):
    """Delete folder"""
    try:
        shutil.rmtree(path) 
    except OSError as e:
        print(f"Error: {e}")


def driver_config(output: str= "", page_load_strategy: str= "normal"):
    """
    Configure Chrome driver with settings:
    - Disable automation flags
    - Set download directory
    - Headless mode
    - Other preferences like disabling popups
    """
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=cat')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.page_load_strategy = 'eager' 
    options.add_argument("user-agent=whatever you want")
    options.add_argument(f"download.default_directory={output}") 
    options.add_argument('--headless')
    
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": output,
             "directory_upgrade": True}

    options.add_experimental_option("prefs",prefs)
    
    
    s=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options,)
    driver.maximize_window()

    return driver

def extract_investing_data(driver, url):
    """
    Extract investing.com data:
    - Load page
    - Save HTML to file
    - Read tables from HTML into pandas DataFrame
    - Return DataFrame
    """
    
    make_folder('html')
    driver.get(url)
    sleep(1)

    with io.open("html/temp.html", "w",encoding='utf-8') as f:
            f.write(driver.page_source)
    
    driver.quit()
    
    for i in range(4):
        df = pd.read_html('html/temp.html')[i]
        if 'Price' in df.columns: break
        
    delete_folder('html')
    
    return df



def update_data(file: str) -> None:
    """
    Update a single Investing.com data file:
    - Load existing CSV data
    - Extract new data
    - Concat old and new data
    - Save updated CSV
    """

    try:
      
      # Load existing data
      df1 = pd.read_csv(f"investing_data/{file}.csv") 
    
      # Get new data    
      df2 = extract_investing_data(driver_config(), urls[file])
      
      # Concat old and new data
      df = pd.concat([df1, df2])
      
      # Save updated CSV
      df.to_csv(f"investing_data/{file}.csv")
      
      print(f"{file} data updated successfully")
          
    except Exception as e:
      logger.error(f"{file} data failed to update: {str(e)}")

def get_features():
    features=dict()
    
    features['USD']=['USD_bond_2Y', 'USD_bond_5Y', 'USD_bond_10Y',
                     'EURUSD', 'NZDUSD', 'GBPUSD', 'USDCHF', 
                     'NASDAQ','VIX','T-Note','US 30 Cash',
                     'Silver', 'Gold', 'Copper', 'CRB']
    
    
    features['CAD']=['CAD_bond_7Y', 'CAD_bond_5Y', 'CAD_bond_4Y', 'CAD_bond_3Y', 'CAD_bond_2Y', 'CAD_bond_10Y', 
                     'CADCHF', 'GBPCAD', 'CADJPY','EURCAD', 'VIX','T-Note', 'US Wheat', 'Heating Oil', 'CRB']
    
    features['AUD']=['AUD_bond_10Y', 'AUD_bond_4Y',
                     'AUDCHF', 'AUDJPY', 'AUDCAD', 'VIX','NASDAQ', 'USD_bond_10Y', 'Lumber','Brent Oil','Copper', 'CRB']
    
    
    features['NZD']=['NZD_bond_6M', 'VIX','NASDAQ' , 'Silver', 'Brent Oil','Copper',
                     'EURNZD', 'NZDUSD', 'GBPNZD']
    
    
    features['JPY']=['JPY_bond_8Y','JPY_bond_10Y','JPY_bond_30Y',
                     'EURJPY', 'GBPJPY', 'CADJPY', 'VIX','NASDAQ', 'Heating Oil', 'US Dollar Index']
    
    
    
    features['GBP']=['GBP_bond_3Y','GBP_bond_1M','GBP_bond_6M',
                     'GBPUSD', 'GBPJPY', 'GBPCHF','EURGBP', 'Heating Oil']
    
    
    features['EUR']=['Germany 10-Year_Bond','Germany 5-Year_Bond','France 10-Year_Bond','US Dollar Index',
                     'EURGBP', 'EURUSD', 'EURJPY','EURCAD', 'NASDAQ', 'Brent Oil', 'Silver', 'CRB', 'Natural Gas']
    
    return features

def get_country_index(country, timeframe='1d'):
    
    dxy =pd.read_csv("investing_data/US Dollar Index.csv")
    dxy = clean_investing_data(dxy, timeframe)
    if country == 'USD':
        country_index =dxy

    else:
        if country in ['CAD', 'JPY', 'SEK', 'CHF']:
            Ticker = 'USD' + country
            df = pd.read_csv(f"investing_data/{Ticker}.csv")
            df = clean_investing_data(df, timeframe)
            df=df[['Open', 'High', 'Low', 'Close']]
            country_index = dxy/df
        else:
            Ticker = country + 'USD'
            df = pd.read_csv(f"investing_data/{Ticker}.csv")
            df = clean_investing_data(df, timeframe)
            df=df[['Open', 'High', 'Low', 'Close']]
            country_index = df*dxy
            
        country_index['Mean']=np.mean(pd.concat((country_index['Low'],country_index['High'], country_index['Close']),axis=1),axis=1)
        country_index['diff']=country_index['Mean']-country_index['Mean'].shift(1)
    
    return country_index.dropna()

# Main functions

def update_investing(method, name=None, country=None):
    """
    Wrapper function to call update_data for:
    - All files
    - Single file
    - All files for a country
    """
    
    if method=='update-all':
        for file in list(urls.keys()):
            update_data(file)
            
    elif method=='update-country':
        # Parse country code
        country1, country2 = country[:3], country[3:]
        
        # Handle special case of USD
        if country1=='USD': 
            country1='US Dollar Index'
            
        if country2=='USD':
            country2='US Dollar Index'
            
        # Update country level data    
        update_data(country1)
        update_data(country2)
        
        # Update all features for this country
        features=get_features()
        
        for file in features[country]:
            update_data(file)
            
    else:
        # Update single file
        update_data(name)
        

        
def clean_investing_data(df, timeframe='1d'):
    
    # Set index to date
    df.index = pd.to_datetime(df["Date"])
    
    # Sort DataFrame by index
    df.sort_index(axis=0, ascending=True, inplace=True)
    
    # Rename 'Price' column to 'Close' for consistency
    df['Close'] = df['Price']
    
    # Drop unnecessary columns
    try:
        df = df.drop(columns=["Date", "Change %", "Vol.", "Price"])
    except:
        df = df.drop(columns=["Date", "Change %", "Price"])
    
    try: 
        df = df.drop(columns=['Unnamed: 0'])
    except: 
        pass
        
    
    # Clean data by removing commas and converting to float
    for column in df.columns:
        for k in range(len(df[column])):
            if type(df[column][k]) == str:
                df[column][k] = df[column][k].replace(",","")
        df[column] = df[column].astype(float)   
    
    #Change to 1w timeframe
    if timeframe=='1w':
        df=df.resample('W-MON', convention='end', kind='period').agg({'Open':'first', 'High':'max', 
                                              'Low':'min', 'Close':'last'})
    df['Mean'] = np.mean(pd.concat((df['Low'], df['High'], df['Close']), axis=1), axis=1)
    df['diff'] = df['Mean'] - df['Mean'].shift(1)
    df = df.loc[~df.index.duplicated()]
    
    return df[['Open', 'Low', 'High', 'Close', 'Mean', 'diff']].dropna()



def get_investing(country, timeframe='1d'):
    
    X=[]

    features=get_features()[country]
    
    for feature in features:
        df =pd.read_csv(f"investing_data/{feature}.csv")
        df = clean_investing_data(df, timeframe)
        X.append(df)
    
    y=get_country_index(country, timeframe)
    
    return X, y
    

# Config    

urls={
"AUD_bond_4Y": 'https://www.investing.com/rates-bonds/australia-4-year-bond-yield-historical-data',
"AUD_bond_10Y":  'https://www.investing.com/rates-bonds/australia-10-year-bond-yield-historical-data',
"AUDCAD": 'https://www.investing.com/currencies/aud-cad-historical-data',
"AUDCHF": 'https://www.investing.com/currencies/aud-chf-historical-data',
"AUDJPY": 'https://www.investing.com/currencies/aud-jpy-historical-data',
"AUDUSD": 'https://www.investing.com/currencies/aud-usd-historical-data',
"Brent Oil": 'https://www.investing.com/commodities/brent-oil-historical-data',
"CAD_bond_2Y": 'https://www.investing.com/rates-bonds/canada-2-year-bond-yield-historical-data',
"CAD_bond_3Y":'https://www.investing.com/rates-bonds/canada-3-year-bond-yield-historical-data',
"CAD_bond_4Y":'https://www.investing.com/rates-bonds/canada-4-year-bond-yield-historical-data',
"CAD_bond_5Y":'https://www.investing.com/rates-bonds/canada-5-year-bond-yield-historical-data',
"CAD_bond_7Y":'https://www.investing.com/rates-bonds/canada-7-year-bond-yield-historical-data',
"CAD_bond_10Y":'https://www.investing.com/rates-bonds/canada-10-year-bond-yield-historical-data',
"CADCHF":  'https://www.investing.com/currencies/cad-chf-historical-data',
"CADJPY": 'https://www.investing.com/currencies/cad-jpy-historical-data',
"CHFJPY": 'https://www.investing.com/currencies/chf-jpy-historical-data',
"Copper": 'https://www.investing.com/commodities/copper-historical-data',
"CRB": 'https://www.investing.com/indices/thomson-reuters---jefferies-crb-historical-data',
"EURAUD":'https://www.investing.com/currencies/eur-aud-historical-data',
"EURCAD":'https://www.investing.com/currencies/eur-cad-historical-data',
"EURGBP":'https://www.investing.com/currencies/eur-gbp-historical-data',
"EURJPY":'https://www.investing.com/currencies/eur-jpy-historical-data',
"EURUSD":'https://www.investing.com/currencies/eur-usd-historical-data',
"EURNZD":'https://www.investing.com/currencies/eur-nzd-historical-data',
"France 10-Year_Bond": 'https://www.investing.com/rates-bonds/france-10-year-bond-yield-historical-data',
"GBP_bond_1M": 'https://www.investing.com/rates-bonds/uk-1-year-month-yield-historical-data',
"GBP_bond_3Y":'https://www.investing.com/rates-bonds/uk-3-year-bond-yield-historical-data',
"GBP_bond_6M":'https://www.investing.com/rates-bonds/uk-6-year-month-yield-historical-data',
"GBPCHF":'https://www.investing.com/currencies/gbp-chf-historical-data',
"GBPJPY":'https://www.investing.com/currencies/gbp-jpy-historical-data',
"GBPUSD":'https://www.investing.com/currencies/gbp-usd-historical-data',
"GBPNZD":'https://www.investing.com/currencies/gbp-nzd-historical-data',
"GBPCAD":'https://www.investing.com/currencies/gbp-cad-historical-data',
"Germany 5-Year_Bond": 'https://www.investing.com/rates-bonds/germany-5-year-bond-yield-historical-data',
"Germany 10-Year_Bond": 'https://www.investing.com/rates-bonds/germany-10-year-bond-yield-historical-data',
"Gold": 'https://www.investing.com/commodities/gold-historical-data',
"Heating Oil": 'https://www.investing.com/commodities/heating-oil-historical-data',
"JPY_bond_8Y": 'https://www.investing.com/rates-bonds/japan-8-year-bond-yield-historical-data',
"JPY_bond_10Y": 'https://www.investing.com/rates-bonds/japan-10-year-bond-yield-historical-data',
"JPY_bond_30Y": 'https://www.investing.com/rates-bonds/japan-30-year-bond-yield-historical-data',
"Lumber": 'https://www.investing.com/commodities/lumber-historical-data',
"NZD_bond_6M": 'https://www.investing.com/rates-bonds/new-zealand-6-months-bond-yield-historical-data',
"NASDAQ": 'https://www.investing.com/indices/nasdaq-composite-historical-data',
"Natural Gas": 'https://www.investing.com/commodities/natural-gas-historical-data',
"NZDUSD": 'https://www.investing.com/currencies/nzd-usd-historical-data',
"Silver": 'https://www.investing.com/commodities/silver-historical-data',
"T-Note": 'https://www.investing.com/rates-bonds/us-10-yr-t-note-historical-data',
"US 30 Cash": 'https://www.investing.com/indices/us-30-futures-historical-data',
"US Dollar Index": 'https://www.investing.com/indices/usdollar-historical-data',
"US Wheat": 'https://www.investing.com/commodities/us-wheat-historical-data',
"USD_bond_2Y": 'https://www.investing.com/rates-bonds/u.s.-2-year-bond-yield-historical-data',
"USD_bond_5Y":'https://www.investing.com/rates-bonds/u.s.-5-year-bond-yield-historical-data',
"USD_bond_10Y":'https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield-historical-data',
"USDCAD": 'https://www.investing.com/currencies/usd-cad-historical-data',
"USDCHF":'https://www.investing.com/currencies/usd-chf-historical-data',
"USDJPY":'https://www.investing.com/currencies/usd-jpy-historical-data',
"VIX": 'https://www.investing.com/indices/volatility-s-p-500-historical-data',
}


