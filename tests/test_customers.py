from app import create_app
from app.models import db, Customer, ServiceTicket
from app.utils.util import encode_token
from datetime import datetime
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="Wasabi", email="wasabi@email.com", phone="1234567890", password="123")
        self.ticket = ServiceTicket(VIN="123", service_date=datetime.strptime("2025-08-06","%Y-%m-%d").date(), service_desc="Car work", customer_id = 1)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.ticket)
            db.session.commit()
        self.token = encode_token(1, "customer")
        self.client = self.app.test_client()
        
    # Test create customer endpoint
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
        
    def test_duplicate_email_create_customer(self):
        customer_payload = {
            "name": "Wasabi",
            "email": "wasabi@email.com",
            "phone": "123345434",
            "password": "123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Customer exists already")
    
    def test_duplicate_email_capital_create_customer(self):
        customer_payload = {
            "name": "Wasabi",
            "email": "WASABI@email.com",
            "phone": "123345434",
            "password": "123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Customer exists already")
    
    
    # Test customer login endpoint
    def test_customer_login(self):
        login_payload = {
            "email": "wasabi@email.com",
            "password": "123"
        }
        
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Successfully logged in")
        return response.json["auth_token"]
    
    def test_capital_customer_login(self):
        login_payload = {
            "email": "WASABI@email.com",
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
        
    def test_invalid_payload_login(self):
        login_payload = {
            "email": "wasabi@email.com"
        }
        
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["password"], ["Missing data for required field."])
        
    # Test get customer endpoint
    def test_get_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]["email"], "wasabi@email.com")

        
    def test_get_customer_by_id(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["email"], "wasabi@email.com")
        
    def test_invalid_get_customer_by_id(self):
        response = self.client.get('/customers/4')
        self.assertEqual(response.status_code, 404) 
        self.assertEqual(response.json['error'], 'Customer not found')
        
    # Test update customer endpoint
    def test_update_customer(self):
        update_payload = {
            "name": "",
            "email": "",
            "phone": "",
            "password": "1234"
        }
        
        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Wasabi")
        self.assertEqual(response.json['password'], "1234")
        
    def test_invalid_payload_update_customer(self):
        update_payload = {
            "email": "",
            "phone": "",
            "password": "1234"
        }
        
        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['name'], ['Missing data for required field.'])
        
    def test_duplicate_email_update_customer(self):
        update_payload = {
            "name": "",
            "email": "sashimi@email.com",
            "phone": "",
            "password": "1234"
        }
        
        customer_payload = {
            "name": "Sashimi",
            "email": "sashimi@email.com",
            "phone": "1234567890",
            "password": "123"
        }
        
        self.client.post('/customers/', json=customer_payload)
        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "email already exists. Please use another email.")

    def test_duplicate_email_capital_update_customer(self):
            update_payload = {
                "name": "Wasabi",
                "email": "SASHIMI@email.com",
                "phone": "123345434",
                "password": "123"
            }
            
            new_customer_payload = {
            "name": "Sashimi",
            "email": "sashimi@email.com",
            "phone": "1234567890",
            "password": "123"
            }
            self.client.post('/customers/', json=new_customer_payload)
            headers = {"Authorization": "Bearer " + self.token}
            response = self.client.put('/customers/', json=update_payload, headers=headers)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["error"], "email already exists. Please use another email.")
    
    def test_invalid_customer_update_customer(self):
        update_payload = {
            "name": "Wasabi new",
            "email": "",
            "phone": "",
            "password": ""
        }
        
        headers = {"Authorization": "Bearer " + self.token}
        self.client.delete('/customers/', headers=headers)
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Customer not found")
        
    def test_missing_token_update_customer(self):
        update_payload = {
            "name": "Wasabi new",
            "email": "",
            "phone": "",
            "password": ""
        }
        
        response = self.client.put('/customers/', json=update_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "Token not found")
        
    def test_invalid_token(self):
        headers = {"Authorization": "Bearer invalid"}
        response = self.client.put('/customers/', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "Invalid token")

    # Test delete customer route
    def test_delete_customer(self):
        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Customer successfully deleted")
        
    def test_delete_nonexistant_customer(self):
        headers = {"Authorization": "Bearer " + self.token}
        self.client.delete('/customers/', headers=headers)
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Customer not found")
        
    # Test the route to get all service tickets associated with customer
    def test_get_service_tickets(self):
        headers = {"Authorization": "Bearer " + self.token}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]["VIN"], "123")
        
    def test_invalid_customer_get_tickets(self):        
        headers = {"Authorization": "Bearer " + self.token}
        self.client.delete('/customers/', headers=headers)
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "customer not found")
