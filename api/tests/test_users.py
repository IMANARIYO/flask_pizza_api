import unittest
from http import HTTPStatus
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create a sample user
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password': 'password123'
        }
        hashed_password = generate_password_hash(self.user_data['password'])
        user = User(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

    def test_signup_success(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@gmail.com',
            'password': 'newpassword123',
        }
        response = self.client.post('/auth/signup', json=data)
        assert response.status_code == HTTPStatus.CREATED
        assert response.json['username'] == data['username'] 
        assert response.json['email'] == data['email']

    def test_signup_duplicate_user(self):
        response = self.client.post('/auth/signup', json=self.user_data)
        assert response.status_code == HTTPStatus.CONFLICT
        assert f"User {self.user_data['email']} already existss" in response.json['message']

    def test_login_success(self):
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        response = self.client.post('/auth/login', json=data)
        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json

    def test_login_invalid_credentials(self):
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword',
        }
        response = self.client.post('/auth/login', json=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Invalid username or password' in response.json['message']

    def test_refresh_token(self):
        # Login to get refresh token
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post('/auth/login', json=login_data)
        refresh_token = login_response.json['refresh_token']

        # Use refresh token to get a new access token
        response = self.client.post(
            '/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json

    def test_toggle_user_role_staff_required(self):
        # Login to get staff access token
        user = User.query.filter_by(email=self.user_data['email']).first()
        user.is_staff = True  # Make user a staff
        db.session.commit()

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post('/auth/login', json=login_data)
        access_token = login_response.json['access_token']

        # Toggle role for another user
        new_user = User(
            username='regularuser',
            email='regularuser@gmail.com',
            password=generate_password_hash('password123')
        )
        db.session.add(new_user)
        db.session.commit()

        response = self.client.patch(
            f'/auth/user/{new_user.id}/toggle-role',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.OK
        assert f"User {new_user.username}'s role toggled successfully." in response.json['message']
    def test_toggle_user_role_user_not_found(self):
        # Login to get staff access token
        user = User.query.filter_by(email=self.user_data['email']).first()
        user.is_staff = True  # pre assigning the   is staff  role in order to be able to update  others role
        db.session.commit()
    
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post('/auth/login', json=login_data)
        access_token = login_response.json['access_token']
    
        # Attempt to toggle role for a non-existent user ID
        non_existent_user_id = 9999  # Use an ID unlikely to exist
        response = self.client.patch(
            f'/auth/user/{non_existent_user_id}/toggle-role',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'User not found.' in response.json['message']
    def test_toggle_user_role_non_staff_user(self):
        # Login as a non-staff user
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post('/auth/login', json=login_data)
        access_token = login_response.json['access_token']
    
        # Attempt to toggle role for another user
        response = self.client.patch(
            f'/auth/user/1/toggle-role',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
    
    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None
