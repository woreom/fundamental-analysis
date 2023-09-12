import numpy as np
import pandas as pd
import os
import pickle

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd

import warnings
import sys
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    os.environ["PYTHONWARNINGS"] = "ignore"
    print("*** Be careful no warnings are printed ***")
    
    
def convert_str_to_float(df: pd.DataFrame) -> pd.DataFrame:
    '''
    The convert_str_to_float function takes a Pandas DataFrame as input and converts the string data types in each column to float.
    The function iterates through each column in the DataFrame, and for each column, it iterates through each row.
    If a particular cell in the DataFrame is of type string, the function removes any commas in the string to convert it to a numeric float value.
    Finally, the function converts the column to float using the astype method.
    The function modifies the input DataFrame in-place, and returns the modified DataFrame as output.
    Note that the function assumes that each string value in the DataFrame can be converted to a float after removing commas.
    If a value cannot be converted to a float, the function will raise an error.
    '''
    for column in df.columns:
        for k in range(len(df[column])):
            if type(df[column][k]) == str:
                df[column][k] = df[column][k].replace(",","")
        df[column] = df[column].astype(float)      

    return df 


def read_data(path:str, file_name:str, column_name_for_corr:str,) -> pd.DataFrame:
    '''
    Read and preprocess time-series data from a CSV file.

    Parameters:
        path (str): The directory path where the CSV file is located.
        file_name (str): The name of the CSV file (without the '.csv' extension) to read.
        column_name_for_corr (str): The name of the column for correlation analysis.

    Returns:
        pd.DataFrame: A Pandas DataFrame with two columns: "Date" and the specified column_name_for_corr.
                      The "Date" column is set as the DataFrame's index.

    Example Usage:
        # Define the path to the directory where the CSV files are located
        data_path = '/path/to/directory'

        # Read and preprocess data1.csv
        data1 = read_data(data_path, 'data1', 'Stock_Price')

        # Read and preprocess data2.csv
        data2 = read_data(data_path, 'data2', 'Sales')
    '''    
    columns_to_keep = ['Date']
    columns_to_keep.append(column_name_for_corr)
    df = pd.read_csv(path+'/'+file_name+'.csv')
    try:
        df.index = pd.to_datetime(df["Date"], format="%b %d, %Y")
    except:
        try:
            df.index = pd.to_datetime(df["Date"], format="%m/%d/%Y") 
        except:
            df.index = pd.to_datetime(df["Date"], format="%d/%m/%Y") 
            
    df.sort_index(axis=0, ascending=True, inplace=True)
    df = df.drop(columns=[col for col in df.columns if col not in columns_to_keep])
    df = df.rename(columns={column_name_for_corr: column_name_for_corr+' '+file_name})
    df = convert_str_to_float(df.drop(columns=['Date']))
    return df

def calculate_correlation(df1:  pd.DataFrame, df2:  pd.DataFrame, start_date: str, end_date: str):
    '''
    Calculate Pearson, Kendall, and Spearman correlations between two DataFrames over a specified date range.

    Parameters:
        df1 (pd.DataFrame): The first DataFrame containing time-series data.
        df2 (pd.DataFrame): The second DataFrame containing time-series data.
        start_date (str): The start date for the correlation analysis (inclusive) can be in 'YYYY-MM-DD' and 'YYYY' format.
        end_date (str): The end date for the correlation analysis (inclusive) can be in 'YYYY-MM-DD' and 'YYYY' format.

    Returns:
        None: The function prints the calculated correlations between the first columns of df1 and df2.

    Example Usage:
        # Calculate correlations between two DataFrames
        calculate_correlation(data1, data2, '2010', '2023')
    '''    
    df_combined = pd.concat([df1, df2], axis=1)
    df_combined = df_combined.dropna()
    filtered_df = df_combined[(df_combined.index >= start_date) & (df_combined.index <= end_date)]
    
    pearson_corr = filtered_df[filtered_df.columns[0]].corr(filtered_df[filtered_df.columns[1]], method='pearson')
    kendall_corr = filtered_df[filtered_df.columns[0]].corr(filtered_df[filtered_df.columns[1]], method='kendall')
    spearman_corr = filtered_df[filtered_df.columns[0]].corr(filtered_df[filtered_df.columns[1]], method='spearman')
    
    print(f"Pearson correlation between {df1.columns[0]} and {df2.columns[0]} is {abs(pearson_corr)}")
    print(f"Kendall correlation between {df1.columns[0]} and {df2.columns[0]} is {abs(kendall_corr)}")
    print(f"Spearman correlation between {df1.columns[0]} and {df2.columns[0]} is {abs(spearman_corr)}")

