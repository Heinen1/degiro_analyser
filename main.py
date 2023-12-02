import pandas as pd
from src.functions import get_amount_and_value_from_description
from src.functions import read_account_overview
from src.functions import get_share_price_history
from src.plots import plot_dividend, plot_transactions

%load_ext autoreload
%autoreload 2

# Load account xls into dataframe
df_account = read_account_overview('Account.xls')

# Define product (does not need to be the entire name)
product = 'VANGUARD'

# Get only records of pre-defined product
df_account = df_account[df_account['Product'].str.contains(product)]

# Select of all transaction of pre-defined product
transactions = df_account[df_account['Omschrijving'].str.contains('Koop')]
transactions.sort_values(by=['Datum'], inplace=True)
transactions[['Transaction_Quantity', 'Transaction_Amount']] = transactions['Omschrijving'].apply(lambda x: get_amount_and_value_from_description(x)).tolist()
transactions['Transaction_Quantity_cumulative'] = transactions['Transaction_Quantity'].cumsum(axis=0)
transactions['Transaction_Total'] = transactions['Transaction_Quantity'] * transactions['Transaction_Amount']
transactions['Transaction_Total_Cum'] = transactions['Transaction_Total'].cumsum(axis=0)

currency = transactions['Mutatie_Valuta'].values[0]
plot_transactions(transactions['Datum'],
                  transactions['Transaction_Total'],
                  transactions['Transaction_Total_Cum'],
                  currency)

dividend = df_account[df_account['Omschrijving'].str.contains('Dividend')][['Datum', 'Datum_Year', 'Mutatie_Valuta', 'Mutatie_Bedrag']]
dividend.sort_values(by=['Datum'], inplace=True)
dividend['Mutatie_Bedrag_Cum'] = dividend['Mutatie_Bedrag'].cumsum(axis=0)

currency = dividend['Mutatie_Valuta'].values[0]
plot_dividend(dividend['Datum'],
              dividend['Mutatie_Bedrag'],
              dividend['Mutatie_Bedrag_Cum'],
              currency)