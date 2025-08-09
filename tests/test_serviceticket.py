from app import create_app
from app.models import db, ServiceTicket, Mechanic, Customer, Inventory
import unittest
from datetime import datetime
from app.utils.util import encode_token

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="Wasabi", email="wasabi@email.com", phone="1234567890", password="123")
        self.ticket = ServiceTicket(VIN="123", service_date=datetime.strptime("2025-08-06","%Y-%m-%d").date(), service_desc="Car work", customer_id = 1)
        self.mechanic = Mechanic(name="Jim", email="jim@email.com", phone="1234567890", password='123', salary=90000)
        self.mechanic_two = Mechanic(name="Dan", email="dan@email.com", phone="1234567890", password='123', salary=90000)
        self.item = Inventory(name='wheels', price=29.99)
        self.item_two = Inventory(name='screw', price=5.00)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.ticket)
            db.session.add(self.mechanic)
            db.session.add(self.mechanic_two)
            db.session.add(self.item)
            db.session.add(self.item_two)
            db.session.commit()
        self.customer_token = encode_token(1, 'customer')
        self.mechanic_token = encode_token(1, 'mechanic')
        self.client = self.app.test_client()
        
    # Test create service ticket
    def test_create_ticket(self):
        create_payload = {
            "VIN": "123",
            'service_date': '2025-08-10',
            'service_desc': 'Tire rotation'
        }
        
        headers = {'Authorization': 'Bearer ' + self.customer_token}
        response = self.client.post('/serviceticket/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], '123')
        
    def test_invalid_payload_create_ticket(self):
        create_payload = {
            'service_date': '2025-08-10',
            'service_desc': 'Tire rotation'
        }
        
        headers = {'Authorization': 'Bearer ' + self.customer_token}
        response = self.client.post('/serviceticket/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['VIN'], ['Missing data for required field.'])
        
    def test_invalid_date_create_ticket(self):
        create_payload = {
            'VIN': '123',
            'service_date': '08-23-2025',
            'service_desc': 'Tire rotation'
        }
        
        headers = {'Authorization': 'Bearer ' + self.customer_token}
        response = self.client.post('/serviceticket/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['service_date'], ['Not a valid date.'])

    def test_invalid_token_create_ticket(self):
        create_payload = {
            'VIN': '123',
            'service_date': '08-23-2025',
            'service_desc': 'Tire rotation'
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.post('/serviceticket/', json=create_payload, headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Invalid token')

    # Test assign logged in mechanic
    def test_assign_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanic 1 added to Service Ticket #1')
        
        response_two = self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        self.assertEqual(response_two.status_code, 200)
        self.assertEqual(response_two.json['message'], 'Mechanic already assigned to service ticket')
        
    def test_invalid_ticket_assign_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/10/assign-mechanic', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Service Ticket not found')
        
    # Test remove logged in mechanic
    def test_remove_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/1/remove-mechanic', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Mechanic not currently assigned to ticket')
        
        response_two = self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        self.assertEqual(response_two.status_code, 200)
        self.assertEqual(response_two.json['message'], 'Mechanic 1 added to Service Ticket #1')
        
        response_three = self.client.put('/serviceticket/1/remove-mechanic', headers=headers)
        self.assertEqual(response_three.status_code, 200)
        self.assertEqual(response_three.json['message'], 'Mechanic successfully removed from Service Ticket #1')
        
        
    def test_invalid_ticket_remove_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/10/remove-mechanic', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Service ticket or mechanic not found')
        
    # Test get all service tickets
    def test_get_service_tickets(self):
        create_payload = {
            "VIN": "123",
            'service_date': '2025-08-10',
            'service_desc': 'Tire rotation'
        }
        
        headers = {'Authorization': 'Bearer ' + self.customer_token}
        self.client.post('/serviceticket/', json=create_payload, headers=headers)

        response = self.client.get('/serviceticket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_date'], '2025-08-06')
        self.assertEqual(response.json[1]['service_date'], '2025-08-10')

    # Test edit ticket
    def test_edit(self):
        edit_payload = {
            'add_mechanic_ids': [1, 2]
        }
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/1/edit', json=edit_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'][0]['name'], 'Jim')
        self.assertEqual(response.json['mechanics'][1]['name'], 'Dan')
        self.assertEqual(len(response.json['mechanics']), 2)
        
        edit_payload_two = {
            'remove_mechanic_ids': [1]
        }
        
        response = self.client.put('/serviceticket/1/edit', json=edit_payload_two, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'][0]['name'], 'Dan')
        self.assertEqual(len(response.json['mechanics']), 1)
        
        edit_payload_three = {
            'add_mechanic_ids': [1],
            'remove_mechanic_ids': [2]
        }
        
        response = self.client.put('/serviceticket/1/edit', json=edit_payload_three, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'][0]['name'], 'Jim')
        self.assertEqual(len(response.json['mechanics']), 1)
        
    def test_invalid_ticket_edit(self):
        edit_payload = {
            'add_mechanic_ids': [1, 2],
            'remove_mechanic_ids': []
        }
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/10/edit', json=edit_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'no ticket found')
    
    def test_invalid_mechanic_edit(self):
        edit_payload = {
            'add_mechanic_ids': [1, 7]
        }
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/1/edit', json=edit_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'One or more mechanics not found')
        
        edit_payload = {
            'remove_mechanic_ids': [1, 7]
        }
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/1/edit', json=edit_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'One or more mechanics not found')
        
    # Test add items
    def test_add_items(self):
        add_item_payload = {
            'ticket_id': 1,
            'item_quant': [
                {
                    'item_id': 1,
                    'quantity': 2
                },
                {
                    'item_id': 2,
                    'quantity': 10
                }
                ]
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        response = self.client.put('/serviceticket/add_items', json=add_item_payload, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['items'][0]['item']['name'], 'wheels')
        self.assertEqual(response.json['items'][0]['quantity'], 2)
        self.assertEqual(response.json['items'][1]['item']['name'], 'screw')
        self.assertEqual(response.json['items'][1]['quantity'], 10)
        
    def test_invalid_payload_add_items(self):
        add_item_payload = {
            'item_quant': [
                {
                    'item_id': 1,
                    'quantity': 2
                },
                {
                    'item_id': 2,
                    'quantity': 10
                }
                ]
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        response = self.client.put('/serviceticket/add_items', json=add_item_payload, headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['ticket_id'], ['Missing data for required field.'])
        
    def test_invalid_mechanic_add_items(self):
        add_item_payload = {
            'ticket_id': 1,
            'item_quant': [
                {
                    'item_id': 1,
                    'quantity': 2
                },
                {
                    'item_id': 2,
                    'quantity': 10
                }
                ]
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        response = self.client.put('/serviceticket/add_items', json=add_item_payload, headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Not authorized to make adjustments to this ticket')
        
    def test_invalid_ticket_add_items(self):
        add_item_payload = {
            'ticket_id': 10,
            'item_quant': [
                {
                    'item_id': 1,
                    'quantity': 2
                },
                {
                    'item_id': 2,
                    'quantity': 10
                }
                ]
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        response = self.client.put('/serviceticket/add_items', json=add_item_payload, headers=headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'no ticket found')
    
    def test_invalid_item_add_items(self):
        add_item_payload = {
            'ticket_id': 1,
            'item_quant': [
                {
                    'item_id': 1,
                    'quantity': 2
                },
                {
                    'item_id': 20,
                    'quantity': 10
                }
                ]
        }
        
        headers = {'Authorization': 'Bearer ' + self.mechanic_token}
        self.client.put('/serviceticket/1/assign-mechanic', headers=headers)
        response = self.client.put('/serviceticket/add_items', json=add_item_payload, headers=headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Item not found')