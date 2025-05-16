import os
import psycopg2
import time
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB', 'hello_flask_dev'),
                user=os.getenv('POSTGRES_USER', 'hello_flask'),
                password=os.getenv('POSTGRES_PASSWORD', 'hello_flask'),
                host=os.getenv('SQL_HOST', 'db'),
                port=os.getenv('SQL_PORT', '5432')
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            print("Waiting for database to be ready...")
            time.sleep(1)


def init_db():
    # Wait for database to be ready
    wait_for_db()
    # Connect to the database
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'hello_flask_dev'),
        user=os.getenv('POSTGRES_USER', 'hello_flask'),
        password=os.getenv('POSTGRES_PASSWORD', 'hello_flask'),
        host=os.getenv('SQL_HOST', 'db'),
        port=os.getenv('SQL_PORT', '5432')
    )
    try:
        # Read and execute schema.sql
        with open('/usr/src/app/schema.sql', 'r') as f:
            schema_sql = f.read()
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
