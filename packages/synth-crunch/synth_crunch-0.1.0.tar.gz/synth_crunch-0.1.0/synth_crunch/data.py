import logging
from datetime import datetime, timezone

import pandas
import requests

from .interface import Asset

logger = logging.getLogger()


class PriceUnavailableError(ValueError):
    """
    Raised when the price provider cannot fetch the price for an asset.
    """


class PythHermes:

    # from https://docs.pyth.network/price-feeds/price-feeds
    _LATEST_PRICE_URL = "https://hermes.pyth.network/api/latest_price_feeds"
    _ASSET_TO_TOKEN_ID_MAP: dict[Asset, str] = {
        "BTC": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
        "ETH": "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
        "XAU": "765d2ba906dbc32ca17cc11f5310a89e9ee1f6420508c63861f2f8ba4ee34bb2",
        "SOL": "ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    }

    # from https://docs.pyth.network/price-feeds/price-feeds
    _HISTORY_URL = "https://benchmarks.pyth.network/v1/shims/tradingview/history"
    _ASSET_TO_SYMBOL_MAP: dict[Asset, str] = {
        "BTC": "Crypto.BTC/USD",
        "ETH": "Crypto.ETH/USD",
        "XAU": "Metal.XAU/USD",
        "SOL": "Crypto.SOL/USD",
    }

    # TODO should likely not be a class variable, a clear function is also required
    _HISTORY_CACHE: dict[tuple, pandas.Series] = {}

    # # from https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/validator/price_data_provider.py#L39
    def get_price_history(
        self,
        *,
        asset: Asset,
        from_: datetime,
        to: datetime,
        timeout=30,
    ) -> pandas.Series:
        cached = self._HISTORY_CACHE.get((asset, from_, to))
        if cached is not None:
            logger.debug(f"using cached price history for {asset} from {from_} to {to}")
            return cached.copy(deep=True)

        query = {
            "symbol": self._ASSET_TO_SYMBOL_MAP[asset],
            "resolution": 1,
            "from": self._unix_timestamp(from_),
            "to": self._unix_timestamp(to),
        }

        try:
            response = requests.get(
                self._HISTORY_URL,
                timeout=timeout,
                params=query,
            )

            response.raise_for_status()

            root = response.json()
            if root.get("s") != "ok":
                raise ValueError(f"api didn't returned ok: {root}")
        except requests.RequestException as error:
            raise PriceUnavailableError(f"could not get last price for {asset}: {error}") from error

        dataframe = pandas.DataFrame(
            {
                "timestamp": root["t"],
                "price": root["c"],
            },
        )

        dataframe["timestamp"] = pandas.to_datetime(dataframe["timestamp"], unit="s", utc=True)
        dataframe.set_index("timestamp", inplace=True)

        prices = dataframe["price"]
        self._HISTORY_CACHE[(asset, from_, to)] = prices.copy(deep=True)

        return prices

    def get_last_price(
        self,
        *,
        asset: Asset,
        timeout=30,
    ) -> float:
        query = {
            "ids[]": self._ASSET_TO_TOKEN_ID_MAP[asset],
        }

        try:
            response = requests.get(
                self._LATEST_PRICE_URL,
                timeout=timeout,
                params=query,
            )

            response.raise_for_status()

            root = response.json()
            if len(root) != 1:
                raise ValueError(f"only one entry must be received: {root}")
        except Exception as error:
            raise PriceUnavailableError(f"could not get last price for {asset}: {error}") from error

        entry = root[0]
        price = int(entry["price"]["price"])
        expo = int(entry["price"]["expo"])

        return price * (10**expo)

    def _unix_timestamp(self, object: datetime) -> int:
        object = object.replace(tzinfo=timezone.utc)

        return int(object.timestamp())


shared_pyth_hermes = PythHermes()
