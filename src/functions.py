import pandas as pd
import yfinance as yf
from datetime import timedelta

def dividends(df_account, base_currency):
    """
    Calculate dividends paid out in base currency:
    
    Equation: (Dividends - CAK) * FX with
    - Dividends: paid out dividends by security
    - CAK: DEGIRO Corporate Action Kosten (CAK)
    - FX: Foreign Exchange rate

    Assumptions (DEGIRO-specific):
    1. Dividend and CAK occur on *same* Valutadatum
    2. Dividend and CAK have same currency
    3. CAK is incurred *before* conversion of currency
    4. AutoFX is enabled in DEGIRO

    Args:
        df_account (DataFrame): Account overview loaded in datafrane
        base_currency (string): Base currency of account statement (e.g. USD or EUR)

    Returns:
        Dividends paid out on Valutadatum and converted to base currency
    """

    # General comment:
    # - The DEGIRO Corporate Action Kosten are usually one line above the Dividend entry in the account overview.
    #   However there are also occurances that the CAK are incured months after the Dividend (e.g. I have 2 CAKs
    #   on date 18-11-2023 with a valutadatum of 28-06-2023 and 28-03-2023).

    # ------------------------------------------------------------------
    # 1. Extract dividends and corporate action costs (CAK)
    # ------------------------------------------------------------------
    # - The CAK entry has no description in the Product column.
    # - Merge has only been tested using a single product (!); cross-product contamination can occur.
    cols_dividend = ['Datum', 'Valutadatum', 'Product', 'Mutatie_Valuta', 'Mutatie_Bedrag']
    cols_cak = ['Valutadatum', 'Mutatie_Bedrag']
    
    df_dividend = df_account[
        df_account['Omschrijving'].str.contains('Dividend', na=False)
    ][cols_dividend]
    
    df_cak = df_account[
        df_account['Omschrijving'].str.contains('Corporate Action Kosten', na=False)
    ][cols_cak].rename(columns={'Mutatie_Bedrag': 'CAK'})

    # Merge CAK with dividends. If CAK is missing -> assume zero)
    df_dividend = df_dividend.merge(
        df_cak,
        how='outer',
        on='Valutadatum',
    ).assign(CAK=lambda x: x['CAK'].fillna(0))
    
    df_dividend['Dividend_foreign'] = df_dividend['Mutatie_Bedrag'] + df_dividend['CAK']

    # ------------------------------------------------------------------
    # 2. Build FX table (default FX = 1 for base currency)
    # ------------------------------------------------------------------
    df_fx_init = pd.DataFrame({
        'Datum': df_dividend['Datum'],
        'Mutatie_Valuta': df_dividend['Mutatie_Valuta'],
        'FX': 1
    })
    
    # Extract all FX entries from (1) account statement, or (2) external API. 
    # Only dividends that are *not* in base currency are extracted from account statement.
    df_fx_source = get_fx_for_dividends(df_account, option='account')

    df_fx = df_fx_init.merge(
        df_fx_source[['Valutadatum', 'FX']],
        left_on="Datum",
        right_on="Valutadatum",
        how="left",
        suffixes=("", "_source")
    )

    # Replace all FX rates in non base currency with the correct FX
    mask = df_fx["Mutatie_Valuta"] != base_currency
    df_fx.loc[mask, "FX"] = df_fx.loc[mask, "FX_source"]

    # ------------------------------------------------------------------
    # 3. Apply FX and finalize output
    # ------------------------------------------------------------------
    
    # Valuta Debitering Valutadatum should agree with the Datum of DEGIRO CAK and Dividend
    df_dividend = df_dividend.merge(
        df_fx[['Valutadatum', 'FX']],
        how='inner',
        left_on='Datum',
        right_on='Valutadatum',
        suffixes=('', '_fx')
    )

    # After merge there will be two `Valutadatum` columns (original from dividends
    # and one from the FX table). Keep the original `Valutadatum` (dividend date)
    # and remove the duplicate added by the FX merge.
    if 'Valutadatum_fx' in df_dividend.columns:
        df_dividend.drop(columns=['Valutadatum_fx'], inplace=True)

    # FX: base currency --> foreign currency, thus:
    # 1 / FX: foreign currency --> base currency
    df_dividend['Dividend_base'] = df_dividend['Dividend_foreign'] * (1 / df_dividend['FX'])
    df_dividend['Datum_Year_Month'] = df_dividend['Datum'].dt.strftime('%Y-%m')

    return df_dividend[['Product', 'Valutadatum', 'Datum_Year_Month', 'Dividend_base']]


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
    Get foreign exchange rates for the dividends from the account statement.

    Args:
        df_account (DataFrame): Account statements loaded in dataframe

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
    """Get the quanity (the amount) and value from the description string.
    
    Split string format: Koop [n] @ [x,y] EUR
    with n is quantity and x is value.

    Args:
        x (string): Description string from account overview

    Returns:
        list: [quantity, value]
    """
    colunm_index_quantity = 1
    column_index_value = 3

    x_split = x.split(' ')
    quantity = float(x_split[colunm_index_quantity])
    value = float(x_split[column_index_value].replace(',', '.'))

    return [quantity, value]

def read_account_overview(filename):
    """Load account statement export .csv from DeGiro.
    
    Unnamed columns and are names, nan-values are replaced with zeros, and
    dates are typecasted to datetime objects.

    Args:
        filename (string): filename of Account.csv from DeGiro website
    
    Returns:
        DataFrame: Account overview loaded in dataframe
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

def get_historical_stock_price(
    ticker, 
    start_date,
    end_date,
    interval='1mo'
):
    """Get stock prices of security using ticker symbol between 2 dates.

    Args:
        ticker (string): Ticker of stock
        start_date (string): Start date of stock price
        end_date (string): End date of stock price
        interval (string): Interval of stock price
    
    Returns:
        DataFrame: Stock price of ticker between start_date and end_date
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
        earliest_date (datetime): Earliest date to get stock price from

    Returns:
        start_datetime (datetime): Start date to get stock price from
    """
    start_day = earliest_date.day
    start_datetime = earliest_date.strftime('%Y-%m-%d')

    # If they ticker interval is set per month, the start date should be the first of the month
    # If the start day is not equal to one, subtract one month from the earliest date to get
    # the stock price at the first of the month
    if start_day > 1:
        start_datetime = (earliest_date - timedelta(days=start_day)).strftime('%Y-%m-%d')

    return start_datetime


