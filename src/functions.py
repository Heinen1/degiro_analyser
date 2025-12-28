import pandas as pd
import yfinance as yf
from datetime import timedelta

def dividends(df_account):
    """
    Equation for paid out dividends (_div) in base currency: (Dividends - CAK) * FX where
    - Dividends: paid out dividends by security
    - CAK: DEGIRO Corporate Action Kosten (CAK)
    - FX: Foreign Exchange rate

    The following is assumed to be true for the DEGIRO overview
    1. Dividend and CAK occur on *same* Valutadatum
    2. Currency of Dividend and CAK are the *same*
    3. CAK is incurred *before* conversion of currency
    4. AutoFX is enabled in DEGIRO

    Args:
        df_account (DataFrame): Account overview loaded in datafrane

    Returns:
        Dividends paid out on Valutadatum and converted to base currency
    """

    # Some general comments:
    # - Valutadatum is fictive date on which a bank actually process a transactions for interest calculations, 
    #   which can differ from the booking date (day of the actual transaction).
    # - The DEGIRO Corporate Action Kosten are usually one line above the Dividend entry in the account overview.
    #   However there are also occurances that the CAK are incured months after the Dividend (e.g. I have 2 CAKs
    #   on date 18-11-2023 with a valutadatum of 28-06-2023 and 28-03-2023).
    # - Valuta Debitering Valutadatum should agree with the Booking date of DEGIRO CAK and Dividend
    # - If a currency conversion takes place in the account, you will be see entries of Valuta Debitering and Valuta Creditering
    #   in the account statement. [1] These are also visible when purchasing securities on a stock exchange that holds a different
    #   currency than the base currency.
    #
    # [1] https://www.degiro.nl/helpdesk/tarieven/transactiekosten/zijn-er-kosten-verbonden-voor-het-handelen-een-vreemde-valuta)
    
    cols_merge = ['Datum', 'Valutadatum', 'Mutatie_Bedrag']
    df_dividend = df_account[df_account['Omschrijving'].str.contains('Dividend', na=False)][cols_merge + ['Product']]
    df_cak = df_account[df_account['Omschrijving'].str.contains('Corporate Action Kosten', na=False)][cols_merge]

    # Assumption 1: Dividend and CAK occur on *same* Valutadatum
    # The CAK entry has no description in the Product column.
    # Outer join ensures that CAK is added as additional column in the dataframe.
    # If there are no GAKs, (e.g. using Basic account), the nan values are replaced by zero.

    # IMPORTANT: this merge has only been tested using a single product. 
    # If multiple products are available and pay out dividends at the same Valutadatum, you will get
    # combinations that are cross-contaminated. 

    # Another approach to match CAK with Dividends is to find the 'closest' entry of CAK for each
    # Dividend entry in the account statement.
    df_dividend = df_dividend.merge(
        df_cak,
        how='outer',
        on='Valutadatum',
        suffixes=('_div', '_cak')
    )
    df_dividend['Mutatie_Bedrag_cak'] = df_dividend['Mutatie_Bedrag_cak'].fillna(0)
    df_dividend['Valuta Debitering calc'] = df_dividend['Mutatie_Bedrag_div'] + df_dividend['Mutatie_Bedrag_cak']

    # ToDO. Check if product is in foreign currency

    # Two options to get the FX (1) extract from Account overview (2) use external Python API (tdb)
    df_fx = get_fx_for_dividends(df_account, option='account')

    # For every dividend and CAK combination, one should also get the FX
    df_dividend = df_dividend.merge(
        df_fx,
        how='inner',
        left_on='Datum_div',
        right_on='Valutadatum',
        suffixes=('_div', '_fx')
    )

    # FX is base currency --> foreign currency
    # So foreign to base is 1 / FX
    df_dividend['Valuta Creditering calc'] = df_dividend['Valuta Debitering calc'] * (1 / df_dividend['FX'])
    df_dividend['Datum_Year_Month'] = df_dividend['Datum_div'].dt.strftime('%Y-%m')

    return df_dividend[['Product', 'Valutadatum_div', 'Datum_Year_Month', 'Valuta Creditering calc']]


def get_fx_for_dividends(df_account, option='account'):
    """
    FX can be extracted from (1) Account document or (2) external Python APIs.

    Option (1) Account document
    - The Valuta Debitering row where the Valuta Datum equals to the booking datum of the Dividend has 
      * a non-zero FX column
      * empty description
    
    Option (2) external Python APIs

    Args:
        df_account (DataFrame): Account overview loaded in dataframe
        option (string): Select option to calculate the FX

    Returns:
        DataFrame containing FX exchange rate for each of Valutadaum

        
    """
    if option == 'external':
        return get_fx_for_dividends_from_external(df_account)

    return get_fx_for_dividends_from_account(df_account)


def get_fx_for_dividends_from_account(df_account):
    """
    Get FX for the dividends from the account overview.

    Args:
        df_account (DataFrame): Account overview loaded in dataframe

    Returns:
        DataFrame containing FX for each dividend transaction 
    """
    cols_debitering = ['Valutadatum', 'FX', 'Mutatie_Bedrag']

    # FX is base currency --> foreign currency
    mask1 = (df_account['FX'].notna())

    # Purchase of foreign security also contains a non-zero FX
    # The Product column is empty for Dividend transactions
    mask2 = (df_account['Product'].str.strip() == '')
    
    return df_account[mask1 & mask2][cols_debitering]
    
def get_fx_for_dividends_from_external(df_account):
    """
    [To be done]
    """
    return None


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
    """Load Account export .csv from DeGiro, rename unnamed columns and
    replace nan-values with zeros.

    Args:
        filename (string): filename of Account.csv from DeGiro website

    Returns:
        Account transactions of securities
    """
    df_account = pd.read_csv(
        filename,
        decimal=',',
        thousands='.'
    )

    columns_dict = {'Mutatie': 'Mutatie_Valuta',
                    'Unnamed: 8': 'Mutatie_Bedrag'}

    df_account.rename(columns=columns_dict, inplace=True)

    df_account.fillna({
        'Mutatie_Bedrag': 0,
        'Product': ''
    }, inplace=True)

    # Typecast strings to datatime objects
    df_account['Datum_datetime'] = pd.to_datetime(df_account["Datum"] + " " + df_account["Tijd"], format="%d-%m-%Y %H:%M")
    df_account['Datum'] = pd.to_datetime(df_account['Datum'], format="%d-%m-%Y")
    df_account['Datum_Year'] = df_account['Datum'].dt.year
    df_account['Datum_Year_Month'] = df_account['Datum'].dt.strftime('%Y-%m')

    df_account['Valutadatum'] = pd.to_datetime(df_account['Valutadatum'], format="%d-%m-%Y")
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

    Args:
        earliest_date (datetime)
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


