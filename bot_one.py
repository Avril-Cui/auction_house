from collections import OrderedDict
import random
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

#sell: -1
#buy: +1


class BotOne:

	def __init__(self) -> None:
		pass

	def stg_ma(self, price_info, time_stamp, st_moving_avg_period, lt_moving_avg_period):
		st_moving_avg = price_info.rolling(
			window=st_moving_avg_period).mean().to_list()
		lt_moving_avg = price_info.rolling(
			window=lt_moving_avg_period).mean().to_list()
		if st_moving_avg[time_stamp] > lt_moving_avg[time_stamp] and st_moving_avg[time_stamp-1] <= lt_moving_avg[time_stamp-1]:
			return 1
		elif st_moving_avg[time_stamp] < lt_moving_avg[time_stamp] and st_moving_avg[time_stamp-1] >= lt_moving_avg[time_stamp-1]:
			return -1
		else:
			return 0

	def stg_surplus(self, index):
		return 0.2 * index
	
	def stg_momentum(self, price_info, volume_info, moving_avg_period, time_stamp):
		price_moving_avg = price_info.rolling(window=moving_avg_period).mean().to_list()
		volume_moving_avg = volume_info.rolling(window=moving_avg_period).mean().to_list()
		price_list = price_info.to_list()
		volume_list = volume_info.to_list()

		if price_list[time_stamp] < price_moving_avg[time_stamp] and volume_list[time_stamp] > volume_moving_avg[time_stamp]:
			return 1
		elif price_list[time_stamp] > price_moving_avg[time_stamp] and volume_list[time_stamp] < volume_moving_avg[time_stamp]:
			return -1
		else:
			return 0

	def stg_mean_reversion(self, price_info, moving_avg_period, time_stamp, n_std=1):
		moving_avg = price_info.rolling(window = moving_avg_period).mean().to_list()[time_stamp]
		moving_std = price_info.rolling(window = moving_avg_period).std().to_list()[time_stamp]
		current_price = price_info.to_list()[time_stamp]
		upper_bound = moving_avg + n_std * moving_std
		lower_bound = moving_avg - n_std * moving_std

		if current_price < lower_bound:
			return -1
		elif current_price > upper_bound:
			return 1
		else:
			return 0	

	def stg_donchian_breakout(self, price_info, moving_avg_period, time_stamp):
		if time_stamp == 0:
			return 0
		else:
			moving_high = price_info.rolling(window = moving_avg_period).max().to_list()[time_stamp-1]
			moving_low = price_info.rolling(window = moving_avg_period).min().to_list()[time_stamp-1]
			current_price = price_info.to_list()[time_stamp]

			if current_price < moving_low:
				return -1
			elif current_price > moving_high:
				return 1
			else:
				print(current_price, moving_low, moving_high)
				return 0

	def evaluator_ma_surplus(self, price_info, time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30):
		"""
			Rule1 [Moving Average] -> direction:
				BUY: When shorter-term MA crosses above the long-term MA: buy, return -1
				SELL: When shorter-term MA crosses below the long-term MA: sell, return +1
			Rule2 [Surplus] -> trade the order with maximum surplus:
				Buy: highest sell order, return 1, 0.8, 0.6, 0.4, 0.2
				Sell: lowest buy order, return -1, -0.8, -0.6, -0.4, -0.2
		"""
		
		print("Bot 1: MA and surplus")
		print("---------------------")
		price = price_info[time_stamp]
		share = 50
		score = 0
		coefficient = self.stg_ma(price_info, time_stamp, st_moving_avg_period, lt_moving_avg_period)
		if coefficient == -1:
			# print(f"At time {time_stamp}, Bot MA buys at ${round(price, 2)} for {abs(share)} shares. \n")
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] < 0:
					index = list(ordered_book.keys()).index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = score_tmp
						share = ordered_book[price_tmp]
						price = price_tmp
		elif coefficient == 1:
			# print(f"At time {time_stamp}, Bot MA sells at ${round(price, 2)} for {abs(share)} shares. \n")
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] > 0:
					price_list = list(ordered_book.keys())
					price_list.reverse()
					index = price_list.index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = ordered_book[price_tmp]
						price = price_tmp
		
		if score < 0:
			print(f"Highest absolute score is {abs(score)}. Bot buys at ${price} for {abs(share)} shares. \n")
			return price, share, score
		elif score > 0:
			print(f"Highest score is {score}. Bot sells at ${price} for {share} shares. \n")
			return price, share, score
		else:
			return 0, 0, 0

	def evaluator_momentum_surplus(self, price_info, volume_info, time_stamp, ordered_book, moving_avg_period=30):
		"""
			Rule1 [Momentum] -> direction:
				BUY:  When stock price is below the x day moving average and the daily
					  volume is above the 30 day moving average, return -1.
				SELL: When stock price is above the x day moving average and the daily
					  volume is below the 30 day moving average, return +1.
			Rule2 [Surplus] -> trade the order with maximum surplus:
				Buy: highest sell order, return 1, 0.8, 0.6, 0.4, 0.2
				Sell: lowest buy order, return -1, -0.8, -0.6, -0.4, -0.2
		"""

		print("Bot 2: Momentum and surplus")
		print("---------------------------")
		price = 0
		share = 0
		score = 0
		coefficient = self.stg_momentum(price_info, volume_info, moving_avg_period, time_stamp)
		
		if coefficient == -1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] < 0:
					index = list(ordered_book.keys()).index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = score_tmp
						share = ordered_book[price_tmp]
						price = price_tmp
		elif coefficient == 1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] > 0:
					price_list = list(ordered_book.keys())
					price_list.reverse()
					index = price_list.index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = ordered_book[price_tmp]
						price = price_tmp
		else:
			score = 0
		
		if score < 0:
			print(f"Highest absolute score is {abs(score)}. Bot buys at ${price} for {abs(share)} shares. \n")
			return price, share, score
		elif score > 0:
			print(f"Highest score is {score}. Bot sells at ${price} for {share} shares. \n")
			return price, share, score
		else:
			print("No translation should proceed. \n")

	def evaluator_mean_reversion_surplus(self, price_info, time_stamp, ordered_book, moving_avg_period=30, n_std=1):
		"""
			Rule1 [Mean Reversion] -> direction:
				BUY: When price is above moving average + n * moving standard deviation
				SELL: When price is below moving average - n * moving standard deviation
			Rule2 [Surplus] -> trade the order with maximum surplus:
				Buy: highest sell order, return 1, 0.8, 0.6, 0.4, 0.2
				Sell: lowest buy order, return -1, -0.8, -0.6, -0.4, -0.2
		"""

		print("Bot 3: Mean reversion and surplus")
		print("---------------------------------")
		price = 0
		share = 0
		score = 0
		coefficient = self.stg_mean_reversion(price_info, moving_avg_period, time_stamp, n_std)
		
		if coefficient == -1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] < 0:
					index = list(ordered_book.keys()).index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = score_tmp
						share = ordered_book[price_tmp]
						price = price_tmp
		elif coefficient == 1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] > 0:
					price_list = list(ordered_book.keys())
					price_list.reverse()
					index = price_list.index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = ordered_book[price_tmp]
						price = price_tmp
		else:
			score = 0
		
		if score < 0:
			print(f"Highest absolute score is {abs(score)}. Bot buys at ${price} for {abs(share)} shares. \n")
			return price, share, score
		elif score > 0:
			print(f"Highest score is {score}. Bot sells at ${price} for {share} shares. \n")
			return price, share, score
		else:
			print("No translation should proceed. \n")

	def evaluator_donchian_breakout_surplus(self, price_info, time_stamp, ordered_book, moving_avg_period=30):
		"""
			Rule1 [Donchian Breakout] -> direction:
				BUY: When price is below Donchian lower bound
				SELL: When the price is above Donchian upper boud
			Rule2 [Surplus] -> trade the order with maximum surplus:
				Buy: highest sell order, return 1, 0.8, 0.6, 0.4, 0.2
				Sell: lowest buy order, return -1, -0.8, -0.6, -0.4, -0.2
		"""

		print("Bot 4: Donchian breakout and surplus")
		print("------------------------------------")
		price = 0
		share = 0
		score = 0
		coefficient = self.stg_donchian_breakout(price_info, moving_avg_period, time_stamp)
		
		if coefficient == -1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] < 0:
					index = list(ordered_book.keys()).index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = score_tmp
						share = ordered_book[price_tmp]
						price = price_tmp
		elif coefficient == 1:
			for price_tmp in ordered_book:
				if ordered_book[price_tmp] > 0:
					price_list = list(ordered_book.keys())
					price_list.reverse()
					index = price_list.index(price_tmp)
					score_tmp = self.stg_surplus(index) * coefficient
					if abs(score_tmp) > score:
						score = abs(score_tmp)
						share = ordered_book[price_tmp]
						price = price_tmp
		else:
			score = 0
		
		if score < 0:
			print(f"Highest absolute score is {abs(score)}. Bot buys at ${price} for {abs(share)} shares. \n")
			return price, share, score
		elif score > 0:
			print(f"Highest score is {score}. Bot sells at ${price} for {share} shares. \n")
			return price, share, score
		else:
			print("No translation should proceed. \n")

	def evaluator_crazy_bot(self, price_info, time_stamp, ordered_book, share_lower_limit=50, share_upper_limit=200, n_std=1, moving_avg_period=30):
		print("Crazy Bot: Random Trading Behavior")
		print("----------------------------------")

		trade_or_take = random.choice([0, 1])

		if trade_or_take == 0: #take
			price, share = random.choice(list(ordered_book.items()))
		elif trade_or_take == 1: #trade
			moving_std = price_info.rolling(window = moving_avg_period).std().to_list()[time_stamp]
			current_price = price_info.to_list()[time_stamp]
			buy_or_sell = random.choice([-1, 1])
			share = random.randint(share_lower_limit, share_upper_limit) * buy_or_sell
			if buy_or_sell == 1: #sell
				price = current_price + n_std * moving_std
			elif buy_or_sell == -1: #buy
				price = current_price - n_std * moving_std

		if share < 0:
			print(f"Crazy Bot buys at ${round(price, 2)} for {abs(share)} shares. \n")
			return price, share
		elif share > 0:
			print(f"Crazy Bot sells at ${round(price, 2)} for {share} shares. \n")
			return price, share
		else:
			print("No translation should proceed. \n")


