# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
# Pruned to only keep India (NSE) market support
from .stock.request_stock_price_india_nse import request_nse_india_quote
from .stock.request_constants import *

class BaseAPI(object):
    """docstring for ClassName"""
    def __init__(self, configs):
        self.configs = configs
        
    def api(self, kwargs):
        """
            Args:
                kwargs: dict, 
            Return:
                res_dict: dict
        """
        # input
        symbol_list = kwargs["symbol_list"]
        market = kwargs["market"]
        # output
        res_dict={}
        return res_dict

class FinanceDataFetchParallelAPI(BaseAPI):
    """
        Args:
            kwargs key value params

            symbol_list: list of str, e.g. ["TSLA", "MSFT", "GOOG"]
            market: str, e.g. US
            sub_market: str, NYSE, NASDAQ, etc.
            data_source_list: list of websites for data sources, e.g. hkex.com, zacks.com, morningstar.com
            token: API calling token
        Output:
            res_dict_list: list of dict
    """
    def __init__(self, configs):
        super(FinanceDataFetchParallelAPI, self).__init__(configs)
        self.name = API_NAME_FINANCE_DATA_PARALLEL

    def api(self, kwargs):
        return request_stock_quote_parrallel_base(kwargs)

    def batch_api(self, kwargs_list):
        """
            kwargs_list: list of dict: kwargs 
        """
        res_dict_list ={}

        try:
            res_dict_list = request_stock_quote_parallel(kwargs_list)
        except Exception as e:
            print (e)
        return res_dict_list


def request_stock_quote_parrallel_base(kwargs):
    """ 
        Args:
            symbol_list
            market
            sub_market
            token
        Output:
            list of dict    
    """
    try:
        # required fields
        symbol_list = kwargs[KEY_SYMBOL_LIST] if KEY_SYMBOL_LIST in kwargs else None 
        market = kwargs[KEY_MARKET] if KEY_MARKET in kwargs else None 
        if (symbol_list is None or market is None):
            return {}

        # optional fields
        sub_market = kwargs[KEY_SUB_MARKET] if KEY_SUB_MARKET in kwargs else None 
        data_source_list = kwargs[KEY_DATA_SOURCE_LIST] if KEY_DATA_SOURCE_LIST in kwargs else None 
        token = kwargs[KEY_TOKEN] if KEY_TOKEN in kwargs else None 

        if market != STOCK_MARKET_NSE_INDIA:
            raise ValueError(f"Unsupported market '{market}'. Only NSE_INDIA is available in the pruned package.")
        return request_nse_india_quote(symbol_list, sub_market, kwargs)
    except Exception:
        raise

def request_stock_quote_parallel(kwargs_list):
    """
        Parallel Fetch data from multiple Market, group by AI by market
        
        Args:
            kwargs_list: list of dict 

            token: if required by API provideer
            symbol_market_list: [ (symbol, market, submarket) ], e,g, [("111111", "CN", ""), ("888888", "HK", ""), ("MSFT","", "NASDAQ")]
            data_source_list: list of data source to fetch data
        Return:
            list of json, [{"symbol":"BABA", "symbol_name":"XXX"}]
    """
    results = []
    if not kwargs_list:
        return results
    try:
        with ThreadPoolExecutor(max_workers=len(kwargs_list)) as executor:
            start_time = time.time()
            tasks = [executor.submit(request_stock_quote_parrallel_base, kwargs) for kwargs in kwargs_list]
            for future in as_completed(tasks):
                if future is not None:
                    results.extend(future.result())
            end_time = time.time()
            total_time = end_time - start_time
            print ("DEBUG: request_stock_quote_parrallel end, total time %d, task cnt %d,future success cnt %d" % (total_time, len(tasks), len(results)))
    except Exception as e:
        print ("DEBUG: request_stock_quote_parallel failed...")
        print (e)
    return results
