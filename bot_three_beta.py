from cgi import test
import random
import math
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import operator

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

def euclidean_distance(instance1, instance2, length):
    distance = 0
    for x in range(1, length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)

#get k nearest neighbor
def get_neighbors(training_set, test_instance, k):
    distance = []
    length = len(test_instance) - 1

    for i in range(len(training_set)):
        #distance between the test instance and each of the training instance
        dist = euclidean_distance(test_instance, training_set.iloc[i], length)
        distance.append((training_set.iloc[i], dist))
    
    distance.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distance[x][0])
    return neighbors

#vote for classification, highest vote wins
def get_response(neighbors):
    class_votes = {}
    for i in range(len(neighbors)):
        response = neighbors[i][-1]
        if response in class_votes:
            class_votes[response] += 1
        else:
            class_votes[response] = 1
    sorted_votes = sorted(class_votes.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_votes[0][0]

def RMSD(X, Y):
    return math.sqrt(pow(Y - X, 2))

def get_accuracy(test_set, predictions):
    correct = 0
    for i in range(len(test_set)):
        if RMSD(test_set.iloc[i][-1], predictions[i]) < 1:
            correct += 1  
    return (correct/float(len(test_set))) * 100.00


def predict_and_get_accuracy(test_set, training_set, k):
    predictions = []
    for i in range(len(test_set)):
        neighbors = get_neighbors(training_set, test_set.iloc[i], k)
        result = get_response(neighbors)
        predictions.append(result)
    
    accuracy = get_accuracy(test_set, predictions)
    print('Accuracy: ' + repr(accuracy) + '%')

def predict_for(k, comp_name, price_data, split):
    training_set, test_set = prepare_data(price_data, split)
    totalCount = 0

    print("Predicting for ", comp_name)
    print("Train: " + repr(len(training_set)))
    print("Test: " + repr(len(test_set)))
    totalCount += len(training_set) + len(test_set)
    print("Total: " + repr(totalCount))

    predict_and_get_accuracy(test_set, training_set, k)

data = pdr.get_data_yahoo("AAPL", "2015-1-1", "2017-1-1")
price_data = data[['High', 'Low', "Open", "Adj Close"]]
split = 0.67

predict_for(5, "Apple", price_data, split)