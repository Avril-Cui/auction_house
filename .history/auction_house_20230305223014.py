"""
Simple Auction House Strategy Model
Rule1 [Moving Average] -> direction:
	When shorter-term MA crosses above the long-term MA: buy, return -1
	When shorter-term MA crosses below the long-term MA: shell, return +1
Rule2 [Surplus] -> trade the order with maximum surplus:
	Buy: highest sell order, return 1, 0.8, 0.6, 0.4, 0.2
	Sell: lowest buy order, return -1, -0.8, -0.6, -0.4, -0.2
"""

from collections import OrderedDict
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
yf.pdr_override()


class BotEvaluatorSample:
	def __init__(
			self,
			price_info: list,
			current_price: float,
			ordered_book: OrderedDict,
			stock_name: str,
			time_stamp: float,
	):
		price_info: list = price_info
		current_price: float = current_price
		ordered_book: dict = ordered_book
		stock_name: str = stock_name
		time_stamp: float = time_stamp
		st_moving_avg_period: int = 15
		lt_moving_avg_period: int = 30

	def stg_ma(self):
		st_moving_avg = self.price_info.rolling(
			window=self.st_moving_avg_period).mean().to_list()
		lt_moving_avg = self.price_info.rolling(
			window=self.lt_moving_avg_period).mean().to_list()
		if st_moving_avg[self.time_stamp] > lt_moving_avg[self.time_stamp] and st_moving_avg[self.time_stamp-1] <= lt_moving_avg[self.time_stamp-1]:
			return -1
		elif st_moving_avg[self.time_stamp] < lt_moving_avg[self.time_stamp] and st_moving_avg[self.time_stamp-1] >= lt_moving_avg[self.time_stamp-1]:
			return 1
		else:
			return 0

	def stg_surplus(self):
		return "HI"