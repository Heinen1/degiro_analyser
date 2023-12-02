import pandas as pd
import yfinance as yf

def get_amount_and_value_from_description(x):
    """Split string format: Koop [n] @ [x,y] EUR

    Parameters
    ----------
    x : string
        Koop [n] @ [x,y] EUR
    """
    index_amount = 1
    index_value = 3

    x_split = x.split(' ')
    amount = float(x_split[index_amount])
    value = float(x_split[index_value].replace(',', '.'))

    return [amount, value]

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

    df_account['Datum'] = pd.to_datetime(df_account['Datum'], infer_datetime_format=True)
    df_account['Datum_Year'] = df_account['Datum'].dt.year
    df_account['Mutatie_Bedrag'].fillna(0, inplace=True)
    df_account['Product'].fillna('', inplace=True)

    return df_account

def get_share_price_history(ticker, startdate, enddate):
    """Get Closed share price of ticker between start and enddate

    Parameters
    ----------
    ticker : string
        Ticker symbol of shares on stock exchange
    startdate : Timestamp
        Datetime of starting date of share price
    enddate : Timestamp
        Datetime of ending date of share price

    Returns
    -------
    DataFrame
        Share prices for each date between start and end
    """
    prices = yf.download(tickers=ticker, start=startdate, end=enddate)['Close']
    prices = pd.DataFrame(prices)
    prices.reset_index(inplace=True)

    return prices



