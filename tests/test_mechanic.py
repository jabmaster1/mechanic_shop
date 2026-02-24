from application.__init__ import create_app
from application.models import db, Mechanic, Inventory, Customer, Ticket
from application.utils.util import encode_token, mechanic_required
from datetime import date
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name = 'test_mechanic', email = 'test@email.com', phone = '444-555-7777', salary = 50000.00, password = 'test')
        self.customer = Customer(id= 1, name = 'test_user', email = 'test@email.com', phone = '111-222-3333', password = 'test')
        self.ticket = Ticket(id= 1, VIN= '123456789', service_date= date(2026, 2, 23), service_desc='Needs work', customer_id= 1, mechanic_id= 1)
        self.inventroy_item = Inventory(id= 1, name= 'Brake Pad', price=10.0)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.add(self.customer)
            db.session.add(self.inventroy_item)
            db.session.add(self.ticket)
            db.session.commit()
        self.token = encode_token(1, 'mechanic')
        self.client = self.app.test_client()
    
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "789-456-1238",
            "salary": 50000.00,
            "password": "password123"
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertEqual(data['name'], "John Doe")

    def test_login_mechanic(self):
        credentials = {
            "email": 'test@email.com',
            "password": 'test'
        }
        
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']

    def test_update_mechanic_by_ID(self):
        update_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "789-456-1238",
            "salary": 100000.00,
            "password": "password123"
        }
        
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        
        response = self.client.put('/mechanics/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Doe')
        self.assertEqual(response.json['email'], 'jd@email.com')
    
    def test_delete_mechanic_by_ID(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        
        response = self.client.delete('/mechanics/1', headers=headers)
        
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Mechanic deleted successfully.')
    
    def test_get_top_mechanics(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.get('/mechanics/top', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertIsInstance(data, list)
        
    def test_get_all_mechanics(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.get('/mechanics/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertIsInstance(data, list)
        
    def test_get_all_customers(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.get('/customers/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertIsInstance(data, list)
    
    def test_get_customer_by_ID(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.get('/customers/1', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertIsInstance(data, dict)
        
    def test_create_a_ticket(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        
        ticket_payload = {
            "VIN": "987654321",
            "service_date": "2025-12-11",
            "service_desc": "Needs more work",
            "customer_id": 1,
            "mechanic_id": 1
        }

        response = self.client.post('/tickets/', json=ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertIsInstance(data, dict)
        
    def test_get_all_tickets(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.get('/tickets/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
    def test_assign_mechanic_to_ticket(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.put('/tickets/1/assign-mechanic/1', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertEqual(data['message'], 'Mechanic assigned successfully.')
        
    def test_remove_mechanic_from_ticket(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.put('/tickets/1/remove-mechanic/1', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertEqual(data['message'], 'Mechanic not assigned to this ticket.')
        
    def test_assign_inventory_item_to_ticket(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.post('/tickets/1/add-part/1', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertEqual(data['message'], 'Inventory item assigned to ticket successfully.')
        
    def test_create_inventory_item(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        
        ticket_payload = {
            'name': 'Rotor',
            'price': 50.25
        }

        response = self.client.post('/inventory/create', json=ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertIsInstance(data, dict)
    
    def test_update_inventory_item_by_ID(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}
        
        ticket_payload = {
            'name': 'Rotor',
            'price': 50.25
        }

        response = self.client.put('/inventory/1', json=ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, dict)
    
    def test_delete_inventory_item_by_ID(self):
        headers = {'Authorization': "Bearer " + self.test_login_mechanic()}

        response = self.client.delete('/inventory/1', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['message'], 'inventory deleted successfully.')
    
    def test_create_mechanic_missing_fields(self):
        payload = {"name": "John Doe"}
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 400)

    def test_login_mechanic_wrong_password(self):
        credentials = {"email": 'test@email.com', "password": 'wrong'}
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 400)

    def test_update_mechanic_no_auth(self):
        payload = {"name": "John", "email": "jd@email.com", "phone": "123", "salary": 60000.00, "password": "pass"}
        response = self.client.put('/mechanics/1', json=payload)
        self.assertEqual(response.status_code, 401)

    def test_delete_mechanic_no_auth(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 401)

    def test_get_all_mechanics_no_auth(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 401)

    def test_get_all_customers_no_auth(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 401)

    def test_get_customer_by_invalid_ID(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.get('/customers/999', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_assign_mechanic_to_ticket_invalid_ids(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.put('/tickets/999/assign-mechanic/999', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_remove_mechanic_from_ticket_invalid_ids(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.put('/tickets/999/remove-mechanic/999', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_assign_inventory_to_ticket_invalid_ids(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.post('/tickets/999/add-part/999', headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_create_inventory_missing_fields(self):
        headers = {'Authorization': "Bearer " + self.token}
        payload = {"name": "Rotor"}
        response = self.client.post('/inventory/create', json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_update_inventory_invalid_ID(self):
        headers = {'Authorization': "Bearer " + self.token}
        payload = {"name": "Rotor", "price": 50.25}
        response = self.client.put('/inventory/999', json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_delete_inventory_invalid_ID(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.delete('/inventory/999', headers=headers)
        self.assertEqual(response.status_code, 404)
    
    
if __name__ == "__main__":
    unittest.main()