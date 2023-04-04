import random
import math
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()

# split the data into a trainingdataset and testdataset in ratio of 67/33
def prepare_data(price_data, split):
    training_set = pd.DataFrame()
    test_set = pd.DataFrame()
    for index in range(len(price_data)):
        if random.random() < split:
            training_set = training_set.append(price_data.iloc[index])
        else:
            test_set = test_set.append(price_data.iloc[index])
    
    return training_set, test_set