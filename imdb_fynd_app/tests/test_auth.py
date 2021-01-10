import json, time
from imdb_fynd_app.core.tests import BaseTestCase
from imdb_fynd_app.models import User
from imdb_fynd_app.routes.auth import RegisterAPI, LoginAPI, LogoutAPI

# -------------------------------
# TEST USER
# To run the test enter this command in your terminal.
# export SQLALCHEMY_DATABASE_URI='sqlite:///IMDB.sqlite3'
# python -m unittest /home/yajant/Downloads/imdb_fynd_app/imdb_fynd_app/tests/test_auth.py
# -------------------------------
class TestUser(BaseTestCase):   

    def test_registration(self):
        """ Test for user registration """
        json_response = self.register_user('joe@gmail.com', 'Download@123',201)    
        # Then
        self.assertTrue(True, type(json_response['is_valid']))        
        self.assertTrue(
            json_response['message'] == "User Registed Successfully")

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        email='joe@gmail.com'
        password='Download@123'  
        json_response = self.register_user('joe@gmail.com', 'Download@123',201)        
        self.assertTrue(True, type(json_response['is_valid']))        

        json_response = self.register_user('joe@gmail.com', 'Download@123',409)        
        self.assertFalse(False, type(json_response['is_valid']))
        self.assertTrue(
            json_response['message'] == 'USERNAME_ALREADY_EXISTS')

    def test_user_registration_with_invalid_email(self):
        json_response = self.register_user("jgjuhyuiyhui", "download123",400)
        # Then
        self.assertEqual(False, json_response['is_valid'])

    def test_user_registration_with_weak_password(self):
        
        json_response = self.register_user("joe@gmail.com",'as',400)                
        self.assertEqual(False, json_response['is_valid']) 
        self.assertEqual('PASSWORD_SHOULD_BE_BETWEEN_LENGTH_3_TO_25' , json_response['message'])
        
    def test_registered_user_login(self):
        """ Test for login of registered-user login """        
        # user registration
        data_register = self.register_user("joe@gmail.com","Download@123",201)        
        self.assertTrue(True, type(data_register['is_valid']))        
        self.assertTrue(data_register['message'] == "User Registed Successfully")
        # time.sleep(2)         
        # # registered user login
        data_login = self.login_user("joe@gmail.com","Download@123",200)        
        self.assertTrue(True, type(data_login['is_valid']))   
        self.assertEqual("Successfully logged in", data_login['message'])
        self.assertTrue(data_login['data']['auth_token'])        

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """    
        time.sleep(2)    
        data_login = self.login_user('sam@gmail.com', '123456',404)        
        self.assertFalse(False, type(data_login['is_valid']))
        self.assertTrue(data_login['message'] == 'No user found!')      

    def test_valid_logout(self):
        """ Test for logout"""        
        ## user registration
        data_register = self.register_user('joe@gmail.com', "Download@123",201)        
        self.assertTrue(True, type(data_register['is_valid'])) 
        
        # user login
        data_login = self.login_user('joe@gmail.com','Download@123',200)        
        self.assertTrue(True, type(data_login['is_valid']))
        ## valid token logout
        uri = LogoutAPI.uri        
        response = self.http_send(
            uri=uri,
            method='POST',            
            code=200,
            headers=dict(
                Authorization='Bearer ' + data_login['data']['auth_token']
            )
        )        
        json_response = json.loads(response.data.decode())                    
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Successfully logged out.", json_response['message']) 
