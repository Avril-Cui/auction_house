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
          SELECT price_list from test_prices WHERE company_id='{company_id}';
    """)
    price = list(cur.fetchone()[0])
    return price


index_price = get_price_from_database("index")[60*60*10:60*60*11]
index_price = [float(i) for i in index_price]
index_price_df = pd.DataFrame(index_price, columns=["index_price"])[
    "index_price"]
price_info = {
    "index": index_price_df
}

bot1 = BotOne()
bot2 = BotThree()

# company_lst = ["ast", "dsc", "fsin", "hhw", "jky", "sgo", "index"]
company_lst = ["index"]


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

        if ma_decision != 0:
            print(ma_decision)

        trade_company = {
            "ma_bot": {
                "share_number": ma_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "mean_reversion_bot": {
                "share_number": mean_reversion_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "donchain_bot": {
                "share_number": donchain_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "crazy_bot": {
                "share_number": crazy_bot_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
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
            "ma_bot": {
                "share_number": ma_share,
                "target_price": ma_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "mean_reversion_bot": {
                "share_number": mean_rev_share,
                "target_price": mean_rev_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "donchain_bot": {
                "share_number": donchain_share,
                "target_price": donchain_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "crazy_bot": {
                "share_number": crazy_share,
                "target_price": crazy_price,
                "comp_name": company,
                "user_uid": "xxx"
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
                "target_price": arima_price,
                "comp_name": company,
                "user_uid": "xxx"
            }
        }

        bidder[company] = bidder_company
    result_queue.put(["bider", bidder])

if __name__ == '__main__':
    for index in range(50, 60):
        bot_data = {}

        result_queue = Queue()
        time_stamp = index
        current_price = price_info["index"][time_stamp]
        order_book_index = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
        order_book = {
            "index": order_book_index
        }
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
        
        print(bot_data)
            

###testing trader
# for index in range(len(price_info["index"])):
#     time_stamp = index
#     trader_result = trader(price_info, time_stamp)
#     if trader_result["index"]["ma_bot"]["share_number"] != 0 or trader_result["index"]["mean_reversion_bot"]["share_number"] != 0 or trader_result["index"]["donchain_bot"]["share_number"] != 0 or trader_result["index"]["crazy_bot"]["share_number"] != 0:
#         print(trader_result)

### testing accepter
# for index in range(len(price_info["index"])):
#     time_stamp = index
#     current_price = price_info["index"][time_stamp]
#     order_book_index = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(
#         current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
#     order_book = {
#         "index": order_book_index
#     }
#     accepter_result = accepter(price_info, time_stamp, order_book)
#     if accepter_result["index"]["ma_bot"]["share_number"] != 0 or accepter_result["index"]["mean_reversion_bot"]["share_number"] != 0 or accepter_result["index"]["donchain_bot"]["share_number"] != 0 or accepter_result["index"]["crazy_bot"]["share_number"] != 0:
#         print(accepter_result)

### testing trader
# for index in range(50,60):
#     time_stamp = index
#     bidder_result = bidder(price_info, time_stamp)
#     print(bidder_result)