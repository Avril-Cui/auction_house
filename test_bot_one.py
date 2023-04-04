from operator import index
import psycopg2
import matplotlib.pyplot as plt
from collections import OrderedDict
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="aspectdatabase",
    user="postgres",
    password="Xiaokeai0717"
)
cur = conn.cursor()

def get_price_from_database(company_id):
	cur.execute(f"""
          SELECT price_list from test_prices WHERE company_id='{company_id}';
    """)
	price = list(cur.fetchone()[0])
	return price

index_price = get_price_from_database("index")[60*60*10:60*60*11]
index_price = [float(i) for i in index_price]

from bot_one import BotOne
bot = BotOne()

z = 1
PL = 0
start_price = index_price[0]
end_price = index_price[-1]
Return = (PL/start_price)
pct_return = ":.2%".format(Return)

print("Start Price: ", round(start_price, 3))
print("End Price: ", round(end_price, 3))


###Bot1
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = index_price[time_stamp]
#     ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
#     index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
#     result = bot.evaluator_ma_surplus(index_price_df, time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30)

#     share = 50
#     if result == -1:
#         if z == 1:
#             print(f"At time {time_stamp}, Bot MA buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == 1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Bot MA sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1
# print(f"Total return for MA strategy throughout the day is {pct_return}.")

###Bot2: Cannot be tested now since volume is not available

###Bot3
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = index_price[time_stamp]
#     ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
#     index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
#     result = bot.evaluator_mean_reversion_surplus(index_price_df, time_stamp, ordered_book, moving_avg_period=30, n_std=1)
#     share = 50
#     if result == -1:
#         if z == 1:
#             print(f"At time {time_stamp}, Bot Mean Reversion buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == 1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Bot Mean Reversion sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1
# print(f"Total return for Mean Reversion strategy throughout the day is {pct_return}.")

###Bot4
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = index_price[time_stamp]
#     ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
#     index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
#     result = bot.evaluator_donchian_breakout_surplus(index_price_df, time_stamp, ordered_book, moving_avg_period=30)
#     share = 50
#     if result == -1:
#         if z == 1:
#             print(f"At time {time_stamp}, Bot Donchian Breakout buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == 1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Bot Donchian Breakout sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1
# print(f"Total return for Donchian Breakout strategy throughout the day is {pct_return}.")

###Crazy Bot
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = index_price[time_stamp]
#     ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
#     index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
#     result = bot.evaluator_crazy_bot(index_price_df, time_stamp, ordered_book, share_lower_limit=50, share_upper_limit=200, n_std=1, moving_avg_period=30)
#     share = 50
#     if result == -1:
#         if z == 1:
#             print(f"At time {time_stamp}, Crazy Bot buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == 1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Crazy Bot sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1
# print(f"Total return for Crazy Bot throughout the day is {pct_return}.")