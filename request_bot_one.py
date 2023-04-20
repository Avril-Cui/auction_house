"""
All bots/users have three possible actions:
    1. Trade stock at equilibrium price
    2. Put trade (buy or sell) at any desired price
    3. Accept an existing order
        - An user/bot can to the market and accept any orders
        - An user/bot can put a trade -> if it is available in the market, then goes through
        - For a bot, when a price is passed through, it will take ALL the orders in the market
"""

import psycopg2
import time
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

# def get_active_order_book(comp_name, url="http://127.0.0.1:5000/"):
#     order_book = json.loads(requests.request("POST", f"{url}get-order-book", data=json.dumps(comp_name)).content)
#     return list(order_book)

def get_active_order_book(comp_name):
    ### get all buy orders from ranked from high to low
    cur.execute(f"""
        SELECT price, shares, RANK() OVER (ORDER BY price DESC) as rank FROM orders WHERE 
        accepted={False} AND company_name='{comp_name}' AND action='buy';
    """)
    buy_orders = list(cur.fetchall())
    buy_order_book = OrderedDict(())
    if buy_orders != []:
        price = buy_orders[0][0]
        shares = buy_orders[0][1]
        for index in range(1, len(buy_orders)):
            if buy_orders[index][0] == price:
                shares += buy_orders[index][1]
            else:
                buy_order_book.update({float(price): -float(shares)})
                price = buy_orders[index][0]
                shares = buy_orders[index][1]
                
            if index + 1 == len(buy_orders):
                    buy_order_book.update({float(price): -float(shares)})

    cur.execute(f"""
        SELECT price, shares, RANK() OVER (ORDER BY price DESC) as rank FROM orders WHERE 
        accepted={False} AND company_name='{comp_name}' AND action='sell';
    """)
    sell_orders = list(cur.fetchall())
    sell_order_book = OrderedDict(())
    if sell_orders != []:
        price = sell_orders[0][0]
        shares = sell_orders[0][1]
        for index in range(1, len(sell_orders)):
            if sell_orders[index][0] == price:
                shares += sell_orders[index][1]

            else:
                sell_order_book.update({float(price), float(shares)})
                price = sell_orders[index][0]
                shares = sell_orders[index][1]
        if index + 1 == len(sell_orders):
                    sell_order_book.update({float(price): float(shares)})
    
    sell_order_book.update(buy_order_book)
    print(sell_order_book)
    return sell_order_book

