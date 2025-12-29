import os
import json
import requests
import pika
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(
    __name__,
    static_folder='static',
    static_url_path='/static'
)


# --- CONFIGURATION ---
# 1. Inventory Service URL (HTTP)
# Note: We use the Private IP of the Inventory VM
INVENTORY_URL = os.environ.get('INVENTORY_URL', 'http://192.168.56.11:5000/api/movies')

# 2. Billing Service Config (RabbitMQ)
# Note: We use the Private IP of the Billing VM
RABBIT_HOST = os.environ.get('RABBIT_HOST', '192.168.56.12')
QUEUE_NAME = 'billing_queue'

# --- HELPER: SEND TO RABBITMQ ---
def publish_to_queue(message_dict):
    try:
          # DEFINE CREDENTIALS
        credentials = pika.PlainCredentials('myuser', 'mypassword')

        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials))
        channel = connection.channel()
        
        # Ensure queue exists
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        
        # Send message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message_dict),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return False

# --- ROUTES ---

# 1. INVENTORY ROUTE (The Proxy)
# We capture ALL methods (GET, POST, DELETE) and just forward them.
@app.route('/api/movies', methods=['GET', 'POST', 'DELETE'])
@app.route('/api/movies/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def inventory_proxy(path=''):
    # Construct the destination URL
    # If path exists, append it. e.g. /api/movies/1
    url = f"{INVENTORY_URL}/{path}" if path else INVENTORY_URL
    
    # Forward the request
    # requests.request() lets us pass the method, headers, and body dynamically
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        json=request.get_json() if request.is_json else None
    )
    
    # Return the response from Inventory back to the Client
    return (resp.content, resp.status_code, resp.headers.items())

# 2. BILLING ROUTE (The Fire-and-Forget)
@app.route('/api/billing', methods=['POST'])
def billing_ingest():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # Send to RabbitMQ
    success = publish_to_queue(data)
    
    if success:
        # Immediate response. We don't wait for the database save!
        return jsonify({"message": "Order queued for processing", "status": "queued"}), 200
    else:
        return jsonify({"error": "Failed to queue order"}), 500

if __name__ == '__main__':
    # CRITICAL: We run on port 8080 because Vagrant forwards host:8080 -> guest:8080
    app.run(host='0.0.0.0', port=3000)


SWAGGER_URL = '/docs'
API_URL = '/static/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Movie Platform Gateway API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
