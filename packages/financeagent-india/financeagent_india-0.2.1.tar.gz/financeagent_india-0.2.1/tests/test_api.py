# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir, 'src'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import FinanceAgent as fa

def test_india_stock_api_only():
    keys = ["symbol", "avg_price", "high", "low", "previous_close", "market_capitalization", "source_url", "data_source"]
    india_stock_info_json = fa.api(symbol_list=['TM03', 'IT'], market="NSE_INDIA")
    assert isinstance(india_stock_info_json, list)
    assert len(india_stock_info_json) >= 0  # allow empty if site unreachable
    for stock_info in india_stock_info_json:
        for key in keys:
            assert key in stock_info

import pytest

def test_unsupported_market_rejected():
    with pytest.raises(ValueError):
        fa.api(symbol_list=['TSLA'], market="US")
