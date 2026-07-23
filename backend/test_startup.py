import unittest
from app import app

class BackendFoundationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_root_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("message", json_data)
        print("\n[PASS] Root endpoint test OK:", json_data)

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get("status"), "healthy")
        print("[PASS] Health check endpoint test OK:", json_data)

    def test_api_v1_health_check(self):
        response = self.app.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get("status"), "healthy")
        print("[PASS] API v1 Health check endpoint test OK:", json_data)

if __name__ == "__main__":
    print("Running Milestone 1 Backend Startup & Verification Test Suite...")
    unittest.main()
