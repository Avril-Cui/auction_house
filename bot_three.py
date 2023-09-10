from collections import OrderedDict
from tracemalloc import start
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import random
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()
import warnings
warnings.filterwarnings("ignore")
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# import psycopg2
# conn = psycopg2.connect(
#     host="localhost",
#     database="aspectdatabase",
#     user="postgres",
#     password="Xiaokeai0717"
# )
# cur = conn.cursor()

# def get_price_from_database(company_id):
# 	cur.execute(f"""
#           SELECT price_list from test_prices WHERE company_id='{company_id}';
#     """)
# 	price = list(cur.fetchone()[0])
# 	return price

# index_price = get_price_from_database("index")[60*60*11:60*60*11+60*60]
# index_price = [float(i) for i in index_price]

class BotThree:
    """
        BotThree are special bots with unique algorithm/learning-based AI trading bots.
        Compared to BotOne, BotThree have more complicated strategies.
        They are more statistical and computational based.
    """

    def __init__(self) -> None:
        pass
    
    def prepare_signal1(self, price_data):
        signal = np.where(price_data.shift(-1)>price_data,1,-1)
        return signal
    
    def knn_trainer(self, price_data, k):
        price_data["diff"] = price_data["Adj Close"].diff()
        price_data = price_data.dropna()
        X = price_data[["diff"]]
        X_train = X
        Y_train = self.prepare_signal1(price_data["Adj Close"])
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, Y_train)
        return knn

    def knn_evaluator(self, knn, current_price, last_price):
        x_data = pd.DataFrame([current_price-last_price], columns=["diff"])
        X = x_data[["diff"]]
        predicted_signal = knn.predict(X)

        coefficient = predicted_signal[-1]
        return coefficient
    
    def svc_trainer(self, price_data):
        price_data["diff"] = price_data["Adj Close"].diff()
        price_data = price_data.dropna()
        X = price_data[["diff"]]
        X_train = X[:-1]
        model = SVC()
        Y_train = self.prepare_signal1(price_data["Adj Close"][:-1])
        model.fit(X_train, Y_train)
        return model

    def svc_evaluator(self, model, current_price, last_price):
        x_data = pd.DataFrame([current_price-last_price], columns=["diff"])
        X = x_data[["diff"]]
        predicted_signal = model.predict(X)

        coefficient = predicted_signal[-1]
        return coefficient
    
    def arima_forecaster(self, price_data, current_price):
        y = price_data.values
        model = ARIMA(y, order=(6, 1, 0)).fit()
        forecast = model.forecast(step=1)[0]
        if forecast > current_price:
            return 1, forecast
        elif forecast < current_price:
            return -1, forecast
        else:
            return 0, 0
        # return forecast
    
    def arima_evaluator(self, price_data, current_price):
        y = price_data.values
        model = ARIMA(y, order=(6, 1, 0)).fit()
        forecast = model.forecast(step=1)[0]
        # print(forecast)
        if forecast > current_price:
            return 1
        elif forecast < current_price:
            return -1
        else:
            return 0
    


# bot = BotThree() 
# price_data = pdr.get_data_yahoo("AAPL", "2021-1-1", "2023-1-1")
# split = 50

# z = 1
# PL = 0
# start_price = price_data["Adj Close"].iloc[split]
# end_price = price_data["Adj Close"].iloc[-1]
# Return = (PL/start_price)
# pct_return = ":.2%".format(Return)

# print("Start Price: ", round(start_price, 3))
# print("End Price: ", round(end_price, 3))


# for index in range(split+1, len(price_data)):
#     time_stamp = index
#     current_price = price_data["Adj Close"].iloc[time_stamp]
#     input_data = price_data[(time_stamp-split):time_stamp]["Adj Close"]
#     result = bot.arima_evaluator(input_data, current_price)
#     share = 50
#     if result == 1:
#         if z == 1:
#             print(f"At time {time_stamp}, Bot ARIMA buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == -1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Bot ARIMA sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1

# normal_return = round(((end_price-start_price)/start_price),4)*100
# print(f"Total return for ARIMA strategy throughout the process is {pct_return}.")
# print(f"Return of the company from beginning to end is {normal_return} %")


# bot = BotThree() 
# # price_data = pd.DataFrame(index_price, columns=["Adj Close"])
# price_data = pdr.get_data_yahoo("NVDA", "2021-1-1", "2022-1-1")
# split_percentage = 0.5
# split = int(split_percentage*len(price_data))

# z = 1
# PL = 0
# start_price = price_data["Adj Close"].iloc[split+1]
# end_price = price_data["Adj Close"].iloc[-1]
# Return = (PL/start_price)
# pct_return = ":.2%".format(Return)

# print("Start Price: ", round(start_price, 3))
# print("End Price: ", round(end_price, 3))

# print(len(price_data))
# # knn = bot.knn_trainer(price_data[:336], 8)
# svc = bot.svc_trainer(price_data[:split])

# for index in range(split+1, len(price_data)):
#     time_stamp = index
#     current_price = price_data["Adj Close"].iloc[time_stamp]
#     last_price = price_data["Adj Close"].iloc[time_stamp-1]
#     result = bot.svc_evaluator(svc, current_price, last_price)
#     share = 50
#     if result == 1:
#         if z == 1:
#             print(f"At time {time_stamp}, Bot SVC buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL - current_price
#             z = z-1
#     elif result == -1:
#         if z ==  0:
#             print(f"At time {time_stamp}, Bot SVC sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
#             PL = PL + current_price
#             Return = (PL / start_price)
#             pct_return = "{:.2%}".format(Return)
#             print("Total Profit/Loss $", round(PL, 2))
#             print("Total Return %", pct_return, "\n")
#             z = z+1

# normal_return = round(((end_price-start_price)/start_price),4)*100
# print(f"Total return for SVC strategy throughout the process is {pct_return}.")
# print(f"Return of the company from beginning to end is {normal_return} %")