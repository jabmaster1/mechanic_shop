from application.__init__ import create_app
from application.models import db, Customer, Inventory
from application.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name = 'test_user', email = 'test@email.com', phone = '444-555-7777', password = 'test')
        self.inventroy_item = Inventory(id= 1, name= 'Brake Pad', price=10.0)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.inventroy_item)
            db.session.commit()
        self.token = encode_token(1, 'customer')
        self.client = self.app.test_client()

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "789-456-1238",
            "password": "password123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertEqual(data['name'], "John Doe")
        
    def test_login_customer(self):
        credentials = {
            "email": 'test@email.com',
            "password": 'test'
        }
        
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
    
    def test_update_customer(self):
        update_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "789-456-1238",
            "password": "password123"
        }
        
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Doe')
        self.assertEqual(response.json['email'], 'jd@email.com')
    
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.delete('/customers/', headers=headers)
        
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Customer deleted successfully.')
    
    def test_get_my_tickets(self):
        headers = {'Authorization': 'Bearer ' + self.test_login_customer()}
        
        response = self.client.get('/tickets/my-tickets', headers=headers)
        
        self.assertEqual(response.status_code, 200)
    
    def test_get_all_inventory(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.get('/inventory/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data= response.get_json()
        self.assertIsInstance(data, list)
    
    def test_get_inventory_by_ID(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.get('/inventory/1', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
    
    def test_create_customer_missing_fields(self):
        customer_payload = {
            "name": "Jane Doe" 
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400) 

    def test_login_customer_wrong_password(self):
        credentials = {
            "email": 'test@email.com',
            "password": 'wrongpassword'
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)

    def test_update_customer_no_auth(self):
        update_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "789-456-1238",
            "password": "password123"
        }
        response = self.client.put('/customers/', json=update_payload)
        self.assertEqual(response.status_code, 401)
        
    def test_delete_customer_no_auth(self):
        response = self.client.delete('/customers/')
        self.assertEqual(response.status_code, 401)

    def test_get_my_tickets_invalid_token(self):
        headers = {'Authorization': 'Bearer invalidtoken'}
        response = self.client.get('/tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_get_inventory_by_invalid_ID(self):
        headers = {'Authorization': "Bearer " + self.token}
        response = self.client.get('/inventory/999', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_get_all_inventory_no_auth(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 401)
    
if __name__ == "__main__":
    unittest.main()