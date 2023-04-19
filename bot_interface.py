from bot_one import BotOne
from bot_three import BotThree
import psycopg2
import time
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
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
price_info = {
    "index": index_price_df
}

bot1 = BotOne()
bot2 = BotThree()

# company_lst = ["ast", "dsc", "fsin", "hhw", "jky", "sgo", "index"]
company_lst = ["index"]

def trader(price_info, time_stamp, shares=10):
    trade = {}
    for company in company_lst:
        ma_decision = bot1.stg_ma(price_info[company], time_stamp, st_moving_avg_period=15, lt_moving_avg_period=30)
        mean_reversion_decision = bot1.stg_mean_reversion(price_info[company], time_stamp, n_std=1, moving_avg_period=30)
        donchain_decision = bot1.stg_donchian_breakout(price_info[company], time_stamp, moving_avg_period=30)
        crazy_bot_decision = bot1.crazy_trader()

        if ma_decision!=0:
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
    
    return trade

###testing trader
for index in range(len(price_info["index"])):
    time_stamp = index
    trader_result = trader(price_info, time_stamp)
    if trader_result["index"]["ma_bot"]["share_number"] != 0 or trader_result["index"]["mean_reversion_bot"]["share_number"] != 0 or trader_result["index"]["donchain_bot"]["share_number"] != 0 or trader_result["index"]["crazy_bot"]["share_number"] != 0:
        print(trader_result)

def accepter(price_info, time_stamp, order_book, volume_info):
    accept = {}
    for company in company_lst:
        ma_price, ma_share, ma_score = bot1.evaluator_ma_surplus_accept(price_info[company], time_stamp, order_book[company], st_moving_avg_period=15, lt_moving_avg_period=30)
        momentum_price, momentum_share, momentum_score = bot1.evaluator_momentum_surplus_accept(price_info[company], volume_info[company], time_stamp, order_book[company], moving_avg_period=30)
        mean_rev_price, mean_rev_share, mean_rev_score = bot1.evaluator_mean_reversion_surplus_accept(price_info[company], time_stamp, order_book[company], moving_avg_period=30, n_std=1)
        donchain_price, donchain_share, donchain_score = bot1.evaluator_donchian_breakout_surplus_accept(price_info[company], time_stamp, order_book[company], moving_avg_period=30)
        crazy_price, crazy_share = bot1.crazy_accepter(order_book[company])

        accept_company = {
            "ma_bot": {
                "share_number": ma_share,
                "target_price": ma_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "momentum_bot": {
                "share_number": momentum_share,
                "target_price": momentum_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "mean_reversion_bot": {
                "share_number": mean_rev_share,
                "target_price": mean_rev_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "ma_bot": {
                "share_number": donchain_share,
                "target_price": donchain_price,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "ma_bot": {
                "share_number": crazy_share,
                "target_price": crazy_price,
                "comp_name": company,
                "user_uid": "xxx"
            }
        }
    
        accept[company] = accept_company
    return accept

def bidder(price_info, shares=10):
    bid = {}
    for company in company_lst:
        arima_price = bot2.arima_forecaster(price_info[company])
        bid_company = {
            "arima_bot": {
                "share_number": shares,
                "target_price": arima_price,
                "comp_name": company,
                "user_uid": "xxx"
            }
        }
    
        bid[company] = bid_company
    return bid
