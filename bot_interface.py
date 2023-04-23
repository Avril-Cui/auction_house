from bot_one import BotOne
from bot_three import BotThree
import psycopg2
import time
import os
import pandas as pd
from collections import OrderedDict
from queue import Queue
from threading import Thread
from dotenv import load_dotenv
import json
import requests
load_dotenv()
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ROOT_NAME = os.getenv("DATABASE_ROOT_NAME")

conn = psycopg2.connect(
    host=DATABASE_HOST if DATABASE_HOST != None else "localhost",
    database=DATABASE_ROOT_NAME if DATABASE_ROOT_NAME != None else "aspectdatabase",
    user=DATABASE_USER if DATABASE_USER != None else "postgres",
    password=DATABASE_PASSWORD if DATABASE_PASSWORD != None else "Xiaokeai0717"
)
cur = conn.cursor()


def get_price_from_database(company_id):
    cur.execute(f"""
          SELECT price_list from prices WHERE company_id='{company_id}';
    """)
    price = list(cur.fetchone()[0])
    price = [float(i) for i in price]
    return price

company_lst = ["ast", "dsc", "fsin", "hhw", "jky", "sgo", "wrkn"]

def register_bot(register_url, bot_name, initial_price):
    payload = json.dumps({
        "bot_name": bot_name,
        "initial_price": initial_price
    })
    response = requests.request("POST", register_url, data=payload)
    print(response.status_code)

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
        if len(buy_orders) == 1:
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
    if sell_order_book==OrderedDict(()):
        sell_order_book.update({0:0})
    return sell_order_book

def trader(result_queue, price_info, time_stamp, shares=10):
    trade = {}
    for company in company_lst:
        ma_decision = bot1.stg_ma(
            price_info[company], time_stamp, st_moving_avg_period=15, lt_moving_avg_period=30)
        mean_reversion_decision = bot1.stg_mean_reversion(
            price_info[company], time_stamp, n_std=1, moving_avg_period=30)
        donchain_decision = bot1.stg_donchian_breakout(
            price_info[company], time_stamp, moving_avg_period=30)
        crazy_bot_decision = bot1.crazy_trader()

        trade_company = {
            "MysticAdventurer": {
                "share_number": ma_decision * shares,
                "target_price": 0
            },
            "MagicRider": {
                "share_number": mean_reversion_decision * shares,
                "target_price": 0
            },
            "DiamondCrystal": {
                "share_number": donchain_decision * shares,
                "target_price": 0
            },
            "MadInvestor": {
                "share_number": crazy_bot_decision * shares,
                "target_price": 0
            }
        }

        trade[company] = trade_company

    result_queue.put(["trader", trade])

def accepter(result_queue, price_info, time_stamp, order_book):
    accept = {}
    for company in company_lst:
        ma_price, ma_share, ma_score = bot1.evaluator_ma_surplus_accept(
            price_info[company], time_stamp, order_book[company], st_moving_avg_period=15, lt_moving_avg_period=30)
        mean_rev_price, mean_rev_share, mean_rev_score = bot1.evaluator_mean_reversion_surplus_accept(
            price_info[company], time_stamp, order_book[company], moving_avg_period=30, n_std=1)
        donchain_price, donchain_share, donchain_score = bot1.evaluator_donchian_breakout_surplus_accept(
            price_info[company], time_stamp, order_book[company], moving_avg_period=30)

        crazy_price, crazy_share = bot1.crazy_accepter(order_book[company])

        accept_company = {
            "MysticAdventurer": {
                "share_number": ma_share,
                "target_price": ma_price
            },
            "MagicRider": {
                "share_number": mean_rev_share,
                "target_price": mean_rev_price
            },
            "DiamondCrystal": {
                "share_number": donchain_share,
                "target_price": donchain_price
            },
            "MadInvestor": {
                "share_number": crazy_share,
                "target_price": crazy_price
            }
        }

        accept[company] = accept_company
    result_queue.put(["accepter", accept])

def bidder(result_queue, price_info, time_stamp, shares=10, split = 50):
    bidder = {}
    for company in company_lst:
        input_data = price_info[company][(time_stamp-split):time_stamp]
        arima_price = bot2.arima_forecaster(input_data)
        bidder_company = {
            "arima_bot": {
                "share_number": shares,
                "target_price": arima_price
            }
        }

        bidder[company] = bidder_company
    result_queue.put(["bidder", bidder])



