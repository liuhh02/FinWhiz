import config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_db_exists(opt):
	try:
		conn = psycopg2.connect(opt)
		cur = conn.cursor()
		cur.close()
		print('Database exists.')
		return True
	except:
		print("Database doesn't exist.")
		return False

def create_db(opt):
	if check_db_exists(opt):
		pass
	else:
		print("Creating new database.")
		conn = psycopg2.connect(opt)
		conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
		cur = conn.cursor()
		cur.execute(f"CREATE DATABASE {config.db_name};")
		cur.close()

def create_tables(opt):
	if check_db_exists(opt):
		commands = (""" CREATE TABLE IF NOT EXISTS stock (
			id SERIAL PRIMARY KEY,
			ticker VARCHAR NOT NULL,
			name VARCHAR NOT NULL,
			created_date TIMESTAMP NOT NULL,
			last_updated_date TIMESTAMP NOT NULL
			)
			""",
			""" CREATE TABLE IF NOT EXISTS price (
			id SERIAL PRIMARY KEY,
			stock_id INTEGER NOT NULL,
			created_date TIMESTAMP NOT NULL,
			last_updated_date TIMESTAMP NOT NULL,
			date_price TIMESTAMP,
			open_price NUMERIC,
			high_price NUMERIC,
			low_price NUMERIC,
			close_price NUMERIC,
			volume BIGINT,
			FOREIGN KEY (stock_id) REFERENCES stock(id))
			""",
			""" CREATE TABLE IF NOT EXISTS fundamentals (
			id SERIAL PRIMARY KEY,
			stock_id INTEGER NOT NULL,
			created_date TIMESTAMP NOT NULL,
			last_updated_date TIMESTAMP NOT NULL,
			longBusinessSummary TEXT,
			sector VARCHAR,
			sharesOutstanding BIGINT,
			marketCap BIGINT,
			forwardPE REAL,
			dividendYield REAL,
			beta REAL,
			previousClose REAL,
			averageVolume BIGINT,
			FOREIGN KEY (stock_id) REFERENCES stock(id))
			""",
			""" CREATE TABLE IF NOT EXISTS news (
			id SERIAL PRIMARY KEY,
			stock_id INTEGER NOT NULL,
			news_date TIMESTAMP NOT NULL,
			headline VARCHAR NOT NULL,
			url VARCHAR NOT NULL,
			sentiment REAL,
			FOREIGN KEY (stock_id) REFERENCES stock(id))
			"""
			)
		try:
			for command in commands:
				print('Building database tables')
				conn = psycopg2.connect(opt)
				cur = conn.cursor()
				cur.execute(command)
				conn.commit()
				cur.close()
		except (Exception, psycopg2.DatabaseError) as e:
			print(e)
			cur.close()
	else:
		pass

def main():
	opt = f"postgres://{config.username}:{config.password}@{config.host}:{config.port}/{config.cluster}.{config.db_name}?sslmode=verify-full&sslrootcert={config.cert_dir}/cc-ca.crt"
	create_db(opt)
	create_tables(opt)

if __name__ == "__main__":
    main()
