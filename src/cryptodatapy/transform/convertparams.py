import logging
from datetime import datetime, timedelta
from importlib import resources
from typing import Dict, List, Union

import pandas as pd

from cryptodatapy.extract.datarequest import DataRequest


class ConvertParams:
    """
    Converts data request parameters from CryptoDataPy to data source format.
    """

    def __init__(self, data_req: DataRequest):
        """
        Constructor

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        """
        self.data_req = data_req

    def to_cryptocompare(self) -> Dict[str, Union[list, str, int, float, None]]:
        """
        Convert tickers from CryptoDataPy to CryptoCompare format.
        """
        # convert tickers
        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            tickers = [ticker.upper() for ticker in self.data_req.tickers]
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            if self.data_req.freq[-3:] == "min":
                freq = "histominute"
            elif self.data_req.freq[-1] == "h":
                freq = "histohour"
            else:
                freq = "histoday"
        # convert quote ccy
        if self.data_req.quote_ccy is None:
            quote_ccy = "USD"
        else:
            quote_ccy = self.data_req.quote_ccy.upper()
        # convert exch
        if self.data_req.exch is None:
            exch = "CCCAGG"
        else:
            exch = self.data_req.exch
        # convert start date
        if self.data_req.freq[-3:] == "min":  # limit to higher frequency data responses
            start_date = round((datetime.now() - timedelta(days=7)).timestamp())
        # no start date
        elif self.data_req.start_date is None:
            start_date = round(pd.Timestamp("2009-01-03 00:00:00").timestamp())
        else:
            start_date = round(pd.Timestamp(self.data_req.start_date).timestamp())
        # convert end date
        if self.data_req.end_date is None:
            end_date = round(pd.Timestamp.utcnow()).timestamp()
        else:
            end_date = round(pd.Timestamp(self.data_req.end_date).timestamp())
        # fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='cryptocompare')
        # tz
        if self.data_req.tz is None:
            tz = "UTC"
        else:
            tz = self.data_req.tz

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": exch,
            "ctys": None,
            "mkt_type": self.data_req.mkt_type,
            "mkts": None,
            "start_date": start_date,
            "end_date": end_date,
            "fields": fields,
            "tz": tz,
            "inst": None,
            "cat": 'crypto',
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_coinmetrics(self) -> Dict[str, Union[list, str, int, float, None]]:
        """
        Convert tickers from CryptoDataPy to CoinMetrics format.
        """
        # convert tickers
        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            tickers = [ticker.lower() for ticker in self.data_req.tickers]
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            if self.data_req.freq is None:
                freq = "1d"
            elif self.data_req.freq == "block":
                freq = "1b"
            elif self.data_req.freq == "tick":
                freq = "raw"
            elif self.data_req.freq[-1] == "s":
                freq = "1s"
            elif self.data_req.freq[-3:] == "min":
                freq = "1m"
            elif self.data_req.freq[-1] == "h":
                freq = "1h"
            else:
                freq = "1d"
        # convert quote ccy
        if self.data_req.quote_ccy is None:
            quote_ccy = "usdt"
        else:
            quote_ccy = self.data_req.quote_ccy.lower()
        # convert inst
        if self.data_req.inst is None:
            inst = "grayscale"
        else:
            inst = self.data_req.inst.lower()
        # convert to exch
        if self.data_req.exch is None:
            exch = "binance"
        else:
            exch = self.data_req.exch.lower()
        # fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='coinmetrics')
        # convert tz
        if self.data_req.tz is None:
            tz = "UTC"
        else:
            tz = self.data_req.tz
        # convert tickers to markets
        mkts_list = []

        if self.data_req.source_tickers is not None:
            mkts_list = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers

        for ticker in self.data_req.tickers:
            if self.data_req.mkt_type == "spot":
                mkts_list.append(
                    exch
                    + "-"
                    + ticker.lower()
                    + "-"
                    + quote_ccy.lower()
                    + "-"
                    + self.data_req.mkt_type.lower()
                )
            elif self.data_req.mkt_type == "perpetual_future":
                if exch == "binance" or exch == "bybit" or exch == "bitmex":
                    mkts_list.append(
                        exch
                        + "-"
                        + ticker.upper()
                        + quote_ccy.upper()
                        + "-"
                        + "future"
                    )
                elif exch == "ftx":
                    mkts_list.append(
                        exch + "-" + ticker.upper() + "-" + "PERP" + "-" + "future"
                        )
                elif exch == "okex":
                    mkts_list.append(
                        exch
                        + "-"
                        + ticker.upper()
                        + "-"
                        + quote_ccy.upper()
                        + "-"
                        + "SWAP"
                        + "-"
                        + "future"
                    )
                elif exch == "huobi":
                    mkts_list.append(
                        exch
                        + "-"
                        + ticker.upper()
                        + "-"
                        + quote_ccy.upper()
                        + "_"
                        + "SWAP"
                        + "-"
                        + "future"
                    )
                elif exch == "hitbtc":
                    mkts_list.append(
                        exch
                        + "-"
                        + ticker.upper()
                        + quote_ccy.upper()
                        + "_"
                        + "PERP"
                        + "-"
                        + "future"
                    )
        # start date
        if self.data_req.start_date is not None:
            start_date = self.data_req.start_date.strftime('%Y-%m-%d')
        else:
            start_date = None
        # end date
        if self.data_req.end_date is not None:
            end_date = self.data_req.end_date.strftime('%Y-%m-%d')
        else:
            end_date = None

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": exch,
            "ctys": None,
            "mkt_type": self.data_req.mkt_type,
            "mkts": mkts_list,
            "start_date": start_date,
            "end_date": end_date,
            "fields": fields,
            "tz": tz,
            "inst": inst,
            "cat": 'crypto',
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_glassnode(self) -> Dict[str, Union[list, str, int, float, None]]:
        """
        Convert tickers from CryptoDataPy to Glassnode format.
        """
        # convert tickers
        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            tickers = self.data_req.tickers
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            if self.data_req.freq is None:
                freq = "24h"
            elif self.data_req.freq[-3:] == "min":
                freq = "10m"
            elif self.data_req.freq[-1] == "h":
                freq = "1h"
            elif self.data_req.freq == "d":
                freq = "24h"
            elif self.data_req.freq == "w":
                freq = "1w"
            elif self.data_req.freq == "m":
                freq = "1month"
            else:
                freq = "24h"
        # convert quote ccy
        if self.data_req.quote_ccy is None:
            quote_ccy = "USD"
        else:
            quote_ccy = self.data_req.quote_ccy.upper()
        # convert exch
        exch = self.data_req.exch
        # start date
        if self.data_req.start_date is None:
            start_date = round(pd.Timestamp("2009-01-03 00:00:00").timestamp())
        else:
            start_date = round(pd.Timestamp(self.data_req.start_date).timestamp())
        # end date
        if self.data_req.end_date is None:
            end_date = self.data_req.end_date
        else:
            end_date = round(pd.Timestamp(self.data_req.end_date).timestamp())
        # convert fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='glassnode')
        # convert tz
        if self.data_req.tz is None:
            tz = "UTC"
        else:
            tz = self.data_req.tz
        # convert inst
        if self.data_req.inst is None:
            inst = "purpose"
        else:
            inst = self.data_req.inst.lower()

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": exch,
            "ctys": None,
            "mkt_type": self.data_req.mkt_type,
            "mkts": None,
            "start_date": start_date,
            "end_date": end_date,
            "fields": fields,
            "tz": tz,
            "inst": inst,
            "cat": 'crypto',
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_tiingo(self) -> Dict[str, Union[list, str, int, float, datetime, None]]:
        """
        Convert tickers from CryptoDataPy to Tiingo format.
        """
        # convert tickers
        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            tickers = [ticker.lower() for ticker in self.data_req.tickers]
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            if self.data_req.freq is None:
                freq = "1day"
            elif self.data_req.freq[-3:] == "min":
                freq = self.data_req.freq
            elif self.data_req.freq[-1] == "h":
                freq = "1hour"
            else:
                freq = "1day"
        # convert quote ccy
        if self.data_req.quote_ccy is None:
            quote_ccy = "usd"
        else:
            quote_ccy = self.data_req.quote_ccy.lower()
        # convert exch
        if (
            self.data_req.exch is None
            and self.data_req.cat == "eqty"
            and self.data_req.freq
            in ["1min", "5min", "10min", "15min", "30min", "1h", "2h", "4h", "8h"]
        ):
            exch = "iex"
        else:
            exch = self.data_req.exch
        # convert tickers to mkts
        mkts_list = []
        if self.data_req.source_tickers is not None:
            mkts_list = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            if self.data_req.cat == "fx":
                fx_list = self.convert_fx_tickers(quote_ccy=quote_ccy)
                mkts_list = [ticker.lower().replace("/", "") for ticker in fx_list]
            elif self.data_req.cat == "crypto":
                mkts_list = [
                    ticker.lower() + quote_ccy for ticker in self.data_req.tickers
                ]
        # convert start date
        if self.data_req.start_date is None and self.data_req.cat == 'crypto':
            start_date = datetime(2010, 1, 1, 0, 0)
        else:
            start_date = self.data_req.start_date
        # convert end date
        if self.data_req.end_date is None:
            end_date = pd.Timestamp.utcnow()
        else:
            end_date = self.data_req.end_date
        # convert fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='tiingo')
        # tz
        if self.data_req.cat == 'eqty' or self.data_req.cat == 'fx':
            tz = "America/New_York"
        else:
            tz = "UTC"

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": exch,
            "ctys": None,
            "mkt_type": self.data_req.mkt_type,
            "mkts": mkts_list,
            "start_date": start_date,
            "end_date": end_date,
            "fields": fields,
            "tz": tz,
            "inst": None,
            "cat": self.data_req.cat,
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_ccxt(self) -> DataRequest:
        """
        Convert tickers from CryptoDataPy to CCXT format.
        """
        # tickers
        if self.data_req.source_tickers is None:
            self.data_req.source_tickers = [ticker.upper() for ticker in self.data_req.tickers]

        # freq
        if self.data_req.source_freq is None:
            if self.data_req.freq is None:
                self.data_req.source_freq = "1d"
            elif self.data_req.freq == "tick":
                self.data_req.source_freq = "tick"
            elif self.data_req.freq[-3:] == "min":
                self.data_req.source_freq = self.data_req.freq.replace("min", "m")
            elif self.data_req.freq[-1] == "h":
                self.data_req.source_freq = self.data_req.freq
            elif self.data_req.freq == "w":
                self.data_req.source_freq = "1w"
            elif self.data_req.freq == "m":
                self.data_req.source_freq = "1M"
            elif self.data_req.freq[-1] == "m":
                self.data_req.source_freq = self.data_req.freq.replace("m", "M")
            elif self.data_req.freq == "q":
                self.data_req.source_freq = "1q"
            elif self.data_req.freq == "y":
                self.data_req.source_freq = "1y"
            else:
                self.data_req.source_freq = "1d"

        # quote ccy
        if self.data_req.quote_ccy is None:
            self.data_req.quote_ccy = "USDT"
        else:
            self.data_req.quote_ccy = self.data_req.quote_ccy.upper()

        # exch
        if self.data_req.mkt_type == "perpetual_future" and (
            self.data_req.exch is None or self.data_req.exch == "binance"
        ):
            self.data_req.exch = "binanceusdm"
        elif self.data_req.exch is None:
            self.data_req.exch = "binance"
        elif (
            self.data_req.exch == "kucoin"
            and self.data_req.mkt_type == "perpetual_future"
        ):
            self.data_req.exch = "kucoinfutures"
        elif (
            self.data_req.exch == "huobi"
            and self.data_req.mkt_type == "perpetual_future"
        ):
            self.data_req.exch = "huobipro"
        elif (
            self.data_req.exch == "bitfinex"
            and self.data_req.mkt_type == "perpetual_future"
        ):
            self.data_req.exch = "bitfinex2"
        elif (
            self.data_req.exch == "mexc"
            and self.data_req.mkt_type == "perpetual_future"
        ):
            self.data_req.exch = "mexc3"
        else:
            self.data_req.exch = self.data_req.exch.lower()

        # markets
        if self.data_req.source_markets is None:
            if self.data_req.mkt_type == "spot":
                self.data_req.source_markets = [ticker + "/" + self.data_req.quote_ccy
                                                for ticker in self.data_req.source_tickers]
            elif self.data_req.mkt_type == "perpetual_future":
                self.data_req.source_markets = [ticker + "/" + self.data_req.quote_ccy + ":" + self.data_req.quote_ccy
                        for ticker in self.data_req.source_tickers]
        else:
            self.data_req.source_tickers = [market.split("/")[0] for market in self.data_req.source_markets]

        # start date
        if self.data_req.start_date is None:
            self.data_req.source_start_date = round(
                pd.Timestamp("2010-01-01 00:00:00").timestamp() * 1e3
            )
        else:
            self.data_req.source_start_date = round(
                pd.Timestamp(self.data_req.start_date).timestamp() * 1e3
            )

        # end date
        if self.data_req.end_date is None:
            self.data_req.source_end_date = round(pd.Timestamp.utcnow().timestamp() * 1e3)
        else:
            self.data_req.source_end_date = round(pd.Timestamp(self.data_req.end_date).timestamp() * 1e3)

        # fields
        if self.data_req.source_fields is None:
            self.data_req.source_fields = self.convert_fields(data_source='ccxt')

        # tz
        if self.data_req.tz is None:
            self.data_req.tz = "UTC"

        return self.data_req

    def to_dbnomics(self) -> Dict[str, Union[list, str, int, float, None]]:
        """
        Convert tickers from CryptoDataPy to DBnomics format.
        """
        # convert tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df, tickers = pd.read_csv(tickers_path, index_col=0, encoding="latin1"), []

        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            for ticker in self.data_req.tickers:
                try:
                    tickers.append(tickers_df.loc[ticker, "dbnomics_id"])
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for DBnomics source. Check tickers in"
                        f" data catalog and try again."
                    )
                    self.data_req.tickers.remove(ticker)
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            freq = self.data_req.freq
        # quote ccy
        quote_ccy = self.data_req.quote_ccy
        # fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='dbnomics')

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": self.data_req.exch,
            "ctys": None,
            "mkt_type": None,
            "mkts": None,
            "start_date": self.data_req.start_date,
            "end_date": self.data_req.end_date,
            "fields": fields,
            "tz": self.data_req.tz,
            "inst": None,
            "cat": self.data_req.cat,
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_investpy(self) -> Dict[str, Union[list, str, int, float, None]]:
        """
        Convert tickers from CryptoDataPy to InvestPy format.
        """
        # convert tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df, tickers = pd.read_csv(tickers_path, index_col=0, encoding="latin1"), []

        if self.data_req.source_tickers is not None:
            tickers = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        else:
            for ticker in self.data_req.tickers:
                try:
                    tickers.append(tickers_df.loc[ticker, "investpy_id"])
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for InvestPy data source. Check tickers in "
                        f"data catalog and try again."
                    )
                    self.data_req.tickers.remove(ticker)
        # convert freq
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            freq = self.data_req.freq
        # convert quote ccy
        if self.data_req.quote_ccy is None:
            quote_ccy = "USD"
        else:
            quote_ccy = self.data_req.quote_ccy.upper()
        # convert ctys
        ctys_list = []
        for ticker in self.data_req.tickers:
            try:
                ctys_list.append(tickers_df.loc[ticker, "country_name"].lower())
            except KeyError:
                logging.warning(
                    f"{ticker} not found for {self.data_req.source} source. Check tickers in "
                    f"data catalog and try again."
                )
        # convert tickers to markets
        mkts_list = []
        if self.data_req.source_tickers is not None:
            mkts_list = self.data_req.source_tickers
            self.data_req.tickers = self.data_req.source_tickers
        # convert start date
        if self.data_req.start_date is None:
            start_date = pd.Timestamp("1970-01-01").strftime("%d/%m/%Y")
        else:
            start_date = pd.Timestamp(self.data_req.start_date).strftime("%d/%m/%Y")
        # convert end date
        if self.data_req.end_date is None:
            end_date = pd.Timestamp.utcnow().strftime("%d/%m/%Y")
        else:
            end_date = pd.Timestamp(self.data_req.end_date).strftime("%d/%m/%Y")
        # convert fields
        if self.data_req.source_fields is not None:
            fields = self.data_req.source_fields
            self.data_req.fields = self.data_req.source_fields
        else:
            fields = self.convert_fields(data_source='investpy')

        return {
            "tickers": tickers,
            "freq": freq,
            "quote_ccy": quote_ccy,
            "exch": self.data_req.exch,
            "ctys": ctys_list,
            "mkt_type": self.data_req.mkt_type,
            "mkts": mkts_list,
            "start_date": start_date,
            "end_date": end_date,
            "fields": fields,
            "tz": self.data_req.tz,
            "inst": None,
            "cat": self.data_req.cat,
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def to_fred(self) -> Dict[str, Union[list, str, int, float, datetime, None]]:
        """
        Convert tickers from CryptoDataPy to Fred format.
        """
        # convert tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df = pd.read_csv(tickers_path, index_col=0, encoding="latin1")

        if self.data_req.source_tickers is None:
            self.data_req.source_tickers = []
            for ticker in self.data_req.tickers:
                try:
                    self.data_req.source_tickers.append(tickers_df.loc[ticker, "fred_id"])
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for Fred source. Check tickers in"
                        f" data catalog and try again."
                    )

        # freq
        if self.data_req.source_freq is None:
            self.data_req.source_freq = self.data_req.freq

        # start date
        if self.data_req.source_start_date is None:
            self.data_req.source_start_date = pd.Timestamp('1920-01-01')
        else:
            self.data_req.source_start_date = self.data_req.start_date

        # end date
        if self.data_req.end_date is None:
            self.data_req.source_end_date = pd.Timestamp.utcnow().tz_localize(None)
        else:
            self.data_req.source_end_date = self.data_req.end_date

        # fields
        if self.data_req.source_fields is None:
            self.data_req.source_fields = self.convert_fields(data_source='fred')

        # tz
        if self.data_req.tz is None:
            self.data_req.tz = "America/New_York"

        return self.data_req

    def to_wb(self) -> Dict[str, Union[list, str, int, float, datetime, None]]:
        """
        Convert tickers from CryptoDataPy to Yahoo Finance format.
        """
        # tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df = pd.read_csv(tickers_path, index_col=0, encoding="latin1")

        if self.data_req.source_tickers is None:
            self.data_req.source_tickers = []
            for ticker in self.data_req.tickers:
                try:
                    self.data_req.source_tickers.append(tickers_df.loc[ticker, "wb_id"])
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for World Bank source. Check tickers in"
                        f" data catalog and try again."
                    )
        # drop dupes
        self.data_req.source_tickers = list(set(self.data_req.source_tickers))

        # freq
        if self.data_req.source_freq is None:
            self.data_req.source_freq = self.data_req.freq

        # convert quote ccy
        if self.data_req.quote_ccy is None:
            self.data_req.quote_ccy = "USD"
        else:
            self.data_req.quote_ccy = self.data_req.quote_ccy.upper()

        # ctys
        ctys_list = []
        if self.data_req.cat == "macro":
            for ticker in self.data_req.tickers:
                try:
                    ctys_list.append(tickers_df.loc[ticker, "country_id_3"].upper())
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for {self.data_req.source} source. Check tickers in "
                        f"data catalog and try again."
                    )
        self.data_req.ctys = list(set(ctys_list))

        # start date
        if self.data_req.start_date is None:
            self.data_req.source_start_date = 1920
        else:
            self.data_req.source_start_date = int(self.data_req.start_date.year)

        # end date
        if self.data_req.end_date is None:
            self.data_req.source_end_date = pd.Timestamp.utcnow().year
        else:
            self.data_req.source_end_date = int(self.data_req.end_date.year)

        # fields
        if self.data_req.source_fields is None:
            self.data_req.source_fields = self.convert_fields(data_source='wb')

        return self.data_req

    def to_yahoo(self) -> DataRequest:
        """
        Convert tickers from CryptoDataPy to Yahoo Finance format.
        """
        # tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df = pd.read_csv(tickers_path, index_col=0, encoding="latin1")

        if self.data_req.source_tickers is None:
            if self.data_req.cat == 'eqty':
                self.data_req.source_tickers = [ticker.upper() for ticker in self.data_req.tickers]
                self.data_req.tickers = self.data_req.source_tickers
            else:
                self.data_req.source_tickers = []
                if self.data_req.cat == 'fx':
                    self.data_req.tickers = [ticker.upper() for ticker in self.data_req.tickers]
                for ticker in self.data_req.tickers:
                    try:
                        self.data_req.source_tickers.append(tickers_df.loc[ticker, "yahoo_id"])
                    except KeyError:
                        logging.warning(
                            f"{ticker} not found for Yahoo Finance data source. Check tickers in"
                            f" data catalog and try again."
                        )

        # freq
        if self.data_req.source_freq is None:
            self.data_req.source_freq = self.data_req.freq

        # start date
        if self.data_req.start_date is None:
            self.data_req.source_start_date = '1920-01-01'
        else:
            self.data_req.source_start_date = self.data_req.start_date

        # end date
        if self.data_req.end_date is None:
            self.data_req.source_end_date = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
        else:
            self.data_req.source_end_date = self.data_req.end_date

        # fields
        if self.data_req.source_fields is None:
            self.data_req.source_fields = self.convert_fields(data_source='yahoo')

        # tz
        if self.data_req.tz is None:
            self.data_req.tz = "America/New_York"

        return self.data_req

    def to_famafrench(self) -> DataRequest:
        """
        Convert tickers from CryptoDataPy to Fama-French format.
        """
        # tickers
        with resources.path("cryptodatapy.conf", "tickers.csv") as f:
            tickers_path = f
        tickers_df = pd.read_csv(tickers_path, index_col=0, encoding="latin1")

        if self.data_req.source_tickers is None:
            self.data_req.source_tickers = []
            for ticker in self.data_req.tickers:
                try:
                    self.data_req.source_tickers.append(tickers_df.loc[ticker, "famafrench_id"])
                except KeyError:
                    logging.warning(
                        f"{ticker} not found for Fama-French source. Check tickers in"
                        f" data catalog and try again."
                    )

        # freq
        if self.data_req.source_freq is None:
            self.data_req.source_freq = self.data_req.freq

        # start date
        if self.data_req.start_date is None:
            self.data_req.source_start_date = datetime(1920, 1, 1)
        else:
            self.data_req.source_start_date = self.data_req.start_date

        # end date
        if self.data_req.end_date is None:
            self.data_req.source_end_date = datetime.now()
        else:
            self.data_req.source_end_date = self.data_req.end_date

        return self.data_req

    def to_aqr(self) -> Dict[str, Union[list, str, int, dict, float, datetime, None]]:
        """
        Convert tickers from CryptoDataPy to AQR format.
        """
        # convert tickers
        all_tickers_dict = {
            'The-Devil-in-HMLs-Details-Factors-': {
                'US_Eqty_Val': 'HML FF',
                'US_Eqty_Size': 'SMB',
                'US_Eqty_Mom': 'UMD',
                'WL_Eqty_Val': 'HML FF',
                'WL_Eqty_Size': 'SMB',
                'WL_Eqty_Mom': 'UMD',
                'US_Rates_1M_RF': 'RF',
            },
            'Quality-Minus-Junk-Factors-': {
                'US_Eqty_Qual': 'QMJ Factors',
                'WL_Eqty_Qual': 'QMJ Factors'
            },
            'Betting-Against-Beta-Equity-Factors-': {
                'US_Eqty_Beta': 'BAB Factors',
                'WL_Eqty_Beta': 'BAB Factors'
            },
            'Century-of-Factor-Premia-': {
                'WL_Eqty_Fut_Val': 'Century of Factor Premia',
                'WL_Eqty_Fut_Mom': 'Century of Factor Premia',
                'WL_Eqty_Fut_Carry': 'Century of Factor Premia',
                'WL_Eqty_Fut_Beta': 'Century of Factor Premia',
                'WL_Rates_Val': 'Century of Factor Premia',
                'WL_Rates_Mom': 'Century of Factor Premia',
                'WL_Rates_Carry': 'Century of Factor Premia',
                'WL_Rates_Beta': 'Century of Factor Premia',
                'WL_Cmdty_Val': 'Century of Factor Premia',
                'WL_Cmdty_Mom': 'Century of Factor Premia',
                'WL_Cmdty_Carry': 'Century of Factor Premia',
                'WL_FX_Val': 'Century of Factor Premia',
                'WL_FX_Mom': 'Century of Factor Premia',
                'WL_FX_Carry': 'Century of Factor Premia'
            },
            'Time-Series-Momentum-Factors-': {
                'WL_Eqty_Fut_Mom_TS': 'TSMOM Factors',
                'WL_Rates_Mom_TS': 'TSMOM Factors',
                'WL_Comdty_Mom_TS': 'TSMOM Factors',
                'WL_FX_Mom_TS': 'TSMOM Factors'
            },
            'Commodities-for-the-Long-Run-Index-Level-Data-': {
                'Cmdty_ER': 'Commodities for the Long Run'
            },
            'Credit-Risk-Premium-Preliminary-Paper-Data': {
                'US_Credit_ER': 'Credit Risk Premium'
            }
        }
        # tickers dict
        tickers_dict = {}
        for ticker in self.data_req.tickers:
            for k, v in all_tickers_dict.items():
                if ticker in v:
                    tickers_dict[ticker] = (k, all_tickers_dict[k][ticker])
        # convert freq
        daily_freqs_list = ['The-Devil-in-HMLs-Details-Factors-', 'Quality-Minus-Junk-Factors-',
                            'Betting-Against-Beta-Equity-Factors-']
        if self.data_req.source_freq is not None:
            freq = self.data_req.source_freq
            self.data_req.freq = self.data_req.source_freq
        else:
            if all([file[0] in daily_freqs_list for file in tickers_dict.values()]) and \
               (self.data_req.freq == 'd' or self.data_req.freq == 'w'):
                freq = 'Daily'
            else:
                freq = 'Monthly'
                self.data_req.freq = 'm'

        return {
            "tickers": tickers_dict,
            "freq": freq,
            "quote_ccy": self.data_req.quote_ccy,
            "exch": self.data_req.exch,
            "ctys": None,
            "mkt_type": self.data_req.mkt_type,
            "mkts": None,
            "start_date": self.data_req.start_date,
            "end_date": self.data_req.end_date,
            "fields": self.data_req.fields,
            "tz": self.data_req.tz,
            "inst": None,
            "cat": self.data_req.cat,
            "trials": self.data_req.trials,
            "pause": self.data_req.pause,
            "source_tickers": self.data_req.source_tickers,
            "source_freq": self.data_req.source_freq,
            "source_fields": self.data_req.source_fields,
        }

    def convert_fx_tickers(self, quote_ccy: str) -> List[str]:
        """
        Converts base and quote currency tickers to fx pairs following fx quoting convention.

        Parameters
        ---------
        quote_ccy: str
            Quote currency

        Returns
        -------
        quote_ccy: str
            Quote currency.

        """
        mkts = []  # fx pairs list
        # fx groups
        base_ccys = ["EUR", "GBP", "AUD", "NZD"]
        # g10_fx = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'NOK', 'SEK']
        # dm_fx = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'NOK', 'SEK', 'SGD', 'ILS', 'HKD', ]
        # em_fx = ['ARS', 'BRL', 'CHN', 'CLP', 'CNY', 'COP', 'IDR', 'INR', 'KRW', 'MYR', 'MXN', 'PEN', 'PHP', 'RUB',
        #          'TRY', 'TWD', 'ZAR']

        for ticker in self.data_req.tickers:
            if ticker.upper() in base_ccys and quote_ccy.upper() == "USD":
                mkts.append(ticker.upper() + "/" + quote_ccy.upper())
            elif quote_ccy.upper() == "USD":
                mkts.append(quote_ccy.upper() + "/" + ticker.upper())
            else:
                mkts.append(ticker.upper() + "/" + quote_ccy.upper())

        return mkts

    def convert_fields(self, data_source: str) -> List[str]:
        """
        Converts fields from CryptoDataPy to data source format.

        Parameters
        ---------
        data_source: str
            Name of data source for fields conversions.

        Returns
        -------
        fields_list: list
            List of fields in data source format.

        """
        # get fields
        with resources.path("cryptodatapy.conf", "fields.csv") as f:
            fields_dict_path = f
        fields_df, fields_list = (
            pd.read_csv(fields_dict_path, index_col=0, encoding="latin1"),
            [],
        )

        # when source fields already provided in data req
        if self.data_req.source_fields is not None:
            fields_list = self.data_req.source_fields

        # convert to source format
        else:
            for field in self.data_req.fields:
                try:
                    fields_list.append(fields_df.loc[field, data_source + "_id"])
                except KeyError as e:
                    logging.warning(e)
                    logging.warning(
                        f"Id for {field} could not be found in the data catalog."
                        f" Try using source field ids."
                    )

        return fields_list