if __name__ == '__main__':
    bot1 = BotOne()
    bot2 = BotThree()

    ast_price = get_price_from_database("ast")[60*60*10:60*60*11]
    ast_price_df = pd.DataFrame(ast_price, columns=["price"])["price"]
    dsc_price = get_price_from_database("dsc")[60*60*10:60*60*11]
    dsc_price_df = pd.DataFrame(dsc_price, columns=["price"])["price"]
    fsin_price = get_price_from_database("fsin")[60*60*10:60*60*11]
    fsin_price_df = pd.DataFrame(fsin_price, columns=["price"])["price"]
    hhw_price = get_price_from_database("hhw")[60*60*10:60*60*11]
    hhw_price_df = pd.DataFrame(hhw_price, columns=["price"])["price"]
    jky_price = get_price_from_database("jky")[60*60*10:60*60*11]
    jky_price_df = pd.DataFrame(jky_price, columns=["price"])["price"]
    sgo_price = get_price_from_database("sgo")[60*60*10:60*60*11]
    sgo_price_df = pd.DataFrame(sgo_price, columns=["price"])["price"]
    wrkn_price = get_price_from_database("wrkn")[60*60*10:60*60*11]
    wrkn_price_df = pd.DataFrame(wrkn_price, columns=["price"])["price"]

    price_info = {
        "ast": ast_price_df,
        "dsc": dsc_price_df,
        "fsin": fsin_price_df,
        "hhw": hhw_price_df,
        "jky": jky_price_df,
        "sgo": sgo_price_df,
        "wrkn": wrkn_price_df,   
    }

    order_book = {
        "ast": get_active_order_book("ast"),
        "dsc": get_active_order_book("dsc"),
        "fsin": get_active_order_book("fsin"),
        "hhw": get_active_order_book("hhw"),
        "jky": get_active_order_book("jky"),
        "sgo": get_active_order_book("sgo"),
        "wrkn": get_active_order_book("wrkn"),
    }

    initial_price = {
        "ast": ast_price[0],
        "dsc": dsc_price[0],
        "fsin": fsin_price[0],
        "hhw": hhw_price[0],
        "jky": jky_price[0],
        "sgo": sgo_price[0],
        "wrkn": wrkn_price[0]
    }

    register_bot("http://127.0.0.1:5000/register-bot", "MysticAdventurer", initial_price) #ma_bot
    register_bot("http://127.0.0.1:5000/register-bot", "MagicRider", initial_price) #mean_reversion_bot
    register_bot("http://127.0.0.1:5000/register-bot", "DiamondCrystal", initial_price) #donchian_bot
    register_bot("http://127.0.0.1:5000/register-bot", "MadInvestor", initial_price) #crazy_bot
    register_bot("http://127.0.0.1:5000/register-bot", "Arima", initial_price) #arima_bot
    register_bot("http://127.0.0.1:5000/register-bot", "KnightNexus", initial_price) #arima_bot

    for index in range(0,2):
        bot_data = {}

        result_queue = Queue()
        time_stamp = index
        split = 50
        if time_stamp >= split:
            t1 = Thread(target=trader, args=(result_queue, price_info, time_stamp))
            t2 = Thread(target=accepter, args=(result_queue, price_info, time_stamp, order_book))
            t3 = Thread(target=bidder, args=(result_queue, price_info, time_stamp))

            t1.start()
            t2.start()
            t3.start()

            t1.join()
            t2.join()
            t3.join()
        else:
            t1 = Thread(target=trader, args=(result_queue, price_info, time_stamp))
            t2 = Thread(target=accepter, args=(result_queue, price_info, time_stamp, order_book))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

        while not result_queue.empty():
            result = result_queue.get()
            bot_data[result[0]] = result[1]
        
        if "bidder" not in bot_data:
            bot_data["bidder"] = {
                "index": {
                    "arima_bot": {
                        "share_number": 0,
                        "target_price": 0
                    }
                }
            }
        
        response = requests.request("POST", "http://127.0.0.1:5000/bot-actions", data=json.dumps(bot_data))
        print(bot_data)
        print('\n')