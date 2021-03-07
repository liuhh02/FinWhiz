import config
import psycopg2
import psycopg2.extras
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

def get_db_tickers(conn):
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT id, ticker FROM stock")
		data = cur.fetchall()
		return [(d[0], d[1]) for d in data]

def get_news_data(symbol, symbol_id, conn):
	cur = conn.cursor()
	print(f"Getting data for {symbol}")
	finwiz_url = 'https://finviz.com/quote.ashx?t='
	url = finwiz_url + symbol
	req = Request(url=url,headers={'user-agent': 'Mozilla/5.0'}) 
	response = urlopen(req)
	html = BeautifulSoup(response, features='lxml')
	news_table = html.find(id='news-table')

	parsed_news = []

	for x in news_table.findAll('tr'):
		text = x.a.get_text() 
		url = x.a['href']
		date_scrape = x.td.text.split()
		if (len(date_scrape) == 1):
			time = date_scrape[0]
		else:
			date = date_scrape[0]
			time = date_scrape[1]
		parsed_news.append([date, time, text, url])

	vader = SentimentIntensityAnalyzer()
	columns = ['date', 'time', 'headline', 'url']
	df = pd.DataFrame(parsed_news, columns=columns)
	scores = df['headline'].apply(vader.polarity_scores).tolist()
	scores_df = pd.DataFrame(scores)
	df = df.join(scores_df, rsuffix='_right')
	df['date'] = pd.to_datetime(df['date'] + ' ' + df['time'])
	df = df[['date', 'headline', 'url', 'compound']]
	df = df[(df.compound != 0.0000)]
	df['stock_id'] = symbol_id
	df.columns = ['news_date', 'headline', 'url', 'sentiment', 'stock_id']
	columns_order = ['stock_id', 'news_date', 'headline', 'url', 'sentiment']
	df = df[columns_order]

	if len(df) > 0:
	    columns = ",".join(columns_order)

	    values = "VALUES({})".format(",".join(["%s" for _ in columns_order])) 

	    command = "INSERT INTO news ({}) {}".format(columns,values)

	    cur = conn.cursor()
	    psycopg2.extras.execute_batch(cur, command, df.values)
	    conn.commit()
	    print("Insert into news is complete")
	    cur.close()

def main():
	opt = f"postgres://{config.username}:{config.password}@{config.host}:{config.port}/{config.cluster}.{config.db_name}?sslmode=verify-full&sslrootcert={config.cert_dir}/cc-ca.crt"
	conn = psycopg2.connect(opt)

	stock_data = get_db_tickers(conn)

	for stock in stock_data:
		symbol_id = stock[0]
		symbol = stock[1]
		print(f"Currently loading {symbol}.")
		get_news_data(symbol, symbol_id, conn)

if __name__ == "__main__":
    main()