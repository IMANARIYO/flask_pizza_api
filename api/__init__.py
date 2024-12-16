from flask import Flask, jsonify, request
from .orders.views import order_namespace
from .authenticate.views import auth_namespace
from flask_restx import Api
from .config.config import config_dict
from .utils import db
from .models.orders import Order
from .models.users import User
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound,MethodNotAllowed  
def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    migrate=Migrate(app,db)

    api=Api(app,security='BearerAuth')

    api.add_namespace(order_namespace)
    api.add_namespace(auth_namespace,path="/auth")
    api.models['BearerAuth'] = {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer <your_token>"'
    }


    db.init_app(app)
    jwt=JWTManager(app)
    @api.errorhandler(NotFound)
    def not_found(error):
        return{"error":"Not Found "},404
    
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error":"method Not  allowed"},405
        
    @app.shell_context_processor
    def make_shell_context():       
        return {'db':db,'User':User,'Order':Order}
    return app