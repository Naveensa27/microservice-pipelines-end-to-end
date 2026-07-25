import time
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Metrics definition
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['endpoint'])

@app.route('/')
def index():
    start_time = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    response = jsonify({"status": "healthy", "message": "DevOps Capstone API active"})
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start_time)
    return response, 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)