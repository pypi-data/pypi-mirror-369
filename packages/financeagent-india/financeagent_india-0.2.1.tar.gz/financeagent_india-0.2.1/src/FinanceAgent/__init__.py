# -*- coding: utf-8 -*-
# @Time    : 2024/06/27
# @Author  : Arush

from .base import FinanceDataFetchParallelAPI
from .stock.request_constants import STOCK_MARKET_NSE_INDIA

SUPPORTED_MARKETS = [STOCK_MARKET_NSE_INDIA]

def api(**kwargs):
    """Fetch NSE India quotes.

    Required kwargs:
      symbol_list: list[str]
      market: 'NSE_INDIA' (synonyms NSE / INDIA accepted)
    """
    market = kwargs.get('market')
    if market:
        m = str(market).strip().upper().replace('-', '_')
        if m in {"INDIA", "NSE", "NSEINDIA", "NSE_INDIA"}:
            kwargs['market'] = STOCK_MARKET_NSE_INDIA
    api_cls = FinanceDataFetchParallelAPI(None)
    return api_cls.api(kwargs)

def markets():
    return {"supported": SUPPORTED_MARKETS}

__all__ = ["api", "markets", "SUPPORTED_MARKETS", "STOCK_MARKET_NSE_INDIA"]
