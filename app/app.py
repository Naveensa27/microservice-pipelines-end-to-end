import time
import os
import logging
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
APP_PORT = int(os.getenv('APP_PORT', 5000))
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_ENV = os.getenv('APP_ENV', 'development')

# Metrics definition
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['endpoint'])
ERRORS = Counter('app_errors_total', 'Total Application Errors', ['error_type'])

@app.route('/')
def index():
    try:
        start_time = time.time()
        REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
        response = jsonify({
            "status": "healthy",
            "message": "DevOps Capstone API active",
            "environment": APP_ENV
        })
        REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start_time)
        return response, 200
    except Exception as e:
        logger.error(f"Error in index endpoint: {str(e)}")
        ERRORS.labels(error_type='index_error').inc()
        REQUEST_COUNT.labels(method='GET', endpoint='/', status='500').inc()
        return jsonify({"error": "Internal server error"}), 500

@app.route('/metrics')
def metrics():
    try:
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        ERRORS.labels(error_type='metrics_error').inc()
        return jsonify({"error": "Failed to generate metrics"}), 500

@app.route('/health')
def health():
    try:
        return jsonify({"status": "alive"}), 200
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        ERRORS.labels(error_type='health_error').inc()
        return jsonify({"status": "error"}), 500

@app.errorhandler(404)
def not_found(error):
    REQUEST_COUNT.labels(method='GET', endpoint='unknown', status='404').inc()
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    ERRORS.labels(error_type='unhandled').inc()
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask app in {APP_ENV} environment on {APP_HOST}:{APP_PORT}")
    app.run(host=APP_HOST, port=APP_PORT, debug=(APP_ENV == 'development'))