import os
from decouple import config 
from datetime import timedelta
BASE_DIR=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
class BaseConfig:
    SECRET_KEY = config('SECRET_KEY','secret')
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    JWT_ACCESS_TOKEN_EXPIRES =timedelta(days=30)
    JWT_REFERESH_TOKEN_EXPIRES =timedelta(days=30)
    JWT_SECRET_KEY=config('JWT_SECRET_KEY')
    
class DevConfig(BaseConfig):
    DEBUG =config('DEBUG',cast=bool)
    SQLALCHEMY_ECHO=True
    # SQLALCHEMY_DATABASE_URI=config('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(BASE_DIR,'db.sqlite3')
class TestConfig(BaseConfig):
   TESTING=True
   SQLALCHEMY_TRACK_MODIFICATIONS= False
   SQLALCHEMY_ECHO=True
   SQLALCHEMY_DATABASE_URI='sqlite://'
class ProdConfig(BaseConfig):
    
    pass
config_dict = {
    'dev':DevConfig,
    'prod':ProdConfig,
    'test':TestConfig
}

    
   