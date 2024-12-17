import unittest
from ..import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users import User

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app(config=config_dict['test'])
        self.appctx=self.app.app_context()
        self.appctx.push()
        self.client=self.app.test_client()
        db.create_all()
    def test_user_registration(self):
        data={
            'username':'testuser',
            'email':'testuser@gmail.com',
            'password':'password123',
        }
        response=self.client.post('/auth/signup',json=data)
        assert response.status_code==201,"Optional error message"
        assert 'username' in response.json
        assert response.json['username'] == 'testuser'
        assert 'email' in response.json
        assert response.json['email'] == 'testuser@gmail.com'
    def test_duplicate_user_registration(self):
        
       data = {
           'username': 'testuser',
           'email': 'testuser@gmail.com',
           'password': 'password123',
       }
       self.client.post('/auth/signup', json=data)
   
        
       response = self.client.post('/auth/signup', json=data)
       
        
       assert response.status_code == 409
       
        
       assert 'User testuser@gmail.com already exists' in response.json['message']
    def test_sql_injection_attempt(self):
        data = {
            'username': "' OR '1'='1",
            'email': "testuser@gmail.com",
            'password': "' OR '1'='1",
        }
        response = self.client.post('/auth/signup', json=data)
        assert response.status_code == 400   
        assert 'invalid' in response.json['message']


          




       
    def tearDown(self):
       db.drop_all()
       self.appctx.pop()
       self.app=None
       self.client=None
     

