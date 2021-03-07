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
		data = yf.download(symbol, period="max")
	except:
		raise Exception(f'Failed to download {symbol}.')
	data['Date'] = data.index
	data.columns = ['open_price', 'high_price', 'low_price', 'Close', 'close_price', 'volume', 'date_price']
	data['stock_id'] = symbol_id
	data['created_date'] = datetime.utcnow()
	data['last_updated_date'] = datetime.utcnow()
	columns_order = ['stock_id', 'created_date', 'last_updated_date', 'date_price', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
	data = data[columns_order]

	if len(data) > 0:
	    columns = ",".join(columns_order)

	    values = "VALUES({})".format(",".join(["%s" for _ in columns_order])) 

	    command = "INSERT INTO price ({}) {}".format(columns,values)

	    cur = conn.cursor()
	    psycopg2.extras.execute_batch(cur, command, data.values)
	    conn.commit()
	    print("Insert into price is complete")
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