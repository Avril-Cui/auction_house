from bot_one import BotOne
bot1 = BotOne

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