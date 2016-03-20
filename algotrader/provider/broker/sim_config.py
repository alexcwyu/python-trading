class SimConfig:
    class FillMode:
        LAST = 0
        NEXT_OPEN = 1
        NEXT_CLOSE = 2

    def __init__(self, partial_fill=True,
                 fill_on_quote=True,
                 fill_on_trade=True,
                 fill_on_bar=True,
                 fill_on_quote_mode=FillMode.LAST,
                 fill_on_trade_mode=FillMode.LAST,
                 fill_on_bar_mode=FillMode.LAST):
        self.partial_fill = partial_fill
        self.fill_on_quote = fill_on_quote
        self.fill_on_trade = fill_on_trade
        self.fill_on_bar = fill_on_bar
        self.fill_on_quote_mode = fill_on_quote_mode
        self.fill_on_trade_mode = fill_on_trade_mode
        self.fill_on_bar_mode = fill_on_bar_mode
