FROM python:3.10-slim-bullseye

WORKDIR /app

# Gateway needs requests and pika, usually no system dependencies needed
# But standardizing doesn't hurt.
RUN apt-get update && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gateway listens on port 3000 as per instructions
# You might need to edit app.py to listen on 3000 instead of 8080!
CMD ["python", "app.py"]