import pika
import json
import os
import sys
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Configuration
# We connect to localhost because this script runs on the SAME VM as RabbitMQ
RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
QUEUE_NAME = 'billing_queue'

# Database Config
DB_USER = os.environ.get('POSTGRES_USER', 'myuser')
DB_PASS = os.environ.get('POSTGRES_PASSWORD', 'mypassword')
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_NAME = os.environ.get('POSTGRES_DB', 'billing_db')

DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# 2. Database Model
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    number_of_items = Column(String)
    total_amount = Column(String)

# 3. Init DB Connection
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(engine)
            print(" [x] Database initialized (Tables created)")
            return True
        except Exception as e:
            print(f" [!] Database not ready yet: {e}")
            print(" ... Retrying DB connection in 5s ...")
            time.sleep(5)
            retries -= 1
    print(" [!] Could not connect to DB after multiple retries.")
    return False


# 4. The Logic (What happens when a message arrives?)
def process_message(ch, method, properties, body):
    print(f" [->] Received message: {body}")
    
    try:
        data = json.loads(body)
        
        # Open a session, do work, close session
        session = Session()
        new_order = Order(
            user_id=str(data.get('user_id')),
            number_of_items=str(data.get('number_of_items')),
            total_amount=str(data.get('total_amount'))
        )
        session.add(new_order)
        session.commit()
        session.close()
        
        print(" [x] Order saved to Database!")
        
        # CRITICAL: Tell RabbitMQ we are done. 
        # If we don't do this, RabbitMQ will hold the message forever.
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f" [!] Error: {e}")

# 5. The Main Loop
def start_consuming():
    print(f" [*] Connecting to RabbitMQ at {RABBIT_HOST}...")
    
    # Retry logic (in case RabbitMQ is still starting up)
    while True:
        try:
            RABBIT_USER = os.environ.get('RABBIT_USER', 'myuser')
            RABBIT_PASS = os.environ.get('RABBIT_PASS', 'mypassword')

            credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
            
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST,credentials=credentials))
            break
        except pika.exceptions.AMQPConnectionError:
            print(" ... RabbitMQ not ready, retrying in 5s ...")
            time.sleep(5)

    channel = connection.channel()
    
    # Create the queue if it doesn't exist
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    # Tell RabbitMQ: "Don't send me a new message until I ack the previous one"
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    # Initialize DB first, then start listening
    init_db()
    try:
        start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)