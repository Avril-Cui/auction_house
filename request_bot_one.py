import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import pandas as pd
from collections import OrderedDict
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
index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  

from bot_one import BotOne
bot = BotOne()

def get_order_book(current_price):
    order_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
    return order_book

def register_bot(register_url, bot_name):
    payload = json.dumps({
        "user_email": f"{bot_name}@gmail.com",
        "password": "Xiaokeai0717",
        "user_name": bot_name
    })
    response = requests.request("POST", register_url, data=payload)
    print(response.status_code)
    uid = str(response.content).split("'")[1].split("'")[0]
    return uid

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

def get_active_order_book(comp_name, url="http://127.0.0.1:5000/"):
    order_book = json.loads(requests.request("POST", f"{url}get-order-book", data=json.dumps(comp_name)).content)
    return list(order_book)

def get_active_order_book(comp_name):
    ### get all buy orders from ranked from high to low
    cur.execute(f"""
        SELECT price, shares, RANK() OVER (ORDER BY price DESC) as rank FROM orders WHERE 
        accepted={False} AND company_name='{comp_name}' AND action='buy';
    """)
    buy_orders = list(cur.fetchall())

    cur.execute(f"""
        SELECT price, shares, RANK() OVER (ORDER BY price DESC) as rank FROM orders WHERE 
        accepted={False} AND company_name='{comp_name}' AND action='sell';
    """)
    sell_orders = list(cur.fetchall())
    
    order_book = buy_orders + sell_orders
    print(order_book)
    return order_book


get_active_order_book("wrkn")
# OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))











# bot_id = register_bot("http://127.0.0.1:5000/register", "bot_ma")
# print(bot_id)
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = index_price[time_stamp]
#     order_book = get_order_book(current_price)
#     price, share, score = bot.evaluator_ma_surplus(index_price_df, time_stamp, order_book, st_moving_avg_period=15, lt_moving_avg_period=30)
#     trade_stock("bot_ma", bot_id, price, share, "wrkn")

# order_book = json.loads(requests.request("POST", "http://127.0.0.1:5000/get-order-book", data=json.dumps("wrkn")).content)
# print(order_book)