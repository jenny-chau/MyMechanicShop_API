from app import create_app
from app.utils.util import encode_token
from app.models import Mechanic, db
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name="Jim", email="jim@email.com", phone="1234567890", password="123", salary="90000")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
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
            'salary': '150000',
            'password': ''
        }
        
        headers = {'Authorization': 'Bearer ' + self.test_mechanic_login()}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['salary'], 150000)
    
    # Test delete mechanic
    
    # Test get mechanics ranked in order of most service tickets worked