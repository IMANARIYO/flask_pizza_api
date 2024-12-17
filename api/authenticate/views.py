from flask_restx import Namespace,Resource,fields
from flask import request
from ..models.users import User
from http import HTTPStatus
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.exceptions import Conflict,BadRequest,Unauthorized,NotFound
from ..models.users import User
from ..utils import db
from ..utils.decorators import staff_required
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity
auth_namespace= Namespace('auth',description=' a name space  for  Authentication related operations')
Signup_model=auth_namespace.model(
    'Signup', {
    'id':fields.Integer(),
    'username':fields.String(required=True,description='The user name for authentication'),
    'email':fields.String(required=True,description='The email address'),
    'password':fields.String(required=True,description='The password for authentication'),   
})
User_model=auth_namespace.model(
    'User',{
    'id':fields.Integer(),
    'username':fields.String(required=True,description='The user name for authentication'),
    'email':fields.String(required=True,description='The email address'),
    'password':fields.String(required=True,description='The password for authentication'),
    'is_active':fields.Boolean(description='this shows  that User is active'),
    'is_staff':fields.Boolean(description="this  shows  if  user is  staff")

    }
)
Login_model=auth_namespace.model(
    'Login',{
        'email':fields.String(required=True,description='The email address'),
        'password':fields.String(required=True,description='The password for authentication') 
    }
            )

   
@auth_namespace.route('/signup')
class Signup(Resource):
    @auth_namespace.expect(Signup_model)
    @auth_namespace.marshal_with(User_model)
    def post(self):
        """ generate  jwt here """
        data=request.get_json()
        try:
    
            new_user=User( 
                username=request.json.get('username'),
                email=request.json.get('email'),
                password=generate_password_hash(request.json.get('password'))
                )
            new_user.save()
            return new_user,HTTPStatus.CREATED
        except Exception as e:
            raise Conflict(f'User {request.json.get('email')  } already existss')

       
@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(Login_model)
    def post(self):
        """Generate JWT pair with additional claims"""
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
             
            additional_claims = {
                'user_id': user.id,
                'is_staff': user.is_staff,
               
                'is_active': user.is_active,
                'username': user.username
            }

            access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            return response, HTTPStatus.OK

        raise BadRequest('Invalid username or password')
   
@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        username=get_jwt_identity()
        access_token=create_access_token(identity=username)
        
        return {'access_token':access_token},HTTPStatus.OK
    
 
@auth_namespace.route('/user/<int:user_id>/toggle-role')
class ToggleUserRole(Resource):
    @jwt_required()
    @staff_required  # Ensure only staff users can access this endpoint
    def patch(self, user_id):
        """
        Toggle the role of the user (is_staff).
        """
        # Fetch the user whose role is to be toggled
        user_to_update = User.query.get(user_id)
        if not user_to_update:
            raise NotFound("User not found.")

        # Toggle the user's is_staff role
        user_to_update.is_staff = not user_to_update.is_staff
        db.session.commit()

        return {
            'message': f"User {user_to_update.username}'s role toggled successfully.",
            'data': {
                'username': user_to_update.username,
                'is_staff': user_to_update.is_staff
            }
        }, HTTPStatus.OK



