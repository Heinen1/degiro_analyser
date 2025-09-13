import pandas as pd
import yfinance as yf

def get_quantity_and_value_from_description(x):
    """Split string format: Koop [n] @ [x,y] EUR
    n is quantity and x is value.

    Parameters
    ----------
    x : string
        Koop [n] @ [x,y] EUR
    """
    index_quantity = 1
    index_value = 3

    x_split = x.split(' ')
    quantity = float(x_split[index_quantity])
    value = float(x_split[index_value].replace(',', '.'))

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

    df_account['Datum'] = pd.to_datetime(df_account['Datum'], format="%d-%m-%Y")
    df_account['Datum_Year'] = df_account['Datum'].dt.year
    df_account.fillna({'Mutatie_Bedrag': 0}, inplace=True)
    df_account.fillna({'Product': ''}, inplace=True)
    # Transform the date to a year-month format for grouping per month
    df_account['datum_reduced'] = df_account['Datum'].dt.strftime('%Y-%m')
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
    df_stock = stock.history(start=start_date, end=end_date, interval=interval)

    return df_stock

def get_current_datetime():
    """Get current datetime.

    Returns
    -------
    datetime
        Current datetime
    """
    return 


