import config
import psycopg2
import pandas as pd
from datetime import datetime

def get_tickers():
	# Download current list of S&P500 companies
	SP500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
	tickers = SP500.Symbol.to_list()
	names = SP500.Security.to_list()
	tickers[65] = 'BRK-B'
	tickers[78] = 'BF-B'
	return tickers, names

def insert_stock(opt):
	conn = psycopg2.connect(opt)
	cur = conn.cursor()
	tickers, names = get_tickers()
	for ticker, name in zip(tickers, names):
		cur.execute("""
			INSERT INTO stock (ticker, name, created_date, last_updated_date)
			VALUES (%s, %s, %s, %s)
		""", (ticker, name, datetime.utcnow(), datetime.utcnow()))
	conn.commit()
	cur.close()

def main():
	opt = f"postgres://{config.username}:{config.password}@{config.host}:{config.port}/{config.cluster}.{config.db_name}?sslmode=verify-full&sslrootcert={config.cert_dir}/cc-ca.crt"
	insert_stock(opt)

if __name__ == "__main__":
    main()