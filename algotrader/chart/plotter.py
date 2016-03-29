import matplotlib.pyplot as plt

from algotrader.trading.instrument_data import inst_data_mgr


class TimeSeriesPlot:
    def __init__(self, time_series, marker=" ", color=None):
        self.time_series = time_series
        self.marker = marker
        self.color = color

    def get_marker(self):
        return self.marker

    def get_color(self):
        return self.color

    def plot(self, ax):
        df = self.time_series.get_series()
        df.plot(ax=ax, color=self.get_color(), marker=self.get_marker())


axescolor = '#f6f6f6'  # the axes background color
fillcolor = 'darkgoldenrod'
textsize = 8
left, width = 0.1, 0.8
rect_stock = [left, 0.6, width, 0.29]
rect_indicator = [left, 0.5, width, 0.09]
rect_equity = [left, 0.3, width, 0.19]
rect_pnl = [left, 0.2, width, 0.09]
rect_drawdown = [left, 0.1, width, 0.09]


class StrategyPlotter:
    def __init__(self, strategy):
        self.strategy = strategy

    def plot(self, instrument = None):
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

        fig = plt.figure(facecolor='white')

        ax_stock, ax_stock_t = self._plot_bar_chart(fig, instrument)
        ax_indicator = self._plot_indicator(fig, ax_stock)
        ax_equity = self._plot_equity(fig, ax_stock)
        ax_pnl = self._plot_pnl(fig, ax_stock)
        ax_drawdown = self._plot_draw_down(fig, ax_stock)

        plt.show()

    def _plot_bar_chart(self, fig, instrument = None):
        key = "Bar.%s.86400.Close" % instrument
        series = inst_data_mgr.get_series(key)
        #key = series_dict.keys()[0]

        ax_stock = fig.add_axes(rect_stock, axisbg=axescolor)  # left, bottom, width, height

        # pmax = series.max()
        ax_stock.text(0.025, 0.95, 'Chart', va='top', transform=ax_stock.transAxes, fontsize=textsize)
        ax_stock.set_title(key)
        # ax_stock.set_ylim(0, 1.1 * pmax)

        #series = series_dict[key]
        if series.size() > 0:
            series = TimeSeriesPlot(series)
            series.plot(ax=ax_stock)

        ## Plot volume
        ax_stock_t = ax_stock.twinx()
        # volume = (s1*s2)/1e6  # dollar volume in millions
        # vmax = volume.max()
        # poly = ax_stock_t.fill_between(df1.index, volume, 0, label='Volume', facecolor=fillcolor, edgecolor=fillcolor)
        # ax_stock_t.set_ylim(0, 5*vmax)
        # ax_stock_t.set_yticks([])

        return ax_stock, ax_stock_t

    def _plot_indicator(self, fig, ax_stock):
        ax_indicator = fig.add_axes(rect_indicator, axisbg=axescolor, sharex=ax_stock)
        ax_indicator.text(0.025, 0.95, 'Indicator', va='top', transform=ax_indicator.transAxes, fontsize=textsize)
        # s2.plot(ax=ax_indicator)

        return ax_indicator

    def _plot_equity(self, fig, ax_stock):
        ax_equity = fig.add_axes(rect_equity, axisbg=axescolor, sharex=ax_stock)
        ax_equity.text(0.025, 0.95, 'Equity', va='top', transform=ax_equity.transAxes, fontsize=textsize)

        if (self.strategy.get_portfolio().total_equity_series.size() > 0):
            series = TimeSeriesPlot(self.strategy.get_portfolio().total_equity_series)
            series.plot(ax=ax_equity)

        return ax_equity

    def _plot_pnl(self, fig, ax_stock):

        ax_pnl = fig.add_axes(rect_pnl, axisbg=axescolor, sharex=ax_stock)
        ax_pnl.text(0.025, 0.95, 'Pnl', va='top', transform=ax_pnl.transAxes, fontsize=textsize)

        if (self.strategy.get_portfolio().pnl_series.size() > 0):
            series = TimeSeriesPlot(self.strategy.get_portfolio().pnl_series)
            series.plot(ax=ax_pnl)

        return ax_pnl

    def _plot_draw_down(self, fig, ax_stock):

        ax_drawdown = fig.add_axes(rect_drawdown, axisbg=axescolor, sharex=ax_stock)
        ax_drawdown.text(0.025, 0.95, 'Drawdown', va='top', transform=ax_drawdown.transAxes, fontsize=textsize)
        if (self.strategy.get_portfolio().drawdown_series.size() > 0):
            series = TimeSeriesPlot(self.strategy.get_portfolio().drawdown_series)
            series.plot(ax=ax_drawdown)

        return ax_drawdown