# def plot_correlation_heatmaps(df1, df2, start_date, end_date):
#     df_combined = pd.concat([df1, df2], axis=1)
#     df_combined = df_combined.dropna()
#     filtered_df = df_combined[(df_combined.index >= start_date) & (df_combined.index <= end_date)]

#     correlations = filtered_df.corr(method='pearson'), filtered_df.corr(method='kendall'), filtered_df.corr(method='spearman')
#     correlation_methods = ['Pearson', 'Kendall', 'Spearman']

#     for correlation, method in zip(correlations, correlation_methods):
#         plt.figure(figsize=(8, 6))
#         sns.heatmap(correlation, annot=True, cmap='coolwarm')
#         plt.title(f'{method} Correlation Heatmap')
#         plt.show()    

def plot_correlation_heatmaps(df1, df2, start_date, end_date):
    '''
    Plot correlation heatmaps between two DataFrames over a specified date range using different correlation methods.

    Parameters:
        df1: The first DataFrame containing time-series data.
        df2: The second DataFrame containing time-series data.
        start_date (str): The start date for the correlation analysis (inclusive) can be in 'YYYY-MM-DD' and 'YYYY'format.
        end_date (str): The end date for the correlation analysis (inclusive) can be in 'YYYY-MM-DD' and 'YYYY'format.

    Returns:
        None: The function displays correlation heatmaps using Plotly for Pearson, Kendall, and Spearman correlations.

    Example Usage:
        # Plot correlation heatmaps between two DataFrames
        plot_correlation_heatmaps(data1, data2, '2010', '2023')
    '''    
    df_combined = pd.concat([df1, df2], axis=1)
    df_combined = df_combined.dropna()
    filtered_df = df_combined[(df_combined.index >= start_date) & (df_combined.index <= end_date)]

    correlations = filtered_df.corr(method='pearson'), filtered_df.corr(method='kendall'), filtered_df.corr(method='spearman')
    correlation_methods = ['Pearson', 'Kendall', 'Spearman']

    for correlation, method in zip(correlations, correlation_methods):
        fig = go.Figure(data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.index,
            colorscale='RdBu',
            colorbar=dict(title='Correlation')
        ))

        fig.update_layout(
            title=f'{method} Correlation Heatmap',
            xaxis=dict(title='Columns of DataFrame'),
            yaxis=dict(title='Columns of DataFrame')
        )

        fig.show()

        
def return_files_name(path:str):
    '''
    Return a list of all file names in a specified directory.

    Parameters:
        path (str): The directory path for which you want to retrieve file names.

    Returns:
        list: A list of file names in the specified directory.

    Example Usage:
        # Get a list of file names in a directory
        file_names = return_files_name('/path/to/directory')
    '''
    files = os.listdir(path)
    return files

def return_csv_filename(path):
    '''
    Return a list of filenames (without '.csv' extension) for all CSV files in a specified directory.

    Parameters:
        path (str): The directory path for which you want to retrieve CSV file names.

    Returns:
        list: A list of filenames (without '.csv' extension) for all CSV files in the specified directory.

    Example Usage:
        # Get a list of CSV file names (without extension) in a directory
        csv_file_names = return_csv_filename('/path/to/directory')
    '''    
    string_list = return_files_name(path=path)
    updated_list = []
    for string in string_list:
        if string.endswith(".csv"):
            updated_list.append(string[:-4])
    return updated_list        
    
    
if __name__=='__main__':
    
    df_dxy = read_data(path="../../data/fund", file_name="US Dollar Index Historical Data", column_name_for_corr = 'High')
    df_wheat = read_data(path="../../data/fund", file_name="US Wheat Futures Historical Data", column_name_for_corr = 'High')
    calculate_correlation(df1=df_dxy, df2=df_wheat, start_date='2010-01-01', end_date='2020-01-01')
    plot_correlation_heatmaps(df1=df_dxy, df2=df_wheat, start_date='2010-01-01', end_date='2020-01-01')
    