import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from OptimizePortfolio import getCompanyName

def areaChart(df, ticker):
	c_area = px.area(df, x="Date", y="Close", title = f'{ticker} SHARE PRICE')

	c_area.update_xaxes(
	    title_text = 'Date',
	    rangeslider_visible = True,
	    rangeselector = dict(
	        buttons = list([
	            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
	            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
	            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
	            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
	            dict(step = 'all')])))

	c_area.update_yaxes(title_text = f'{ticker} Close Price', tickprefix = '$')
	c_area.update_layout(showlegend = False,
	    title = {
	        'text': f'{ticker} SHARE PRICE',
	        'y':0.9,
	        'x':0.5,
	        'xanchor': 'center',
	        'yanchor': 'top'})

	return c_area

def candlestickChart(df, ticker, sma=0, ema=0):
	candlestick = go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="candlesticks")
	if (sma!=0 and ema!=0):
		sma = go.Scatter(x=df['Date'], y=df[f'{sma}sma'], name=f"{sma}SMA", line={'color': '#17BECF'})
		ema = go.Scatter(x=df['Date'], y=df[f'{ema}ema'], name=f"{ema}EMA", line={'color': '#B279A2'})
		fig = go.Figure(data=[candlestick, sma, ema])
		fig.update_layout(xaxis_rangeslider_visible=False)
		fig.update_layout(title='Candlestick chart with moving averages', yaxis_title=f"{ticker} Stock")
	else:
		fig = go.Figure(data=candlestick)
		fig.update_layout(title='Candlestick chart', yaxis_title=f"{ticker} Stock")
	fig.update_xaxes(
	    title_text = 'Date',
	    rangeslider_visible = True,
	    rangeselector = dict(
	        buttons = list([
	            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
	            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
	            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
	            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
	            dict(step = 'all')])))
	fig.update_yaxes(tickprefix = '$')
	return fig

def gaugeChart(df, ticker):
	high = df['High'].max()
	gauge = go.Figure(go.Indicator(
	    domain = {'x': [0, 1], 
	              'y': [0, 1]},
	    value = int(df['Close'].tail(1)),
	    mode = "gauge+number+delta",
	    title = {'text':f"<b>{ticker} STOCK PRICE DAY RANGE</b><br><span style='color: gray; font-size:0.8em'>USD $</span>", 
	             'font': {"size": 20}},
	    delta = {'reference': int(df['Close'].iloc[-2])},
	    gauge = {
	             'axis': {'range': [None, high]},
	             'steps' : [
	                 {'range': [0, 3/4 * high], 'color': "lightgray"},
	                 {'range': [3/4 * high, high], 'color': "gray"}]}))
	return gauge

def pieChart(df):
	fig = px.pie(df, values='Percentage', names='Company Name', title='Portfolio Allocation')
	return fig

def fundamentalChart(df, metric, xaxis, number, order):
	subset = df[['symbol', xaxis]]
	subset['name'] = subset['symbol'].apply(lambda x: getCompanyName(x))
	if order == 'Ascending':
		subset = subset.sort_values(by=[xaxis])
	else:
		subset = subset.sort_values(by=[xaxis], ascending=False)
	subset = subset.head(number)
	fig = px.bar(subset, x='name', y=xaxis, color=xaxis)
	fig.update_yaxes(title_text = metric)
	return fig
