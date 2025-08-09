from app import create_app
from app.utils.util import encode_token
from app.models import Mechanic, db, ServiceTicket
from datetime import datetime
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name="Jim", email="jim@email.com", phone="1234567890", password='123', salary=90000)
        self.second_mechanic = Mechanic(name="Dan", email="dan@email.com", phone="1234567892", password='123', salary=90000)
        self.ticket = ServiceTicket(VIN="123", service_date=datetime.strptime("2025-08-06","%Y-%m-%d").date(), service_desc="Car work", customer_id = 1)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.add(self.second_mechanic)
            db.session.add(self.ticket)
            self.ticket.mechanics.append(self.second_mechanic)
            db.session.commit()
        self.token = encode_token(1, "mechanic")
        self.client = self.app.test_client()
        
    # Test login
    def test_mechanic_login(self):
        login_payload= {
            "email": 'jim@email.com',
            'password': '123'
        }
        
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully logged in')
        return response.json['token']
    
    def test_mechanic_login_capital(self):
        login_payload= {
            "email": 'JIM@email.com',
            'password': '123'
        }
        
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully logged in')
        return response.json['token']
    
    def test_missing_payload_mechanic_login(self):
        login_payload= {
            "email": 'jim@email.com'
        }
        
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['password'], ['Missing data for required field.'])
    
    def test_invalid_payload_mechanic_login(self):
        login_payload= {
            "email": 'jim@email.com',
            'password': '1'
        }
        
        response = self.client.post('/mechanics/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Invalid username or password')
        
    # Test create mechanic endpoint
    def test_create_mechanic(self):
        create_payload = {
            'name': "Larry", 
            'email': "larry@email.com", 
            'phone': "1234567890", 
            'password': "123", 
            'salary': 90000
        }
        
        response = self.client.post('/mechanics/', json=create_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['email'], 'larry@email.com')
        self.assertEqual(response.json['salary'], 90000)
        
    def test_invalid_payload_create_mechanic(self):
        create_payload = {
            'email': "larry@email.com", 
            'phone': "1234567890", 
            'password': "123", 
            'salary': 90000
        }
        
        response = self.client.post('/mechanics/', json=create_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['name'], ['Missing data for required field.'])
    
    def test_duplicate_email_create_mechanic(self):
        create_payload = {
            'name': 'Larry',
            'email': "JIM@email.com", 
            'phone': "1234567890", 
            'password': "123", 
            'salary': 90000
        }
        
        response = self.client.post('/mechanics/', json=create_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Email already registered")
    
    def test_invalid_data_create_mechanic(self):
        create_payload = {
            'name': 'Larry',
            'email': "jim@email.com", 
            'phone': "1234567890", 
            'password': "123", 
            'salary': 'abc'
        }
        
        response = self.client.post('/mechanics/', json=create_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['salary'], ['Not a valid number.'])
    
    # Test get all mechanics
    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['email'], 'jim@email.com')
    
    # Test update mechanic
    def test_update_mechanic(self):
        update_payload = {
            'name': '',
            'email': '',
            'phone': '',
            'salary': 150000,
            'password': ''
        }
        
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['salary'], 150000)
        self.assertEqual(response.json['name'], 'Jim')

    
    def test_invalid_payload_update_mechanic(self):
        update_payload = {
            'email': "", 
            'phone': "", 
            'password': "", 
            'salary': 90000
        }

        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['name'], ['Missing data for required field.'])
    
    def test_duplicate_email_update_mechanic(self):
        update_payload = {
            'name': "",
            'email': "DAN@email.com", 
            'phone': "", 
            'password': "", 
            'salary': 90000
        }
        
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Duplicate email. Please use another email.")
    
    def test_invalid_mechanic_update_mechanic(self):
        update_payload = {
            "name": "Jim new",
            "email": "",
            "phone": "",
            "password": "",
            "salary": 90000
        }
        
        headers = {"Authorization": "Bearer " + self.token}
        self.client.delete('/mechanics/', headers=headers)
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Mechanic not found")

    def test_missing_token_update(self):
        update_payload = {
            'name': '',
            'email': '',
            'phone': '',
            'salary': 150000,
            'password': ''
        }
        
        response = self.client.put('/mechanics/', json=update_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "Token not found")
        
    def test_invalid_token_update(self):
        update_payload = {
            'name': '',
            'email': '',
            'phone': '',
            'salary': 150000,
            'password': ''
        }
        
        headers = {'Authorization': 'Bearer invalid'}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Invalid token')
    
    # Test delete mechanic
    def test_delete_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanic deleted')
        
    def test_delete_missing_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        self.client.delete('/mechanics/', headers=headers)
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Mechanic not found')
    
    # Test get mechanics ranked in order of most service tickets worked
    def test_ranked_mechanic(self):
        create_payload = {
            'name': "Amy", 
            'email': "amy@email.com", 
            'phone': "1234567890", 
            'password': "123", 
            'salary': 90000
        }
        
        self.client.post('/mechanics/', json=create_payload)
        
        initial = self.client.get('/mechanics/')
        response = self.client.get('/mechanics/ranked')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(initial.json[0]['name'], 'Jim')
        self.assertEqual(response.json[0]['name'], 'Dan')
        self.assertEqual(response.json[1]['name'], 'Jim')
        self.assertEqual(response.json[2]['name'], 'Amy')