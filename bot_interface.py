from bot_one import BotOne
from bot_three import BotThree
bot1 = BotOne()
bot2 = BotThree()

company_lst = ["ast", "dsc", "fsin", "hhw", "jky", "sgo", "wrkn"]

def trader(price_info, time_stamp, volume_info, shares=10):
    trade = {}
    for company in company_lst:
        ma_decision = bot1.stg_ma(price_info[company], time_stamp, st_moving_avg_period=15, lt_moving_avg_period=30)
        momentum_decision = bot1.stg_momentum(price_info[company], volume_info[company], time_stamp, moving_avg_period=30)
        mean_reversion_decision = bot1.stg_mean_reversion(price_info[company], time_stamp, n_std=1, moving_avg_period=30)
        donchain_decision = bot1.stg_donchian_breakout(price_info[company], time_stamp, moving_avg_period=30)
        crazy_bot_decision = bot1.crazy_trader()

        trade_company = {
            "ma_bot": {
                "share_number": ma_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "momentum_bot": {
                "share_number": momentum_decision * shares,
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
            "ma_bot": {
                "share_number": donchain_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            },
            "ma_bot": {
                "share_number": crazy_bot_decision * shares,
                "target_price": 0,
                "comp_name": company,
                "user_uid": "xxx"
            }
        }
    
        trade[company] = trade_company

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

