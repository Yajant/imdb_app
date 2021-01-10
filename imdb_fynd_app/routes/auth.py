from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
import logging
from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User
from imdb_fynd_app.core.imdb_decorator import token_required , is_superuser
from helpers import create_response_format, print_exception, isValidEmail
from imdb_fynd_app.core.views import BaseView
from imdb_fynd_app.core.http import request_data, parse_args

logger = logging.getLogger(__name__)

class RegisterAPI(BaseView): 

    uri = '/user/register'

    def post(self):
        try:     
            # get the post data
            data = parse_args(
                (
                    ('email', str, True),
                    ('password', str, True)
                ),
                request_data()
            )
                    
            email = data.get('email')            
            password = data.get('password')

            is_Valid_Email = isValidEmail(email)
            if not is_Valid_Email:
                return create_response_format(msg="""Please enter a valid email. Valid e-mail can contain only contain latin letters, numbers, '@' and '.'. """)
                
            if not email:
                return create_response_format(msg='email_IS_MANDOTRY')
            if not password:
                return create_response_format(msg='password_IS_MANDOTRY')
            else:
                #check length for password
                pass_length = len(password)
                if pass_length < 3 or pass_length > 25:
                    return create_response_format(msg='PASSWORD_SHOULD_BE_BETWEEN_LENGTH_3_TO_25')
            
            new_user = User.query.filter_by(email=email).one_or_none()
            if new_user is None:                                
                new_user = User(email=email.lower(), password=password,is_active=True)
            else:
                return create_response_format(msg='USERNAME_ALREADY_EXISTS',status=409)
            db.session.add(new_user)
            db.session.commit()

            ## generate the auth token
            auth_token = new_user.encode_auth_token(new_user.id)                
            logger.info(str(auth_token))
                        
            data = {'auth_token': auth_token}
                        
            return create_response_format(msg='User Registed Successfully',data=data,is_valid=True,status=201)

        except Exception as e:
            print_exception(e)
            return create_response_format(msg='SOMETHING_WENT_WRONG_IN_REGISTERING_USER')
    
class LoginAPI(BaseView): 

    uri = '/user/login'
    
    def post(self):
        try:
            data = parse_args(
                (
                    ('email', str, True),
                    ('password', str, True)
                ),
                request_data()
            )
                    
            email = data.get('email')            
            password = data.get('password')

            if not email:
                return create_response_format(msg='email_IS_MANDOTRY')
            if not password:
                return create_response_format(msg='password_IS_MANDOTRY')

            # check that email exits or not
            user = User.query.filter_by(email=email).one_or_none()
            if not user:                
                return create_response_format(msg="No user found!", status=404)
           
            #authenticate password            
            if user and user.check_password(password):
                auth_token = user.encode_auth_token(user.id)
                print(auth_token, " - auth_token")
                if auth_token:                                                                            
                    # data = {'auth_token': auth_token.decode()}
                    data = {'auth_token': auth_token}
                    logger.info("Successfully logged in -'{0}'".format(user.email))

                    print("\n---------------------------------------------------------------------------\n")
                    print("\nLogged in user: '{0}'".format(user.email))
                    print("\n---------------------------------------------------------------------------\n")

                    return create_response_format(msg='Successfully logged in',data=data, status=200, is_valid=True)     
            else:                
                return create_response_format(msg='Login Unsuccessful. Please check email and password.', status=401)     

        except Exception as e:
            print_exception(e)
            return create_response_format(msg='SOMETHING_WENT_WRONG_IN_LOGGING_USER')

class LogoutAPI(BaseView): 

    uri = '/user/logout'

    @token_required
    def post(self):   
        current_user = self.current_user                      
        auth_header = request.headers.get('Authorization')

        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        if auth_token and current_user.id:                                        
            try:                
                # insert the token                
                current_user.auth_token = auth_token
                db.session.commit()
                                
                logger.info("Successfully logged out. -'{0}'".format(current_user.email))
                return create_response_format(msg='Successfully logged out.', status=200,is_valid=True)                
            except Exception as e:
                logger.error(e)
                return create_response_format(exception=True,status=200)            
        else:                    
            return create_response_format(msg='Provide a valid auth token.',status=403)        