def accept_order(price, trade_action, user_uid, comp_name):
    if trade_action == "sell":
        action = "buy"
    elif trade_action == "buy":
        action = "sell"
    
    cur.execute(f"""
        SELECT order_id, user_uid FROM orders WHERE price={price} AND action='{action}';
    """)
    ids = list(cur.fetchall())
    share_number = 0
    for index in range(len(ids)):
        order_id = ids[index][0]
        cur.execute(f"""
            SELECT shares FROM orders WHERE order_id='{order_id}' AND action='{action}' AND price={price};
        """)
        shares=float(cur.fetchone()[0])
        if action == "buy":
            share_number+=shares
        elif action == "sell":
            share_number-=shares

    cur.execute(f"""
		  SELECT cashvalue from users WHERE uid='{user_uid}';
    """)
    cash_value = float(cur.fetchone()[0])
    cur.execute(f"""
		SELECT shares_holding from portfolio WHERE uid='{user_uid}' and company_id='{comp_name}';
    """)
    portfolio_data = cur.fetchone()
    if portfolio_data != None:
        shares_holding = float(portfolio_data[0])

    trade_value = share_number * price

    invalid = False

    if trade_value > cash_value and share_number > 0:
        invalid = True
        print("INVALID 2")
        return "Invalid 2"  
    elif share_number > 0:
        if portfolio_data != None:
            cur.execute(f"""
                INSERT INTO trade_history VALUES (
                    '{user_uid}',
                    '{comp_name}',
                    {round(float(time.time()), 2)},
                    {round(share_number,2)},
                    {round(trade_value,2)}
                );
                UPDATE users SET cashvalue = (cashvalue-{round(trade_value, 2)})
                WHERE uid='{user_uid}';
                UPDATE portfolio SET shares_holding = (shares_holding+{round(share_number,2)})
                WHERE uid='{user_uid}' and company_id='{comp_name}';
                UPDATE portfolio SET cost = (cost+{round(trade_value,2)})
                WHERE uid='{user_uid}' and company_id='{comp_name}';
            """)
            conn.commit()
        else:
            cur.execute(f"""
                INSERT INTO trade_history VALUES (
                    '{user_uid}',
                    '{comp_name}',
                    {round(float(time.time()), 2)},
                    {round(share_number,2)},
                    {round(trade_value,2)}
                );
                UPDATE users SET cashvalue = (cashvalue-{round(trade_value, 2)})
                WHERE uid='{user_uid}';
                INSERT INTO portfolio VALUES (
                    '{user_uid}',
                    '{comp_name}',
                    {round(share_number,2)},
                    {round(trade_value,2)}
                );
            """)
            conn.commit()
    else:
        if portfolio_data != None:
            if abs(share_number) > shares_holding:
                invalid = True
                print("INVALID 1")
                return "Invalid 1"
            else:
                cur.execute(f"""
                    INSERT INTO trade_history VALUES (
                        '{user_uid}',
                        '{comp_name}',
                        {round(float(time.time()), 2)},
                        {round(share_number,2)},
                        {round(trade_value,2)}
                    );
                    UPDATE users SET cashvalue = (cashvalue+{abs(round(trade_value, 2))})
                    WHERE uid='{user_uid}';
                    UPDATE portfolio SET shares_holding = (shares_holding+{round(share_number,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                    UPDATE portfolio SET cost = (cost+{round(trade_value,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                    
                """)
                conn.commit()
        else:
            invalid = True
            print("INVALID 1")
            return "Invalid 1"

    if invalid == False:
        cur.execute(f"""
            SELECT order_id, user_uid FROM orders WHERE price={price} AND action='{action}';
        """)
        ids = list(cur.fetchall())
        print(ids)
        for index in range(len(ids)):
            order_id = ids[index][0]
            print(order_id)
            user_uid = ids[index][1]
            cur.execute(f"""
                UPDATE orders SET accepted={True} WHERE order_id='{order_id}';
            """)
            conn.commit()  
            cur.execute(f"""
                SELECT shares FROM orders WHERE action='{action}' AND price={price} AND order_id='{order_id}';
            """)
            conn.commit()
            shares = float(cur.fetchone()[0])
            trade_value = shares * price
            if action == 'buy':
                cur.execute(f"""
                    INSERT INTO trade_history VALUES (
                        '{user_uid}',
                        '{comp_name}',
                        {round(float(time.time()), 2)},
                        {round(shares,2)},
                        {round(trade_value,2)}
                    );
                    UPDATE portfolio SET shares_holding = (shares_holding+{round(shares,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                    UPDATE portfolio SET cost = (cost+{round(trade_value,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                """)
                conn.commit()
            else:
                cur.execute(f"""
                    INSERT INTO trade_history VALUES (
                        '{user_uid}',
                        '{comp_name}',
                        {round(float(time.time()), 2)},
                        {-round(shares,2)},
                        {-round(trade_value,2)}
                    );
                    UPDATE portfolio SET shares_holding = (shares_holding-{round(shares,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                    UPDATE portfolio SET cost = (cost-{round(trade_value,2)})
                    WHERE uid='{user_uid}' and company_id='{comp_name}';
                """)
                conn.commit()

# orders = get_active_order_book("wrkn")

###trader bots
# bot_id = register_bot("http://127.0.0.1:5000/register", "trade_ma")
# for index in range(len(index_price)):
#     time_stamp = index
#     current_price = 0
#     coefficient = bot.stg_ma(index_price_df, time_stamp, st_moving_avg_period=15, lt_moving_avg_period=30)
#     share = 50
#     if coefficient == 1:
#         trade_stock("trader_ma", bot_id, current_price, share, "wrkn")
#     elif coefficient == -1:
#         trade_stock("trader_ma", bot_id, current_price, -(share), "wrkn")

###put orders
bot_id = register_bot("http://127.0.0.1:5000/register", "bot_ma")
print(bot_id)
for index in range(len(index_price)):
    time_stamp = index
    current_price = index_price[time_stamp]
    order_book = get_order_book(current_price)
    price, share, score = bot.evaluator_ma_surplus_accept(index_price_df, time_stamp, order_book, st_moving_avg_period=15, lt_moving_avg_period=30)
    trade_stock("bot_ma", bot_id, price, share, "wrkn")

##accept trades
bot_id = register_bot("http://127.0.0.1:5000/register", "accept_bot")
# bot_id = "0vYqDkUjRycZW2BwGaKLEkkwLnf1"
trade_stock("accept_bot", bot_id, 0, 50, "wrkn")
accept_order(985, "sell", bot_id, "wrkn")