import matplotlib.pyplot as plt
from matplotlib.axis import Axis   
from matplotlib.ticker import FuncFormatter

# Dictionary with keys as currencies (eur and usd) and value unicode
currency_symbols = {'EUR': '€', 'USD': '$'}

def plot_metric_and_cum_metric(product, date, metric, metric_cum, currency, ylabel):
    """Plot metric and cumulative metric as function of time.
    Does NOT i) include DEGIRO Corporate Action Cost, ii) FX rate conversion.

    Parameters
    ----------
    product: string
        Product name
    date : Series
        Date of each dividend return
    metric : Series
        Value of metric per time unit
    metric_cum : Series
        Cumulative of metric per time unit
    currency : string
        Three letter symbols for currency in which dividend is paid out
    ylabel : string
        Label for y-axis
    """
    # Create subplots with gridspec
    fig, axs = plt.subplots(2, sharex=True)

    # Top subplot for cumulative metric
    axs[0].set_title(product)
    axs[0].plot(date, metric_cum, 'o-', color='b')
    axs[0].set_ylabel('Cumulative ' + ylabel)
    axs[0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{currency_symbols[currency]}{x:,.0f}'))
    axs[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)  # Hide x-axis labels

    # Bottom subplot for metric
    axs[1].bar(date, metric, color='grey')
    axs[1].set_xlabel('Datum')
    axs[1].set_ylabel(ylabel)
    axs[1].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{currency_symbols[currency]}{x:,.0f}'))
    axs[1].set_xticklabels(date, rotation=45, ha='right')

    # Add grid to subplots
    axs[0].grid(ls='--', alpha=0.5)
    axs[1].grid(ls='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

def plot_dividend(product, date, dividend, dividend_cum, currency):
    """Plot dividend and cumulative dividend as function of time.
    Does NOT i) include DEGIRO Corporate Action Cost, ii) FX rate conversion.

    Parameters
    ----------
    product: string
        Product name of dividend return
    date : Series
        Date of each dividend return
    dividend : Series
        Value of dividend paid-out per time unit
    dividend_cum : Series
        Cumulative of dividend paid-out
    currency : string
        Three letter symbols for currency in which dividend is paid out
    """
    plot_metric_and_cum_metric(product, date, dividend, dividend_cum, currency, 'Dividend')

def plot_transactions(product, date, amount_share, amount_share_cum, currency):
    """Plot transactions of shares and cumulative transactions as function of time.

    Parameters
    ----------
    product: string
        Product name of transaction
    date : Series
        Date of each dividend return
    amount_share : Series
        Transaction of each purchased share
    amount_share_cum : Series
        Cumulative transactions of each shares
    currency : string
        Currency in which share is purchased
    """
    plot_metric_and_cum_metric(product, date, amount_share, amount_share_cum, currency, 'Aankoop')

def plot_cumulative_transaction_value_and_current_value(product, date, transaction_cum, current_cum, currency):
    """Plot cumulative value and current value as function of time.

    Parameters
    ----------
    product: string
        Product name of transaction
    date : Series
        Date of each dividend return
    transaction_cum : Series
        Cumulative value of shares
    current_cum : Series or float
        Current value of shares at end of date 
    currency : string
        Currency in which share is purchased
    """
    fig, ax = plt.subplots(1)
    ax.set_title(product)
    ax.plot(date, transaction_cum, 'o-', color='blue', label='Cumulatieve Waarde')
    ax.plot(date, current_cum, 'o-', color='grey', label='Cumulatieve Waarde historische koers')
    ax.set_xlabel('Datum')
    ax.set_ylabel('Waarde')
    ax.legend()
    # Use FuncFormatter to add currency symbol to y-axis


    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{currency_symbols[currency]}{x:,.0f}'))
    ax.set_xticklabels(date, rotation=45, ha='right')
    ax.grid(ls='--', alpha=0.5)

    plt.tight_layout()
    plt.show()