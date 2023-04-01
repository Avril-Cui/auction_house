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
			price_info: pd.DataFrame,
			current_price: float,
			ordered_book: OrderedDict,
			time_stamp: float
	):
		"""
			OrderedDict(((price, share), ("c", '3'), ("b", "2")))
		"""
		self.price_info: pd.DataFrame = price_info
		self.current_price: float = current_price
		self.ordered_book: dict = ordered_book
		self.time_stamp: float = time_stamp
		self.st_moving_avg_period: int = 15
		self.lt_moving_avg_period: int = 30

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

	def stg_surplus(self, index):
		return 0.2 * index
	
	def evaluator(self):
		price = 0
		share = 0
		score = 0
		coefficient = self.stg_ma()
		if coefficient == -1:
			for price_tmp in self.ordered_book:
				if self.ordered_book[price_tmp] < 0:
					index = list(self.ordered_book.keys()).index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = self.ordered_book[price_tmp]
						price = price_tmp
		elif coefficient == 1:
			for price_tmp in self.ordered_book:
				if self.ordered_book[price_tmp] > 0:
					index = list(self.ordered_book.keys()).index(price_tmp)
					print(list(self.ordered_book.keys()))
					print(list(self.ordered_book.keys()).reverse())
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = self.ordered_book[price_tmp]
						price = price_tmp
		
		if score != 0:
			return price, share, score
		else:
			return "no translation should proceed"

price_info = pdr.get_data_yahoo("AAPL", "2015-3-9", "2017-1-1")['Adj Close']
current_price = price_info.to_list()[287]
print(current_price)
ordered_book = OrderedDict(((27, 10), (26, 20), (25, 30), (24, 40), (23, 50), (21, -50), (20, -40), (19, -30), (18, -20), (17, -10)))
time_stamp = 287
bot = BotEvaluatorSample(price_info, current_price, ordered_book, time_stamp)
result = bot.evaluator()
print(result)
st_moving_avg = price_info.rolling(window=15).mean().to_list()
lt_moving_avg = price_info.rolling(window=30).mean().to_list()
# for index in range(len(price_info)):
# 	if st_moving_avg[index] > lt_moving_avg[index] and st_moving_avg[index-1] <= lt_moving_avg[index-1]:
# 		print(index, "UP")
# 	elif st_moving_avg[index] < lt_moving_avg[index] and st_moving_avg[index-1] >= lt_moving_avg[index-1]:
# 		print(index, "DOWN")

# import matplotlib.pyplot as plt
# plt.plot(price_info.to_list())
# plt.plot(st_moving_avg)
# plt.plot(lt_moving_avg)
# plt.show()

# class BotEvaluatorSample:
# 	def __init__(
# 			self,
# 			price_info: list,
# 			current_price: float,
# 			ordered_book: OrderedDict,
# 			stock_name: str,
# 			time_stamp: float,
# 	):