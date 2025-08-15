#coding=utf-8
#!/usr/bin/python

## Stock Market (only NSE India retained)
STOCK_MARKET_NSE_INDIA = "NSE_INDIA"

## API NAME LIST
API_NAME_FINANCE_DATA_PARALLEL = "finance_data_parallel"

## API Input Dict Keys
KEY_TOKEN = "token"
KEY_SYMBOL_LIST = "symbol_list"
KEY_MARKET = "market"
KEY_SUB_MARKET = "sub_market"
KEY_DATA_SOURCE_LIST = "data_source_list"

## API Output Dict Keys
KEY_SYMBOL = "symbol"
KEY_TIMESTAMP = "timestamp"
KEY_UPDATE_TIME = "update_time"
KEY_PE_RATIO = "pe_ratio"
KEY_AVG_PRICE = "avg_price"
KEY_CHANGE = "change"
KEY_CHANGE_PERCENT = "change_percent"
KEY_HIGH_PRICE = "high"
KEY_LOW_PRICE = "low"
KEY_PREVIOUS_CLOSE= "previous_close"
KEY_LAST_PRICE = "last_price"
KEY_ADVICE = "advice"
KEY_DATA_SOURCE = "data_source"
KEY_SOURCE_URL = "source_url"
KEY_SOURCE = "source"
KEY_SYMBOL_AND_NAME = "symbol_and_name"
KEY_SYMBOL_NAME_DISPLAY = "symbol_name_display"
KEY_MARKET_CAP = "market_capitalization"
KEY_SYMBOL_HK = "symbol_hk"
KEY_SYMBOL_NAME_HK = "symbol_name_hk"
KEY_COMPANY_NAME = "company_name"
KEY_INDUSTRY = "industry"

## DATA SOURCE
DATA_SOURCE_MONEY_CONTROL = "moneycontrol.com"

## DATA SOURCE RESPONSE
# Pruned response source templates

## URL
# Removed other market URLs

## Currency (only INR)
UNIT_INR = "INR"
UNIT_INR_CR = "Cr."

### India Stock Market 

INDIA_NSE_STOCK_URL_MONEY_CONTROL = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9"
INDIA_NSE_STOCK_URL_MONEY_CONTROL_BASE = "https://www.moneycontrol.com"


MINUS_SIGN = "-"

# Public re-export list (explicit) to keep package surface tidy
__all__ = [
	'STOCK_MARKET_NSE_INDIA', 'API_NAME_FINANCE_DATA_PARALLEL',
	'KEY_TOKEN','KEY_SYMBOL_LIST','KEY_MARKET','KEY_SUB_MARKET','KEY_DATA_SOURCE_LIST',
	'KEY_SYMBOL','KEY_TIMESTAMP','KEY_UPDATE_TIME','KEY_PE_RATIO','KEY_AVG_PRICE','KEY_CHANGE','KEY_CHANGE_PERCENT',
	'KEY_HIGH_PRICE','KEY_LOW_PRICE','KEY_PREVIOUS_CLOSE','KEY_LAST_PRICE','KEY_ADVICE','KEY_DATA_SOURCE','KEY_SOURCE_URL','KEY_SOURCE',
	'KEY_SYMBOL_AND_NAME','KEY_SYMBOL_NAME_DISPLAY','KEY_MARKET_CAP','KEY_SYMBOL_HK','KEY_SYMBOL_NAME_HK','KEY_COMPANY_NAME','KEY_INDUSTRY',
	'DATA_SOURCE_MONEY_CONTROL','UNIT_INR','UNIT_INR_CR','INDIA_NSE_STOCK_URL_MONEY_CONTROL','INDIA_NSE_STOCK_URL_MONEY_CONTROL_BASE','MINUS_SIGN'
]
