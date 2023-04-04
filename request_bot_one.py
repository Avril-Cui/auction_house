import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import time
from collections import OrderedDict
import pandas as pd

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

def trade_stock(bot_name, time_stamp, comp_name, ordered_book, current_price, index_price_df, url="http://127.0.0.1:5000/"):
    payload = f"\"{comp_name}\""
    current_price = float(json.loads(requests.request("POST", f"{url}current-price", data=payload).text)["price"])

    index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
    price, share, score = bot.evaluator_ma_surplus(index_price_df, time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30)

    if share < 0:
        buy_data = {
            "user_uid": bot_name,
            "comp_name": comp_name,
            "share_number": abs(share),
            "target_price": price
        }

        reponse = requests.request("POST", f"{url}/trade-stock", data=json.dumps(buy_data))
        print(f"Buy order made successfully by {bot_name} at {current_price} for {abs(share)} shares.")

    elif share > 0:
        sell_data = {
            "user_uid": bot_name,
            "comp_name": comp_name,
            "share_number": abs(share),
            "target_price": (current_price)-1
        }

        reponse = requests.request("POST", f"{url}/trade-stock", data=json.dumps(sell_data))
        print(f"Sell order made successfully by {bot_name} at {current_price} for {abs(share)} shares.")
        print(f"\n")


# bot_two = BotTwo("ast")
# for i in range(10):
#     bot_two.trade_stock()
#     time.sleep(1)