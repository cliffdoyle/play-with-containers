# 1. Base Image: Python on Debian Bullseye (Slim version)
FROM python:3.10-slim-bullseye

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies (needed for psycopg2)
# We clean up apt cache afterwards to keep the image small
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# 4. Copy requirements first! (Docker Layer Caching)
# If requirements didn't change, Docker skips this step to build faster.
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Command to run the application
# Note: We run on port 8080 as requested
CMD ["python", "app.py"]