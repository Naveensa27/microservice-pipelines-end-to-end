import unittest
import os
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        os.environ['APP_ENV'] = 'testing'

    def test_healthcheck(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"healthy", response.data)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_metrics_endpoint(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"http_requests_total", response.data)

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'alive')

    def test_404_endpoint(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Endpoint not found", response.data)

    def test_environment_variable_in_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('environment', data)

if __name__ == '__main__':
    unittest.main()