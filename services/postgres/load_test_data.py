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

def generate_test_data(num_rows):
    fake = Faker()
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    
    # Generate users
    users = []
    for i in range(num_rows):
        users.append((
            fake.user_name(),
            fake.email(),
            fake.date_time_between(start_date, end_date),
            fake.date_time_between(start_date, end_date),
            random.choice([True, False])
        ))
    
    # Generate tweets (10x more than users)
    tweets = []
    for i in range(num_rows * 10):
        user_id = random.randint(1, num_rows)
        content = fake.text(max_nb_chars=280)
        created_at = fake.date_time_between(start_date, end_date)
        tweets.append((
            user_id,
            content,
            created_at,
            random.randint(0, 10000),
            random.randint(0, 5000)
        ))
    
    # Generate URLs (2x more than tweets)
    urls = []
    for i in range(num_rows * 20):
        tweet_id = random.randint(1, num_rows * 10)
        url = fake.url()
        created_at = fake.date_time_between(start_date, end_date)
        urls.append((
            tweet_id,
            url,
            created_at,
            random.choice([True, False]),
            fake.date_time_between(start_date, end_date)
        ))
    
    return users, tweets, urls

def load_data(conn, users, tweets, urls):
    cur = conn.cursor()
    
    # Load users
    execute_values(cur, """
        INSERT INTO users (username, email, created_at, last_login, is_active)
        VALUES %s
    """, users)
    
    # Load tweets
    execute_values(cur, """
        INSERT INTO tweets (user_id, content, created_at, likes_count, retweets_count)
        VALUES %s
    """, tweets)
    
    # Load URLs
    execute_values(cur, """
        INSERT INTO urls (tweet_id, url, created_at, is_valid, last_checked)
        VALUES %s
    """, urls)
    
    conn.commit()
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
        
        # Generate test data
        users, tweets, urls = generate_test_data(num_rows)
        
        # Load data into database
        print("Loading data into database...")
        load_data(conn, users, tweets, urls)
        
        print("Data loading completed successfully!")
        print(f"Loaded {len(users)} users")
        print(f"Loaded {len(tweets)} tweets")
        print(f"Loaded {len(urls)} URLs")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 