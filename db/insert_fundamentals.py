import config
import psycopg2
import psycopg2.extras
import pandas as pd
import yfinance as yf
from datetime import datetime

def get_db_tickers(conn):
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT id, ticker FROM stock")
		data = cur.fetchall()
		return [(d[0], d[1]) for d in data]

def get_yfinance_data(symbol, symbol_id, conn):
	cur = conn.cursor()
	try:
		info = yf.Ticker(symbol).info
	except:
		raise Exception(f'Failed to download {symbol}.')
	fundamentals = ['longBusinessSummary', 'sector', 'sharesOutstanding', 'marketCap', 'forwardPE', 'dividendYield', 'beta', 'previousClose', 'averageVolume']
	df = pd.DataFrame([info])
	print(len(df))
	df = df[df.columns[df.columns.isin(fundamentals)]]
	df['stock_id'] = symbol_id
	df['created_date'] = datetime.utcnow()
	df['last_updated_date'] = datetime.utcnow()
	columns_order = ['stock_id', 'created_date', 'last_updated_date', 'longBusinessSummary', 'sector', 'sharesOutstanding', 'marketCap', 'forwardPE', 'dividendYield', 'beta', 'previousClose', 'averageVolume']
	df = df[columns_order]
	print(len(df))

	if len(df) > 0:
	    columns = ",".join(columns_order)

	    values = "VALUES({})".format(",".join(["%s" for _ in columns_order])) 

	    command = "INSERT INTO fundamentals ({}) {}".format(columns,values)

	    cur = conn.cursor()
	    psycopg2.extras.execute_batch(cur, command, df.values)
	    conn.commit()
	    print("Insert into fundamentals is complete")
	    cur.close()

def main():
	opt = f"postgres://{config.username}:{config.password}@{config.host}:{config.port}/{config.cluster}.{config.db_name}?sslmode=verify-full&sslrootcert={config.cert_dir}/cc-ca.crt"
	conn = psycopg2.connect(opt)

	stock_data = get_db_tickers(conn)

	for stock in stock_data:
		symbol_id = stock[0]
		symbol = stock[1]
		print(f"Currently loading {symbol}.")
		get_yfinance_data(symbol, symbol_id, conn)

if __name__ == "__main__":
    main()