price_data = pdr.get_data_yahoo("AAPL", "2015-3-9", "2017-1-1")
bot = BotOne()

###Bot One
time_stamp = 287
current_price = price_data['Adj Close'].to_list()[time_stamp]
ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
result = bot.evaluator_ma_surplus(price_data['Adj Close'], time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30)

# ###Bot Two
# time_stamp = 47
# current_price = price_data['Adj Close'].to_list()[time_stamp]
# ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
# result = bot.evaluator_momentum_surplus(price_data['Adj Close'], price_data['Volume'], time_stamp, ordered_book, moving_avg_period=30)

# ###Bot Three
# time_stamp = 31
# current_price = price_data['Adj Close'].to_list()[time_stamp]
# ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
# result = bot.evaluator_mean_reversion_surplus(price_data['Adj Close'], time_stamp, ordered_book, moving_avg_period=30, n_std=1)

# ###Bot Four
# time_stamp = 78
# current_price = price_data['Adj Close'].to_list()[time_stamp]
# ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
# result = bot.evaluator_donchian_breakout_surplus(price_data['Adj Close'], time_stamp, ordered_book, moving_avg_period=30)

# ###Crazy Bot
# time_stamp = 100
# current_price = price_data['Adj Close'].to_list()[time_stamp]
# ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
# result = bot.evaluator_crazy_bot(price_data['Adj Close'], time_stamp, ordered_book, share_lower_limit=50, share_upper_limit=200, n_std=1, moving_avg_period=30)

# #Graphing:
# # st_moving_avg = price_info.rolling(window=15).mean().to_list()
# # lt_moving_avg = price_info.rolling(window=30).mean().to_list()
# # import matplotlib.pyplot as plt
# # plt.plot(price_info.to_list())
# # plt.plot(st_moving_avg)
# # plt.plot(lt_moving_avg)
# # plt.show()