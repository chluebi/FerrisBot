import psycopg2
from util import parse_config

# standard database connection used by both services
def connect():
    config = parse_config('database')
    conn = psycopg2.connect(host=config['host'],
                            port=config['port'],
                            database=config['database'],
                            user=config['user'],
                            password=config['password'] if 'password' in config else None)
    return conn

conn = connect()