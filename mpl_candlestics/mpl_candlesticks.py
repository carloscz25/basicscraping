from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.dates as mpl_dates
from matplotlib import ticker
import time
from datetime import datetime



def _candlestick_ohlc(ax, quotes, width=0.2, colorup='k', colordown='r',
                     alpha=1.0):
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of (time, open, high, low, close, ...) sequences
        As long as the first 5 elements are these values,
        the record can be as long as you want (e.g., it may store volume).

        time must be in float days format - see date2num

    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """
    return _candlestick(ax, quotes, width=width, colorup=colorup,
                        colordown=colordown,
                        alpha=alpha, ochl=False)


def _candlestick(ax, quotes, width=0.2, colorup='k', colordown='r',
                 alpha=1.0, ochl=True):
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of quote sequences
        data to plot.  time must be in float date format - see date2num
        (time, open, high, low, close, ...) vs
        (time, open, close, high, low, ...)
        set by `ochl`
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level
    ochl: bool
        argument to select between ochl and ohlc ordering of quotes

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """

    OFFSET = width / 2.0

    lines = []
    patches = []
    for q in quotes:
        if ochl:
            t, open, close, high, low = q[:5]
        else:
            t, open, high, low, close = q[:5]

        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - OFFSET, lower),
            width=width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)
    ax.autoscale_view()

    return lines, patches

class CandlesticksDateFormatter(ticker.Formatter):
    """
    Format a tick (in days since the epoch) with a
    `~datetime.datetime.strftime` format string.
    """
    df = None
    timestampMin, timestampMax = None, None

    def illegal_s(self):
        # return re.compile(r"((^|[^%])(%%)*%s)")
        pass
    def __init__(self, fmt, tz=None, df=None):
        """
        Parameters
        ----------
        fmt : str
            `~datetime.datetime.strftime` format string
        tz : `datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone.
        """
        if tz is None:
            tz = mpl_dates._get_rc_timezone()
        self.fmt = fmt
        self.tz = tz
        self.df = df


    def __call__(self, x, pos=0):
        maxindex = max(self.df.index.values)
        minindex = min(self.df.index.values)
        mindateint = int(time.mktime(self.df["tts"][minindex].timetuple()))
        maxdateint = int(time.mktime(self.df["tts"][maxindex].timetuple()))
        factor = (maxdateint - mindateint)/len(self.df.index.values)
        dateint = mindateint + (factor*x)
        datet = datetime.fromtimestamp(dateint)
        dateformatted =  datet.strftime(self.fmt)
        return dateformatted



    def set_tzinfo(self, tz):
        self.tz = tz


def plot_candlesticks(dfTicker, ax):
    ohlc = []
    for index, row in dfTicker.iterrows():
        d = mpl_dates._to_ordinalf(dfTicker["tts"][index])
        append_me = dfTicker.index[index], dfTicker["open"][index], dfTicker["high"][index], dfTicker["low"][index], dfTicker["close"][index], \
                    dfTicker["real_volume"][index],
        ohlc.append(append_me)
    _candlestick_ohlc(ax, ohlc)
    # ax.xaxis.set_major_formatter(mpl_dates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_formatter(CandlesticksDateFormatter('%d/%m', df=dfTicker))