FROM python:3.10-slim-bullseye

WORKDIR /app

# Install dependencies for Postgres and building wheels
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# This is the consumer, not a web server
CMD ["python", "consumer.py"]