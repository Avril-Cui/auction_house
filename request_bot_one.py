import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import time
import pandas as pd
from collections import OrderedDict
import random
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ROOT_NAME = os.getenv("DATABASE_ROOT_NAME")

conn = psycopg2.connect(
    host=DATABASE_HOST if DATABASE_HOST!=None else "localhost",
    database=DATABASE_ROOT_NAME if DATABASE_ROOT_NAME!=None else "aspectdatabase",
    user=DATABASE_USER if DATABASE_USER!=None else "postgres",
    password=DATABASE_PASSWORD if DATABASE_PASSWORD!=None else "Xiaokeai0717"
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

def register_bot(register_url, bot_name):
    payload = json.dumps({
        "user_email": f"{bot_name}@gmail.com",
        "password": "Xiaokeai0717",
        "user_name": bot_name
    })
    response = requests.request("POST", register_url, data=payload)
    print(response.status_code)

def trade_stock(bot_name, bot_uid, price, share, comp_name, url="http://127.0.0.1:5000/"):
    payload = f"\"{comp_name}\""

    if share > 0:
        buy_data = {
            "user_uid": bot_uid,
            "comp_name": comp_name,
            "share_number": abs(share),
            "target_price": price
        }

        response = requests.request("POST", f"{url}trade-stock", data=json.dumps(buy_data))
        if response.status_code == 401:
            print("You do not owe enough shares of this stock.")
        elif response.status_code == 402:
            print("You do not have enough money for this trade")
        elif response.status_code == 403:
            print("Currently no shares available for trade. Your transaction will enter the pending state.")
        else:
            print(f"Buy order made successfully by {bot_name} at {price} for {abs(share)} shares.")

    elif share < 0:
        sell_data = {
            "user_uid": bot_uid,
            "comp_name": comp_name,
            "share_number": (share),
            "target_price": price
        }

        response = requests.request("POST", f"{url}trade-stock", data=json.dumps(sell_data))
        if response.status_code == 401:
            print("You do not owe enough shares of this stock.")
        elif response.status_code == 402:
            print("You do not have enough money for this trade")
        elif response.status_code == 403:
            print("Currently no shares available for trade. Your transaction will enter the pending state.")
        else:
            print(f"Sell order made successfully by {bot_name} at {price} for {abs(share)} shares.")

# register_bot("http://127.0.0.1:5000/register", "ma_bot")

price_data = pdr.get_data_yahoo("AAPL", "2015-3-9", "2017-1-1")
time_stamp = 287
current_price = price_data['Adj Close'].to_list()[time_stamp]
ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
price, share, score = bot.evaluator_ma_surplus(price_data['Adj Close'], time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30)
trade_stock("Moving Average", "iMioxAB0MpNWoPFwIaZY2Y3jr4G3", price, share, "wrkn")

# bot_two = BotTwo("ast")
# for i in range(10):
#     bot_two.trade_stock()
#     time.sleep(1)