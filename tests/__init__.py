from algotrader.trading.config import Config

test_override = {
    "Application": {
        "dataStoreId": "InMemory",
        "createDBAtStart": True,
        "deleteDBAtStop": False,
        "plot": False
    },
    "DataStore": {"InMemory":
        {
            "file": "../data/algotrader_backtest_db.p",
            "instCSV": "../data/refdata/instrument.csv",
            "ccyCSV": "../data/refdata/ccy.csv",
            "exchCSV": "../data/refdata/exch.csv"
        }
    },
    "Feed": {"CSV":
                 {"path": "/mnt/data/dev/workspaces/python-trading/data/tradedata"}
             }
}

config = Config(test_override)

empty_config = Config({
    "Application": {
        "dataStoreId": "InMemory",
        "createDBAtStart": True,
        "deleteDBAtStop": False
    },
    "DataStore": {"InMemory":
        {
            "file": "../data/algotrader_backtest_db.p",
        }
    },
    "Feed": {"CSV":
                 {"path": "/mnt/data/dev/workspaces/python-trading/data/tradedata"}
             }
})
