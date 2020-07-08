# -*- coding: utf-8 -*-
"""
This program implements Historical Value at Risk calculation for a 
portfolio of tickers with given weights. To simulate returns, it draws 
(with replacement) from historical returns for each ticker. 
Change tickers, weights, time for lookback at the top.

Created on Mon Feb 3 11:03:15 2020

@author: mroll
"""
# import some packages and use some shorthand (data, plt, pd)
from pandas_datareader import data 
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import statistics as stats # need this to take standard deviations
from random import choice # choice will select an item from list at random

def MR_get(tickers,s,e):
    stock_data = data.DataReader(tickers, data_source='yahoo', start = s, 
                       end = e)['Adj Close']
    
    return stock_data

# Initialize all the stuff you might want to change later
tickers = ['F', 'AAPL', 'GOOG'] # stock tickers go here
# Need some weights for where we have our money
weights = pd.Series(index = tickers, dtype = float)
weights[tickers]=0.33333333
start_date = '2018-1-27' # start day for lookback
end_date = '2020-1-27' # end day for lookback

# Initialize some Monte Carlo paramters
monte_carlo_runs = 1000
days_to_simulate = 5
loss_cutoff = 0.99 # count any losses larger than 5% (or -5%)

# Call that simple function we wrote above
what_we_got = MR_get(tickers, start_date, end_date)
# Compute returns from those Adjusted Closes
returns = what_we_got[tickers].pct_change()
    # This is basically what bt.get returned, just the returns
# Remove the NA from returns; we always get 1 fewer returns than data
returns = returns.dropna() # pretty easy command

# Calculate mu and sigma
mu = returns.mean() # mu was very easy using .mean method
# sigma was harder, as I couldn't do it in one line
#   the statistics package didn't know what to do without the loop
#   So I copied the mu data structure and filled it in a loop
sigma=mu.copy() # copy the mu series (a pandas datatype)
# Loop over tickers and fill sigma up with the calculated standard deviation
for i in tickers: # python loops over tickers no problem
    sigma[i]=stats.stdev(returns[i]) # fill up sigma with stdev's
# There is probably a cleaner way to do that 
'''sigma = np.std()
print(sigma)'''

# Now we can start the Monte Carlo VaR loop

compound_returns = sigma.copy()
total_simulations = 0
bad_simulations = 0
for run_counter in range(0,monte_carlo_runs): # Loop over runs    
    for i in tickers: # loop over tickers, below is done once per ticker
        # Loop over simulated days:
        compounded_temp = 1
        for simulated_day_counter in range(0,days_to_simulate): # loop over days
            simulated_return = choice(returns[i])
            compounded_temp = compounded_temp * (simulated_return + 1)        
        compound_returns[i]=compounded_temp # store compounded returns
    # Now see if those returns are bad by combining with weights
    portfolio_return = compound_returns.dot(weights) # dot product
    if(portfolio_return<loss_cutoff):
        bad_simulations = bad_simulations + 1
    total_simulations = total_simulations + 1

print("Your portfolio will lose",round((1-loss_cutoff)*100,3),"%",
      "over",days_to_simulate,"days", 
      bad_simulations/total_simulations, "of the time")
        
        
            
        
            