import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import time

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
          SELECT price_list from prices WHERE company_id='{company_id}';
        """)
	price = list(cur.fetchone()[0])
	return price

index_price = get_price_from_database("index")
ast_price = get_price_from_database("ast")
dsc_price = get_price_from_database("dsc")
fsin_price = get_price_from_database("fsin")
hhw_price = get_price_from_database("hhw")
jky_price = get_price_from_database("jky")
sgo_price = get_price_from_database("sgo")
wrkn_price = get_price_from_database("wrkn")


class BotTwo:
    def __init__(self, comp_name):
        self.url = "http://127.0.0.1:5000/trade-stock"
        self.comp_name = comp_name

    def trade_stock(self):
        payload = "\"wrkn\""
        payload = f"\"{self.comp_name}\""
        current_price = float(json.loads(requests.request("POST", "http://127.0.0.1:5000/current-price", data=payload).text)["price"])

        buy_data = {
            "user_uid": "bot_two",
            "comp_name": self.comp_name,
            "share_number": 100,
            "target_price": (current_price)-1
        }
    
        reponse = requests.request("POST", self.url, data=json.dumps(buy_data))
        print(f"Buy order made successfully by Bot 2 at {current_price} for 100 shares.")

        sell_data = {
            "user_uid": "bot_two",
            "comp_name": self.comp_name,
            "share_number": -100,
            "target_price": (current_price)-1
        }
    
        reponse = requests.request("POST", self.url, data=json.dumps(sell_data))
        print(f"Sell order made successfully by Bot 2 at {current_price} for 100 shares.")
        print(f"\n")

bot_two = BotTwo("ast")
for i in range(10):
    bot_two.trade_stock()
    time.sleep(1)