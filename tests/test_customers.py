from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="Wasabi", email="wasabi@email.com", phone="1234567890", password="123")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1, "customer")
        self.client = self.app.test_client()
        
    def test_create_customer(self):
        customer_payload = {
            "name": "Sashimi",
            "email": "sashimi@email.com",
            "phone": "1234567890",
            "password": "123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Sashimi")
        
    def test_invalid_create_customer(self):
        customer_payload = {
            "name": "Wasabi",
            "email": "wasabi@email.com",
            "password": "123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["phone"], ["Missing data for required field."])
        
    def test_customer_login(self):
        login_payload = {
            "email": "wasabi@email.com",
            "password": "123"
        }
        
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Successfully logged in")
        return response.json["auth_token"]
    
    def test_invalid_login(self):
        login_payload = {
            "email": "w@email.com",
            "password": "123"
        }
        
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"], "Invalid username or password")