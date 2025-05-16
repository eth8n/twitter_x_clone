FROM postgres:13

# Install Python and pip for data loading
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-13-rum \
    && rm -rf /var/lib/apt/lists/*

# Create Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy schema to initialization directory
COPY schema.sql /docker-entrypoint-initdb.d/

# Create a scripts directory for data loading
RUN mkdir -p /scripts
COPY load_test_data.py /scripts/
COPY requirements.txt /scripts/

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir -r /scripts/requirements.txt

# Make the data loading script executable
RUN chmod +x /scripts/load_test_data.py 