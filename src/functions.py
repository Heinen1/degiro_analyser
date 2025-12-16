import pandas as pd
import yfinance as yf
from datetime import timedelta

def get_quantity_and_value_from_description(x):
    """Split string format: Koop [n] @ [x,y] EUR
    n is quantity and x is value.

    Parameters
    ----------
    x : string
        Koop [n] @ [x,y] EUR
    """
    colunm_index_quantity = 1
    column_index_value = 3

    x_split = x.split(' ')
    quantity = float(x_split[colunm_index_quantity])
    value = float(x_split[column_index_value].replace(',', '.'))

    return [quantity, value]

def read_account_overview(filename):
    """Load Account export .xls from DeGiro, rename unnamed columns and
    replace nan-values with zeros.

    Parameters
    ----------
    filename : string
        filename of Account.xls from DeGiro website

    Returns
    -------
    DataFrame
        Account transactions of shares
    """
    df_account = pd.read_excel(filename,
                               decimal=',',
                               thousands='.')

    columns_dict = {'Mutatie': 'Mutatie_Valuta',
                    'Unnamed: 8': 'Mutatie_Bedrag',
                    'Saldo': 'Saldo_Valuta',
                    'Unnamed: 10': 'Saldo_Bedrag'}

    df_account.rename(columns=columns_dict, inplace=True)

    df_account.fillna({
        'Mutatie_Bedrag': 0,
        'Product': ''
    }, inplace=True)

    df_account['Datum'] = pd.to_datetime(df_account['Datum'], format="%d-%m-%Y")
    df_account['Datum_Year'] = df_account['Datum'].dt.year
    df_account['Datum_Year_Month'] = df_account['Datum'].dt.strftime('%Y-%m')
    df_account.sort_values(by=['Datum'], ascending=True, inplace=True)

    return df_account

def get_historical_stock_price(ticker, start_date, end_date, interval='1mo'):
    """Get historical stock price of ticker from Yahoo Finance.

    Parameters
    ----------
    ticker : string
        Ticker of stock
    start_date : string
        Start date of historical stock price
    end_date : string
        End date of historical stock price
    interval : string
        Interval of historical stock price

    Returns
    -------
    DataFrame
        Historical stock price of ticker
    """
    stock = yf.Ticker(ticker)
    # for 1-month interval: open = at first day of month, high/low = highest/lowest of that month,
    # close = last available day of the month (if month is not over).
    df_stock = stock.history(start=start_date, end=end_date, interval=interval)

    df_stock['Datum_Year_Month'] = df_stock.index.strftime('%Y-%m')

    return df_stock

def get_start_datetime(earliest_date):
    """Get current and start datetime.

    Returns
    -------
    datetime
        Current datetime
    """

    start_day = earliest_date.day
    start_datetime = earliest_date.strftime('%Y-%m-%d')

    # If they ticker interval is set per month, the start date should be the first of the month
    # If the start day is not equal to one, subtract one month from the earliest date to get
    # the stock price at the first of the month
    if start_day > 1:
        start_datetime = (earliest_date - timedelta(days=start_day)).strftime('%Y-%m-%d')

    return start_datetime


