from collections import OrderedDict
from tracemalloc import start
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import random
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


class BotThree:
    """
        BotThree are special bots with unique algorithm/learning-based AI trading bots.
        Compared to BotOne, BotThree have more complicated strategies.
        They are more statistical and computational based.
    """

    def __init__(self) -> None:
        pass

    # def calculate_k_value(self, X_test, Y_test, X_train, Y_train, k_range=20):
    #     accuracy = []
    #     for i in range(1, k_range):
    #         knn = KNeighborsClassifier(n_neighbors=i)
    #         knn.fit(X_train, Y_train)
    #         accuracy_train = accuracy_score(Y_train, knn.predict(X_train))
    #         accuracy_test = accuracy_score(Y_test, knn.predict(X_test))
    #         print(i, accuracy_train, accuracy_test)
    #         accuracy.append(abs(accuracy_train - accuracy_test))
    #     k = accuracy.index(min(accuracy)) + 1
    #     return k
    
    def prepare_signal(self, price_data):
        signal = [0]
        n_std = 0.75
        moving_avg = price_data.rolling(window = 15).mean().to_list()
        moving_std = price_data.rolling(window = 15).std().to_list()

        for index in range(1, len(price_data)):
            upper_bound = moving_avg[index] + n_std * moving_std[index]
            lower_bound = moving_avg[index] - n_std * moving_std[index]
            if price_data.iloc[index] < lower_bound:
                signal.append(1)
            elif price_data.iloc[index] > upper_bound:
                signal.append(-1)
            else:
                signal.append(0)
        return signal

    def prepared_data(self, price_data, k):
        price_data["diff"] = price_data["Adj Close"].diff()
        price_data = price_data.dropna()
        X = price_data[["diff"]]
        X_train = X[:-1]
        signal = self.prepare_signal(price_data["Adj Close"][:-1])
        Y_train = np.asarray(signal, dtype=int)
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, Y_train)
        predicted_signal = knn.predict(X)

        coefficient = predicted_signal[-1]
        return coefficient

bot = BotThree() 
price_data = pdr.get_data_yahoo("AAPL", "2021-1-1", "2021-9-1")
bot.prepared_data(price_data, 12)

z = 1
PL = 0
start_price = price_data["Adj Close"].iloc[0]
end_price = price_data["Adj Close"].iloc[-1]
Return = (PL/start_price)
pct_return = ":.2%".format(Return)

print("Start Price: ", round(start_price, 3))
print("End Price: ", round(end_price, 3))

for index in range(30, len(price_data)):
    time_stamp = index
    current_price = price_data["Adj Close"].iloc[time_stamp]
    result = bot.prepared_data(price_data[:index], 12)

    share = 50
    if result == -1:
        if z == 1:
            print(f"At time {time_stamp}, Bot MA buys at ${round(current_price, 2)} for {abs(share)} shares. \n")
            PL = PL - current_price
            z = z-1
    elif result == 1:
        if z ==  0:
            print(f"At time {time_stamp}, Bot MA sells at ${round(current_price, 2)} for {abs(share)} shares. \n")
            PL = PL + current_price
            Return = (PL / start_price)
            pct_return = "{:.2%}".format(Return)
            print("Total Profit/Loss $", round(PL, 2))
            print("Total Return %", pct_return, "\n")
            z = z+1

normal_return = ":.2%".format((end_price-start_price)/start_price)
print(f"Total return for kNN strategy throughout the process is {pct_return}.")
print(f"Return of the company from beginning to end is {normal_return}")