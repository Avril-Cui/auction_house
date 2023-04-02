from operator import index
import psycopg2
import matplotlib.pyplot as plt
from collections import OrderedDict
import pandas as pd

conn = psycopg2.connect(
    host="localhost",
    database="aspectdatabase",
    user="postgres",
    password="Xiaokeai0717"
)

cur = conn.cursor()
def get_price_from_database(company_id):
	cur.execute(f"""
          SELECT price_list from test_prices WHERE company_id='{company_id}';
        """)
	price = list(cur.fetchone()[0])
	return price

index_price = get_price_from_database("index")[0:60*60*10]

from bot_one import BotOne
bot = BotOne()

for index in range(len(index_price)):
    time_stamp = index
    current_price = index_price[time_stamp]
    ordered_book = OrderedDict(((int(current_price)+5, 10), (int(current_price)+4, 20), (int(current_price)+3, 30), (int(current_price)+2, 40), (int(current_price)+1, 50), (int(current_price)-1, -50), (int(current_price)-2, -40), (int(current_price)-3, -30), (int(current_price)-4, -20), (int(current_price)-5, -10)))
    index_price_df = pd.DataFrame(index_price, columns=["index_price"])["index_price"]  
    result = bot.evaluator_ma_surplus(index_price_df, time_stamp, ordered_book, st_moving_avg_period=15, lt_moving_avg_period=30)