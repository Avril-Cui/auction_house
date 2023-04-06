from collections import OrderedDict
import pandas as pd
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
        n_std = 1
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

    def prepared_data(self, price_data, k):
        X_train = price_data.diff()
        signal = self.prepare_signal(price_data)
        Y_train = np.asarray(signal, dtype=int)
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, Y_train)
        predicted_signal = knn.predict(price_data)

        return predicted_signal

bot = BotThree() 
price_data = pdr.get_data_yahoo("NVDA", "2021-1-1", "2023-1-1")
bot.prepared_data(price_data["Adj Close"], 10)