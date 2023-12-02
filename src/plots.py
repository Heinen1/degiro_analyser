import matplotlib.pyplot as plt

def plot_dividend(x, y1, y2, currency):
    """Plot dividend and cumulative dividend as function of time.
    Does NOT include DEGIRO Corporate Action Cost nor FX rate conversion.

    Parameters
    ----------
    x : Series
        Date of each dividend return
    y1 : Series
        Value of dividend paid-out per time unit
    y2 : Series
        Cumulative of dividend paid-out
    currency : string
        Currency in which dividend is paid out
    """
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x, y1, 'o-', color='g')
    ax2.plot(x, y2, 'o-', color='b')
    ax1.set_xlabel('Datum')
    ax1.set_ylabel('Dividend (' + currency + ')', color='g')
    ax2.set_ylabel('Dividend Cum (' + currency + ')', color='b')
    ax1.tick_params(labelrotation=45)

def plot_transactions(x, y1, y2, currency):
    """Plot transactions of shares and cumulative transactions as function of time.

    Parameters
    ----------
    x : Series
        Date of each dividend return
    y1 : Series
        Transaction of each purchased share
    y2 : Series
        Cumulative transactions of each shares
    currency : string
        Currency in which share is purchased
    """
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x, y1, 'o-', color='g')
    ax2.plot(x, y2, 'o-', color='b')
    ax1.set_xlabel('Datum')
    ax1.set_ylabel('Aankopen (' + currency + ')', color='g')
    ax2.set_ylabel('Aankopen Cum (' + currency + ')', color='b')
    ax1.tick_params(labelrotation=45)
