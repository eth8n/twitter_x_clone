FROM postgres:13

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy schema and test data loading script
COPY schema.sql /docker-entrypoint-initdb.d/
COPY load_test_data.py /docker-entrypoint-initdb.d/
COPY requirements.txt /docker-entrypoint-initdb.d/

# Install Python dependencies
RUN pip3 install -r /docker-entrypoint-initdb.d/requirements.txt

# Make the script executable
RUN chmod +x /docker-entrypoint-initdb.d/load_test_data.py 