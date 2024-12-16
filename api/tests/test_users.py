import unittest
from ..import create_app
from ..config.config import config_dict
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app(config=config_dict['testing'])
        pass
    def tearDown(self):
       pass
     

