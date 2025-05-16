#!/usr/bin/env python3
import os
import sys
import random
import string
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values
import argparse
from faker import Faker

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_user_batch(start_idx, batch_size, fake):
    users = []
    for i in range(start_idx, start_idx + batch_size):
        username = f"user_{i}"
        email = f"user_{i}@example.com"
        password_hash = fake.sha256()
        created_at = fake.date_time_between(datetime(2020, 1, 1), datetime.now())
        last_login = fake.date_time_between(datetime(2020, 1, 1), datetime.now())
        is_active = random.choice([True, False])
        users.append((username, email, password_hash, created_at, last_login, is_active))
    return users

def generate_tweet_batch(start_idx, batch_size, num_users, fake):
    tweets = []
    for i in range(start_idx, start_idx + batch_size):
        user_id = random.randint(1, num_users)
        content = fake.text(max_nb_chars=280)
        created_at = fake.date_time_between(datetime(2020, 1, 1), datetime.now())
        likes_count = random.randint(0, 10000)
        retweets_count = random.randint(0, 5000)
        tweets.append((user_id, content, created_at, likes_count, retweets_count))
    return tweets

def generate_url_batch(start_idx, batch_size, num_tweets, fake):
    urls = []
    for i in range(start_idx, start_idx + batch_size):
        tweet_id = random.randint(1, num_tweets)
        url = fake.url()
        created_at = fake.date_time_between(datetime(2020, 1, 1), datetime.now())
        is_valid = random.choice([True, False])
        last_checked = fake.date_time_between(datetime(2020, 1, 1), datetime.now())
        urls.append((tweet_id, url, created_at, is_valid, last_checked))
    return urls

def load_data_in_chunks(conn, num_rows, batch_size=1000):
    cur = conn.cursor()
    fake = Faker()
    
    print(f"Loading data in batches of {batch_size}...")
    
    # Load users in chunks
    for i in range(0, num_rows, batch_size):
        current_batch_size = min(batch_size, num_rows - i)
        users = generate_user_batch(i, current_batch_size, fake)
        execute_values(cur, """
            INSERT INTO users (username, email, password_hash, created_at, last_login, is_active)
            VALUES %s
        """, users)
        conn.commit()
        print(f"Loaded users {i+1} to {i+current_batch_size}")
    
    # Load tweets in chunks
    for i in range(0, num_rows * 10, batch_size):
        current_batch_size = min(batch_size, (num_rows * 10) - i)
        tweets = generate_tweet_batch(i, current_batch_size, num_rows, fake)
        execute_values(cur, """
            INSERT INTO tweets (user_id, content, created_at, likes_count, retweets_count)
            VALUES %s
        """, tweets)
        conn.commit()
        print(f"Loaded tweets {i+1} to {i+current_batch_size}")
    
    # Load URLs in chunks
    for i in range(0, num_rows * 20, batch_size):
        current_batch_size = min(batch_size, (num_rows * 20) - i)
        urls = generate_url_batch(i, current_batch_size, num_rows * 10, fake)
        execute_values(cur, """
            INSERT INTO urls (tweet_id, url, created_at, is_valid, last_checked)
            VALUES %s
        """, urls)
        conn.commit()
        print(f"Loaded URLs {i+1} to {i+current_batch_size}")
    
    cur.close()

def ensure_tables_exist(conn):
    cur = conn.cursor()
    
    # Read and execute schema.sql
    with open('/docker-entrypoint-initdb.d/schema.sql', 'r') as f:
        schema_sql = f.read()
        cur.execute(schema_sql)
    
    conn.commit()
    cur.close()

def clear_existing_data(conn):
    cur = conn.cursor()
    try:
        # Drop all data but keep the schema
        cur.execute("TRUNCATE urls, tweets, users CASCADE;")
        conn.commit()
    except psycopg2.Error as e:
        print(f"Warning: Could not truncate tables: {e}")
    finally:
        cur.close()

def main():
    # Check if running in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    # Set number of rows based on environment
    num_rows = 100 if is_github_actions else 1000
    
    print(f"Running in {'GitHub Actions' if is_github_actions else 'local'} environment")
    print(f"Generating {num_rows} base rows...")
    
    # Database connection parameters
    db_params = {
        'dbname': os.getenv('POSTGRES_DB', 'hello_flask_dev'),
        'user': os.getenv('POSTGRES_USER', 'hello_flask'),
        'password': os.getenv('POSTGRES_PASSWORD', 'hello_flask'),
        'host': os.getenv('POSTGRES_HOST', 'db'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        
        # Ensure tables exist
        print("Ensuring tables exist...")
        ensure_tables_exist(conn)
        
        # Clear existing data
        print("Clearing existing data...")
        clear_existing_data(conn)
        
        # Load data in chunks
        print("Loading data into database...")
        load_data_in_chunks(conn, num_rows)
        
        print("Data loading completed successfully!")
        print(f"Loaded {num_rows} users")
        print(f"Loaded {num_rows * 10} tweets")
        print(f"Loaded {num_rows * 20} URLs")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 