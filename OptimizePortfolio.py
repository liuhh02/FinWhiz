import pandas as pd
import numpy as np
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import requests

def optimize_portfolio(df, portfolio_val, method="sharpe", custom_value=0):
	assets = df.columns
	#Calculate expected annualized returns & annualized sample covariance matrix
	mu = expected_returns.mean_historical_return(df)
	S = risk_models.sample_cov(df)

	# Optimize for maximal Sharpe ratio
	ef = EfficientFrontier(mu, S)
	if (method == "sharpe"):
		weights = ef.max_sharpe()
	elif (method == "min_risk"):
		weights = ef.min_volatility()
	elif (method == "custom_risk"):
		# maximises return for a given target risk
		weights = ef.efficient_risk(custom_value)
	elif (method == "custom_return"):
		# minimises risk for a given target return
		weights = ef.efficient_return(custom_value)

	cleaned_weights = ef.clean_weights()
	expectedReturns, volatility, ratio = ef.portfolio_performance(verbose=True)

	latest_prices = get_latest_prices(df)
	weights = cleaned_weights
	da = DiscreteAllocation(weights, latest_prices, total_portfolio_value = portfolio_val)
	allocation, leftover = da.lp_portfolio()

	return (expectedReturns, volatility, ratio, allocation, leftover)

def getCompanyName(ticker):
	url = f"http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={ticker}&region=1&lang=en"
	result = requests.get(url).json()
	for r in result['ResultSet']['Result']:
		if r['symbol'] == ticker:
			return r['name']

def getStockPrice(df, ticker):
	return df[ticker].iloc[-1]

def calculate_portfolio(df, allocation):
	companyName = []
	for ticker in allocation:
		companyName.append(getCompanyName(ticker))

	discrete_allocation_list = []
	for ticker in allocation:
		discrete_allocation_list.append(allocation.get(ticker))

	price_list = []
	for ticker in allocation:
		price_list.append(getStockPrice(df, ticker))

	portfolio_df = pd.DataFrame(columns=['Company Name', 'Ticker', 'Stock Price', 'Number', 'Total Cost', 'Percentage'])
	portfolio_df['Company Name'] = companyName
	portfolio_df['Ticker'] = allocation
	portfolio_df['Stock Price'] = price_list
	portfolio_df['Number'] = discrete_allocation_list
	portfolio_df['Total Cost'] = portfolio_df['Stock Price'] * portfolio_df['Number']
	portfolio_df['Percentage'] = 100 * portfolio_df['Total Cost'] / portfolio_df['Total Cost'].sum()
	portfolio_df = portfolio_df.round({'Stock Price': 0, 'Total Cost': 0, 'Percentage': 2})
	return portfolio_df