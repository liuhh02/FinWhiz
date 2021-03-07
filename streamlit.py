# Import libraries
import streamlit as st
import pandas as pd
import yfinance as yf
import talib
import plotly.graph_objects as go
import plotly.express as px
import requests
import seaborn as sns
import os
from streamlit_lottie import st_lottie
from sqlalchemy import create_engine

# Import my custom scripts
from patterns import candlestick_patterns
from OptimizePortfolio import optimize_portfolio, calculate_portfolio, getCompanyName
from chart import areaChart, candlestickChart, gaugeChart, pieChart, fundamentalChart
from scan import scanStocks
from db import config
import user

db_string = f"cockroachdb://{config.username}:{config.password}@{config.host}:{config.port}/{config.cluster}.{config.db_name}?sslmode=require"
db = create_engine(db_string)

def calculateSMA(df, window):
	df[f'{window}sma'] = df['Close'].rolling(window=window).mean()

def calculateEMA(df, window):
	df[f'{window}ema'] = df['Close'].ewm(span=window).mean()

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def main():
	st.title('Stock Tracker')

	functionality = st.sidebar.selectbox('What would you like to do?',
		('Track Individual Stocks', 'Compare Company Fundamentals', 'Optimize my Portfolio',
			'Find Candlestick Patterns', 'Scan for Candlestick Patterns'))

	if (functionality == 'Track Individual Stocks'):
		st.header('Track Individual Stocks')
		ticker = st.sidebar.text_input('Enter ticker symbol', value='AMD')
		companyName = getCompanyName(ticker)
		df = user.get_db_price(ticker, db)
		st.subheader(f'Real-time information for {companyName}')
		type = st.sidebar.selectbox('Choose Chart Type', ('Line Chart', 'Candlestick Chart'))

		if (type == 'Line Chart'):
			plot = areaChart(df, ticker)
			st.plotly_chart(plot)
		
		else:
			plot = candlestickChart(df, ticker)
			st.plotly_chart(plot)
			with st.beta_expander("What is a candlestick chart?"):
				st.write("""A daily candlestick shows the market's open, high, low, and close price for the day.
					When the body of the candlestick is green, it means the close was higher than the open (ie. the price increased). 
					If the body is red, it means the close was lower than the open (ie. the price decreased).""")
				st.image("https://upload.wikimedia.org/wikipedia/commons/e/ea/Candlestick_chart_scheme_03-en.svg", use_column_width="auto")
				st.write("Probe-meteo.com, CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0>, via Wikimedia Commons")
		gauge = gaugeChart(df, ticker)
		st.plotly_chart(gauge)
		
		st.subheader(f"Fundamental Analysis of {companyName}")
		with st.beta_expander("What is Fundamental Analysis?"):
			st.write("""Fundamental analysis (FA) is a method of **measuring a security's intrinsic value** 
				by examining related economic and financial factors. These factors include macroeconomic 
				factors such as the state of the economy and industry conditions to microeconomic factors 
				like the effectiveness of the company's management. The **end goal** is to arrive at a number 
				that an investor can compare with a security's current price **in order to see whether the 
				security is undervalued or overvalued.**""")
		
		info = user.get_db_fundamentals(ticker, db)
		st.write(f"**_Business Summary_**: {info['longBusinessSummary'].values[0]}")
		st.write(f"**_Sector_**: {info['sector'].values[0]}")
		st.write(f"**_Shares Outstanding_**: {info['sharesOutstanding'].values[0]}")
		with st.beta_expander("Shares Outstanding"):
			st.write("""Shares outstanding refer to a company's stock currently held by all its 
				shareholders, including share blocks held by institutional investors and restricted 
				shares owned by the company’s officers and insiders.""")
		st.write(f"**_Market Capitalization_**: {info['marketCap'].values[0]}")
		with st.beta_expander("Market Capitalization"):
			st.write("""Market Capitalization is the total dollar value of all of a company's 
				outstanding shares. It is a measure of corporate size.""")
			st.text('Market Capital = Current Market Price * Number Of Shares Outstanding')
		st.write(f"**_Price-to-Earnings (P/E) Ratio_**: {info['forwardPE'].values[0]}")
		with st.beta_expander("P/E Ratio"):
			st.write("""The **price-to-earnings (P/E) ratio** is a metric that helps investors 
				determine the market value of a stock compared to the company's earnings. The P/E 
				ratio shows what the market is willing to pay today for a stock based on its past 
				or future earnings. The P/E ratio is important because it provides a measuring stick 
				for comparing whether a stock is overvalued or undervalued.""")
			st.write("""A **high** P/E ratio could mean that a stock's price is expensive relative to 
				earnings and **possibly overvalued**. Conversely, a **low** P/E ratio might indicate that 
				the **current stock price is cheap relative to earnings**.""")
			st.text('P/E = Average Common Stock Price / Net Income Per Share')
			st.write("""The **Forward P/E** uses forecasted earnings to calculate P/E for the next fiscal 
				year. If the earnings are expected to grow in the future, the forward P/E will be lower 
				than the current P/E.""")
			st.text('Forward P/E = Current Market Price / Forecasted Earnings Per Share')
		st.write(f"**_Dividend Yield_**: {info['dividendYield'].values[0]}")
		with st.beta_expander("Dividend Yield"):
			st.write("""The dividend yield, expressed as a percentage, is a financial ratio 
				(dividend/price) that shows how much a company pays out in dividends each year 
				relative to its stock price.""")
			st.text('Dividend Yield = Annual Dividend Per Share / Price Per Share')
			st.write("""New companies that are relatively small, but still growing quickly, may pay a 
				lower average dividend than mature companies in the same sectors. In general, mature 
				companies that aren't growing very quickly pay the highest dividend yields.""")
		st.write(f"**_Beta_**: {info['beta'].values[0]}")
		with st.beta_expander("Beta"):
			st.write("""Beta is a measure of the volatility—or systematic risk—of a security or portfolio 
				compared to the market as a whole. It effectively describes the activity of a security's 
				returns as it responds to swings in the market.""")
			st.write("If a stock has a beta of **1.0**, it indicates that its price activity is strongly correlated with the market.")
			st.write("""A beta value that is **less than 1.0** means that the security is theoretically 
				less volatile than the market. Including this stock in a portfolio makes it less risky 
				than the same portfolio without the stock.""")
			st.write("""A beta that is greater than 1.0 indicates that the security's price is 
				theoretically more volatile than the market. For example, if a stock's beta is 
				1.2, it is assumed to be 20% more volatile than the market. Technology stocks 
				and small cap stocks tend to have higher betas than the market benchmark.""")
			st.write("""A negative beta shows that the asset inversely follows the market, 
				meaning it decreases in value if the market goes up and increases if the market goes down.""")

		st.subheader("Calculate Moving Averages")
		windowSMA = st.slider("Select Simple Moving Average Period", 5, 200)
		#st.write(f"{windowSMA} Simple Moving Average selected")
		try:
			calculateSMA(df, windowSMA)
		except Exception as e:
			st.write(f"Failed to calculate {windowSMA}SMA.")

		windowEMA = st.slider("Select Exponential Moving Average Period", 5, 200)
		#st.write(f"{windowEMA} Exponential Moving Average selected")
		try:
			calculateEMA(df, windowEMA)
		except Exception as e:
			st.write(f"Failed to calculate {windowEMA}EMA.")
		plot = candlestickChart(df, ticker, sma=windowSMA, ema=windowEMA)
		st.plotly_chart(plot)

		if st.checkbox("Get Real-time News Articles"):
			st.subheader(f'Latest {companyName} News')
			df = user.get_db_news(ticker, db)
			df = df[['news_date', 'headline', 'sentiment', 'url']]
			cm = sns.diverging_palette(20, 145, as_cmap=True)
			st.dataframe(df.style.background_gradient(cmap=cm))
			mean_scores = df.groupby(['news_date']).mean()
			mean_scores = mean_scores.xs('sentiment', axis="columns").transpose()
			st.subheader('Sentiment Over Time')
			st.line_chart(mean_scores)

	elif (functionality == 'Compare Company Fundamentals'):
		st.header('Compare Company Fundamentals')
		lottie_url = load_lottieurl("https://assets10.lottiefiles.com/private_files/lf30_F3v2Nj.json")
		st_lottie(lottie_url, height=300)	
		choice = st.sidebar.selectbox("Which Companies To Compare?", ('Analyze All Companies','Custom'))
		
		if (choice == 'Analyze All Companies'):
			df = user.get_all_fundamentals(db)
			df = df.head(100)
			st.write(df)
			metric = st.selectbox('Select Metric to Visualize', ('Stock Price', 'Market Cap', 'Beta', 'Forward P/E', 'Dividend Yield', 'Average Volume'))
			number = st.slider('Number of Companies', 5, 20)
			order = st.selectbox('Ascending or Descending Order?', ('Ascending', 'Descending'))
			if metric == 'Stock Price':
				xaxis = 'previousClose'
			elif metric == 'Market Cap':
				xaxis = 'marketCap'
			elif metric == 'Beta':
				xaxis = 'beta'
			elif metric == 'Forward P/E':
				xaxis = 'forwardPE'
			elif metric == 'Dividend Yield':
				xaxis = 'dividendYield'
			elif metric == 'Average Volume':
				xaxis = 'averageVolume'
			plot = fundamentalChart(df, metric, xaxis, number, order)
			st.plotly_chart(plot)
		
		else:
			number = st.sidebar.slider('Select Number of Companies to Compare', 2, 10)
			tickers = []
			for i in range(1, number+1):
				ticker = st.sidebar.text_input(f"Enter ticker symbol {i}:")
				tickers.append(ticker)
			infos = []
			fundamentals = ['sector', 'previousClose', 'beta', 'marketCap', 'averageVolume', 'forwardPE', 'dividendYield', 'sharesOutstanding']
			if len(tickers) == number:
				for ticker in tickers:
				    print(f"Downloading data for {ticker}")
				    infos.append(yf.Ticker(ticker).info)
				df = pd.DataFrame(infos)
				df = df.set_index('symbol')
				df = df[df.columns[df.columns.isin(fundamentals)]]
				st.write(df)
	
	elif (functionality == 'Optimize my Portfolio'):
		st.header('Optimize my Portfolio')
		lottie_url = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_TWo1Pn.json")
		st_lottie(lottie_url, height=300)	
		index = st.sidebar.selectbox('Select Which Companies to Evaluate', 
			('Dow Jones Industrial Average (DJIA)', 'S&P500', 'S&P100', 'NASDAQ-100'))
		portfolio_val = int(st.sidebar.text_input("Enter Amount to Invest", value=10000))
		strategy = st.sidebar.selectbox("Select Allocation Strategy",
			('Optimize Return & Risk', 'Minimize Risk', 'Custom Risk', 'Custom Return'))
		
		if (index == 'S&P500'):
			st.subheader('S&P 500')
			st.write('''The S&P 500, or simply the S&P, is a stock market index that measures the 
				stock performance of 500 large companies listed on stock exchanges in the United 
				States. It is one of the most commonly followed equity indices. The S&P 500 index 
				is a capitalization-weighted index and the 10 largest companies in the index account 
				for 27.5% of the market capitalization of the index. The 10 largest companies in the 
				index, in order of weighting, are Apple Inc., Microsoft, Amazon.com, Facebook, Tesla, 
				Inc., Alphabet Inc. (class A & C), Berkshire Hathaway, Johnson & Johnson, and JPMorgan 
				Chase & Co., respectively.''')
			portfolio = pd.read_csv("S&P500.csv", index_col="Date")
		
		elif (index == 'S&P100'):
			st.subheader('S&P 100')
			st.write('''The S&P 100 Index is a stock market index of United States stocks maintained 
				by Standard & Poor's. It is a subset of the S&P 500 and includes 101 (because one of 
				its component companies has 2 classes of stock) leading U.S. stocks. Constituents of 
				the S&P 100 are selected for sector balance and represent about 67% of the market 
				capitalization of the S&P 500 and almost 54% of the market capitalization of the U.S. 
				equity markets as of December 2020. The stocks in the S&P 100 tend to be the largest 
				and most established companies in the S&P 500.''')
			portfolio = pd.read_csv("SP100index.csv", index_col="Date")
			with st.beta_expander("The S&P 100 consists of:"):
				tickers = portfolio.columns
				for ticker in tickers:
					st.write(f"* {getCompanyName(ticker)}")
		
		elif (index == 'NASDAQ-100'):
			st.subheader('NASDAQ-100')
			st.write('''The NASDAQ-100 is a stock market index made up of 102 equity securities issued 
				by 100 of the largest non-financial companies listed on the Nasdaq stock market.''')
			portfolio = pd.read_csv("NASDAQ.csv", index_col="Date")
			with st.beta_expander("The NASDAQ-100 consists of:"):
				tickers = portfolio.columns
				for ticker in tickers:
					st.write(f"* {getCompanyName(ticker)}")
		
		elif (index == 'Dow Jones Industrial Average (DJIA)'):
			st.subheader('Dow Jones Industrial Average (DJIA)')
			st.write('''The Dow Jones Industrial Average (DJIA), Dow Jones, or simply the Dow, is a
				stock market index that measures the stock performance of 30 large companies listed 
				on stock exchanges in the United States. It is one of the most commonly followed 
				equity indices. First calculated on May 26, 1896, the index is the second-oldest 
				among the U.S. market indices (after the Dow Jones Transportation Average). It was 
				created by Charles Dow, the editor of The Wall Street Journal and the co-founder of 
				Dow Jones & Company, and named after him and his business associate, statistician 
				Edward Jones. Although the word industrial appears in the name of the index, several 
				of the constituent companies operate in sectors of the economy other than heavy industry.''')
			portfolio = pd.read_csv("DJIA.csv", index_col="Date")
			with st.beta_expander("The DJIA consists of:"):
				tickers = portfolio.columns
				for ticker in tickers:
					st.write(f"* {getCompanyName(ticker)}")
		
		if (strategy == 'Optimize Return & Risk'):
			expectedReturns, volatility, ratio, allocation, leftover = optimize_portfolio(portfolio, portfolio_val)
		
		elif (strategy == 'Minimize Risk'):
			expectedReturns, volatility, ratio, allocation, leftover = optimize_portfolio(portfolio, portfolio_val, method="min_risk")
		
		elif (strategy == 'Custom Risk'):
			target = st.sidebar.slider("Maximise return for a chosen target risk", 15, 50)
			expectedReturns, volatility, ratio, allocation, leftover = optimize_portfolio(portfolio, portfolio_val, method="custom_risk", custom_value=target/100)
		
		elif (strategy == 'Custom Return'):
			target = st.sidebar.slider("Minimize risk for a chosen target return", 15, 50)
			expectedReturns, volatility, ratio, allocation, leftover = optimize_portfolio(portfolio, portfolio_val, method="custom_return", custom_value=target/100)
		
		portfolio_df = calculate_portfolio(portfolio, allocation)
		st.subheader('Suggested Portfolio')
		st.write(portfolio_df)
		st.write(f'**Expected annual return**: {str(round(expectedReturns*100, 2))}%')
		st.write(f'**Annual Volatility**: {str(round(volatility*100, 2))}%')
		st.write(f'**Funds Remaining**: ${str(round(leftover, 2))}')
		st.plotly_chart(pieChart(portfolio_df))

	elif (functionality == 'Find Candlestick Patterns'):
		st.header('Find Candlestick Patterns')
		ticker = st.sidebar.text_input('Enter ticker symbol', value='AAPL')
		with st.beta_expander("What are candlestick patterns?"):
			st.write("""Candlestick charts are a type of financial chart for tracking the movement of 
				securities. Each candlestick represents one day’s worth of price data about a stock 
				through four pieces of information: the opening price, the closing price, the high 
				price, and the low price.""")
			st.write("""Over time, groups of daily candlesticks fall into recognizable patterns 
				with descriptive names like *three white soldiers*, *dark cloud cover*, *hammer*, *morning 
				star*, and *abandoned baby*. Patterns form over a period of one to four weeks and are 
				a source of valuable insight into a stock’s future price action.""")
			st.write("""There are bullish and bearish candlestick patterns. **Bullish** candlestick patterns
				suggest the stock price will increase in the near future, while **bearish** candlestick
				patterns suggest the stock price will decrease in the near future.""")
		df = user.get_db_price(ticker, db)
		plot = candlestickChart(df, ticker)
		st.plotly_chart(plot)
		positive = []
		negative = []
		try:
			for key in candlestick_patterns:
				pattern_function = getattr(talib, key)
				results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
				last = results.tail(1).values[0]

				if last > 0:
					positive.append(candlestick_patterns[key])
				elif last < 0:
					negative.append(candlestick_patterns[key])

		except Exception as e:
				st.subheader(f"Failed to find patterns for {ticker}.")
		
		if (len(positive) > 0):
			st.subheader("Bullish Patterns Matched:")
			for pos in positive:
				st.write(f"* {pos}")
		else:
			st.subheader("No Bullish Patterns Matched")
		
		if (len(negative) > 0):
			st.subheader("Bearish Patterns Matched:")
			for neg in negative:
				st.write(f"* {neg}")
		else:
			st.subheader("No Bearish Patterns Matched")

	elif (functionality == 'Scan for Candlestick Patterns'):
		st.header('Scan for Candlestick Patterns')
		lottie_url = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_N1ffOJ.json")
		st_lottie(lottie_url, height=300)
		patterns = pd.DataFrame(candlestick_patterns.items(), columns=['LibName', 'Full'])
		pattern_full = st.selectbox('Choose Pattern', patterns['Full'])
		pattern = list(candlestick_patterns.keys())[list(candlestick_patterns.values()).index(pattern_full)]
		print(pattern)
		
		if (pattern == 'CDLENGULFING'):
			with st.beta_expander(f"What is the {pattern_full}?"):
				st.write(f"""The Bullish {pattern_full} is is a green candlestick that closes higher than 
					the previous day's opening after opening lower than the previous day's close. 
					It can be identified when a small red candlestick, showing a bearish trend, is 
					followed the next day by a large green candlestick, showing a bullish trend, the 
					body of which completely overlaps or engulfs the body of the previous day’s candlestick.""")
				st.image("https://a.c-dn.net/b/3i9BYH/trading-the-bullish-engulfing-candle_body_Stockbullishengulfingpatternlargerfinalfinal.png", use_column_width="auto")
				st.image("https://a.c-dn.net/b/07I4Ef/trading-the-bullish-engulfing-candle_body_2candlebulishengulfing.png", use_column_width="auto")
		
		elif (pattern == 'CDLBELTHOLD'):
			with st.beta_expander(f"What is the {pattern_full} pattern?"):
				st.write("""A belt-hold pattern suggests that a trend may be reversing and indicates investor 
					sentiment may have changed. The belt-hold pattern can be classified into two categories: 
					the bullish and bearish belt-hold.""")
				st.image("https://images.ctfassets.net/8c2uto3zas3h/4KO9peJQVLsaFqUz9Zwgjd/c2cf86bfe1639968d5cf8a1045c5a122/NAD_BlogInfographic_Candlesticks_BeltHolds.png", use_column_width="auto")
				st.write("""A **bullish belt hold** is a single bar Japanese candlestick pattern that suggests 
					a possible reversal of the prevailing downtrend. The candle opens at the low of the 
					period and subsequently rallies to close near its high, leaving a small shadow at the 
					top of the candle. The pattern surfaces after a stretch of bearish candlesticks in a 
					downtrend. The pattern closes well into the body of the previous candle, holding price 
					from falling further, hence the name "belt hold".""")
				st.write("""Conversely, a **bearish belt hold** is a candlestick pattern that forms during an 
					upward trend. It often signals a reverse in investor sentiment from bullish to bearish. 
					However, the bearish belt hold is not considered very reliable as it occurs frequently 
					and is often incorrect in predicting future share prices. As with any other candlestick 
					charting method, more than two days of trading should be considered when making 
					predictions about trends.""")
		
		else:	
			with st.beta_expander(f"What is the {pattern_full} pattern?"):
				st.write(f"The {pattern_full} is")
		
		bullish, bearish = scanStocks(pattern)
		if len(bullish) == 0 and len(bearish) == 0:
			st.subheader("No stocks currently show this pattern")
		else:
			if (len(bullish) > 0):
				st.subheader("Bullish Patterns Matched:")
				for stock in bullish:
					st.write(f"* {stock}")
					st.image(f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l", use_column_width="auto")
			if (len(bearish) > 0):
				st.subheader("Bearish Patterns Matched:")
				for stock in bearish:
					st.write(f"* {stock}")
					st.image(f"https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l", use_column_width="auto")

if __name__=='__main__':
	main()