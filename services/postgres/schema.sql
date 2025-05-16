-- Performance optimization settings for search
SET work_mem = '128MB';               -- Higher memory for sorting operations
SET maintenance_work_mem = '256MB';   -- Higher memory for maintenance operations
SET random_page_cost = 1.1;           -- Optimize for SSD storage
SET effective_cache_size = '6GB';     -- Increase cache estimate
SET cpu_tuple_cost = 0.01;            -- Reduce cost estimate for CPU operations
SET cpu_index_tuple_cost = 0.001;     -- Favor index scans

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create tweets table
CREATE TABLE IF NOT EXISTS tweets (
    tweet_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    retweets_count INTEGER DEFAULT 0,
    CONSTRAINT content_length CHECK (char_length(content) <= 280)
);

-- Add FTS support
ALTER TABLE tweets ADD COLUMN IF NOT EXISTS content_tsv tsvector
GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

-- Create RUM index for FTS
CREATE EXTENSION IF NOT EXISTS rum;
DROP INDEX IF EXISTS idx_tweets_content_rum;
CREATE INDEX idx_tweets_content_rum ON tweets USING rum (content_tsv rum_tsvector_ops, created_at);

-- Create urls table
CREATE TABLE IF NOT EXISTS urls (
    url_id SERIAL PRIMARY KEY,
    tweet_id INTEGER NOT NULL REFERENCES tweets(tweet_id),
    url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_tweets_user_id ON tweets(user_id);
CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at);
CREATE INDEX IF NOT EXISTS idx_urls_tweet_id ON urls(tweet_id);
CREATE INDEX IF NOT EXISTS idx_urls_url ON urls(url);

-- Add additional indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_tweets_content_gin ON tweets USING gin (to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_tweets_created_at_btree ON tweets USING btree (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tweets_user_id_created_at ON tweets (user_id, created_at DESC);

