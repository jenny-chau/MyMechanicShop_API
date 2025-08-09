from app import create_app
from app.models import db, Inventory, Mechanic, Customer
import unittest
from app.utils.util import encode_token

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.inventory = Inventory(name='wheels', price=10.99)
        self.mechanic = Mechanic(name="Jim", email="jim@email.com", phone="1234567890", password='123', salary=90000)
        self.customer = Customer(name='June', email='june@email.com', phone='123', password='1')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory)
            db.session.add(self.mechanic)
            db.session.add(self.customer)
            db.session.commit()
        self.mechanic_token = encode_token(1, "mechanic")
        self.customer_token = encode_token(1, 'customer')
        self.client = self.app.test_client()
        

    # test create inventory
    def test_create_inventory(self):
        create_payload = {
            'name': 'Screws',
            'price': 5.99
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'screws')
        
    def test_missing_token_create_inventory(self):
        create_payload = {
            'name': 'Screws',
            'price': 5.99
        }
        
        response = self.client.post('/inventory/', json=create_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Token not found')
        
    def test_invalid_payload_create_inventory(self):
        create_payload = {
            'name': 'Screws'
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
        
    def test_invalid_datatype_create_inventory(self):
        create_payload = {
            'name': 'Screws',
            'price': 'invalid'
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Not a valid number.'])
        
    def test_string_too_long_create_inventory(self):
        create_payload = {
            'name': 'Screws' * 100,
            'price': '1.00'
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['name'], ['Longer than maximum length 255.'])
        
    def test_duplicate_item_create_inventory(self):
        create_payload = {
            'name': 'wheels',
            'price': 10.99
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Item already exists')
        
    def test_duplicate_item_capital_create_inventory(self):
        create_payload = {
            'name': 'WHEELS',
            'price': 10.99
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/inventory/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Item already exists')
        
    #  Test get items
    def test_get_items(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'wheels')
        
    def test_get_single_item(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'wheels')
        
    def test_invalid_id_get_single_item(self):
        response = self.client.get('/inventory/200')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Item not found')
        
    # Test update item
    def test_update_item(self):
        update_payload = {
            "name": "",
            'price': 20.00
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/inventory/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['price'], 20.00)

    def test_invalid_id_update_item(self):
        update_payload = {
            "name": "",
            'price': 20.00
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/inventory/3', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Item not found')
        
    def test_invalid_payload_update_item(self):
        update_payload = {
            "name": "metal"
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/inventory/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
        
    # Test delete item
    def test_delete_item(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.delete('/inventory/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Item successfully deleted')
        
    def test_invalid_id_delete_item(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.delete('/inventory/4', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Item not found')
        
    def test_invalid_token_delete_item(self):
        headers = {'Authorization': 'Bearer ' + self.customer_token}
        response = self.client.delete('/inventory/4', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Invalid token')