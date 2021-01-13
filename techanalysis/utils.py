import pandas
import datetime
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import TickerMC
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib



def calc_emaN_on_ticker_from_date(ticker, date, Nperiods, engine):
    if type(date)!=datetime.date:
        raise TypeError()
    if type(engine)!=sqlalchemy.engine.Engine:
        raise TypeError()
    if (type(ticker)!=str):
        raise TypeError()
    datestr = date.strftime("%Y-%m-%d")
    sql = "select *, STR_TO_DATE(fechatexto,'%d-%m-%Y') as fechacierre from cotizaciones_hist_mc where ticker = '{0}' and STR_TO_DATE(fechatexto,'%d-%m-%Y') < '{1}' order by id desc".format(ticker, datestr)
    df = pandas.read_sql(sql, engine)
    df.set_index("fechacierre", inplace=True)
    valorcierre = df['valorcierre']
    val = valorcierre.ewm(span=Nperiods, adjust=False).mean()
    df['valorcierre'] = val
    df.drop(columns=["id","nombre","ticker","percdiff","fechatexto"], inplace=True)


    return val

def calc_ema50_on_ticker_from_date(ticker, date, engine):
    return calc_emaN_on_ticker_from_date(ticker, date, 50, engine)

def calc_ema100_on_ticker_from_date(ticker, date, engine):
    return calc_emaN_on_ticker_from_date(ticker, date, 100, engine)

def get_values_descending_for_ticker_from_date(ticker, date, engine):
    datestr = date.strftime("%Y-%m-%d")
    sql = "select *, STR_TO_DATE(fechatexto,'%d-%m-%Y') as fechacierre from cotizaciones_hist_mc where ticker = '{0}' and STR_TO_DATE(fechatexto,'%d-%m-%Y') < '{1}' order by id desc".format(
        ticker, datestr)
    df = pandas.read_sql(sql, engine)
    df.set_index("fechacierre", inplace=True)
    df.drop(columns=["id","nombre","fechatexto","ticker","percdiff"], inplace=True)
    valorcierre = df['valorcierre']
    return valorcierre

def stochastic_oscilator_K(windowprices):
    res = 100*((windowprices[len(windowprices)-1]-windowprices.min())/(windowprices.max()-windowprices.min()))
    return res

def calc_stochastic_indicator_for_ticker_from_date(ticker, date, nperiods, engine):
    values = get_values_descending_for_ticker_from_date(ticker, date, engine)
    #line %K
    res = values.rolling(nperiods).apply(lambda x:stochastic_oscilator_K(x))
    return res


def plot_standard_timeseries(df):
    if (isinstance(df, pandas.Series)):
        dfr = pandas.DataFrame()
        dfr['values'] = df
        df = dfr
    plt.figure(figsize=(15, 10))
    for c in df.columns:
        plt.plot(df[c], label=c)

    plt.legend(loc=1)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.show()

def plot_emas_and_stochoscilators_for_ticker(ticker, emas, stochastics, engine):
    emasseries = {}
    stochasticsseries = {}

    for e in emas:
        emasseries[e] = (calc_emaN_on_ticker_from_date(ticker, datetime.datetime.now().date(), e, engine))
    values = get_values_descending_for_ticker_from_date(ticker, datetime.datetime.now().date(), engine)
    for s in stochastics:
        s_ = calc_stochastic_indicator_for_ticker_from_date(ticker, datetime.datetime.now().date(), s, engine)
        stochasticsseries[s] = (s_.rolling(3).mean())

    fig = plt.figure(figsize=[15, 10])
    gs = matplotlib.gridspec.GridSpec(2, 1, height_ratios=(0.8, 0.2))
    axs = []
    axs.append(fig.add_subplot(gs[0]))
    axs.append(fig.add_subplot(gs[1], sharex=axs[0]))

    for k,v in emasseries.items():
        axs[0].plot(v, label="R"+str(k), linewidth=0.5)
    axs[0].plot(values, label="Price", linewidth=0.5)
    for k,v in stochasticsseries.items():
        axs[1].plot(v, label="Stoch"+str(k), linewidth=0.5)

    axs[0].legend(loc=1)
    axs[1].legend(loc=1)
    axs[0].grid(True)
    axs[1].grid(True)

    fig.suptitle(ticker)
    plt.show()




engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")
ticker = "ANA"

plot_emas_and_stochoscilators_for_ticker(ticker, [50,100], [14,28,56], engine)



