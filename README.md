# Aspect Trading Bots

## Introduction to Aspect
Aspect is an educational website that gamifies the process of learning finance. Users can learn how to make investment decisions through trading in a dynamic and intense virtual stock market.
In the Aspect stock market, all stocks and the indices are virtual, with characteristics resembling the real-world. One interesting trait of the Aspect stock market is that there is always some intense financial events happening to the market and each individual companies. Through gaming, users could learn how to correctly and rationally make investment strategies when facing major opportunities or risks.

## Auction House and Bots
Contary to stock simulations currently available in the market, in the Aspect stock market, users have influences on the stock prices.
Through puting buy or sell orders in the auction house, users' demands and supplies affect the equilibrium prices.
Besides users, there are trading bots present in the stock market constantly buying and selling. Each instance of the trading bot has an unique trading
strategy that either mocks a type of investor or implemented a statistical learning model.

## Bot Type One
In Aspect, prices of companies and indices were simulated through stochastic differential equations. The details of the model could be found in https://github.com/Avril-Cui/AspectPython.
Bot type one are bots that always buy and sell at the model-generated price at a given timestamp t.

## Bot Type Two
Bot type two contains bots that follows economic-gaming strategies or commonly-used algorithm/technical trading strategies.
Most strategies in Bot Type Two are simple and straightforward, aiming to modifies different types of investors existing in the market, such as
"buy high, sell low" or "buy low, sell high" strategies.

## Bot Type Three
Bot type three contains AI bots with more advanced strategy models, primarily statistical learning models such as K-Nearest Neighbors (kNN), Support Vector Classifier (SVC), and Autoregressive Integrated Moving Average (ARIMA).
These strategies are more complicated compared to Bot Two and are commonly used in HFTs and algorithm tradings.
This type aims to experiment the performance of more complicated statistical model's performance in a stock market with exceptional events, such as the stock market facing an economic crisis, a stock boom, or in the Aspect stock market.


