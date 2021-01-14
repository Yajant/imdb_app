from functools import wraps
from helpers import create_response_format
from imdb_fynd_app.models import User
from flask import request, g, session, redirect
import logging
import os
import datetime

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorator(self,*args, **kwargs):            
        auth_header = request.headers.get('Authorization')    
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:                
                return create_response_format(msg="Bearer token malformed.", status=401)                
        else:
            auth_token = ''

        if auth_token:
            token_status, resp = User.decode_auth_token(auth_token)  

            if token_status:
                try:
                    current_user = User.query.get(resp)  

                    print("\n---------------------------------------------------------------------------\n")
                    print("Request coming from user: '{0}'".format(current_user.email))
                    print("\n---------------------------------------------------------------------------\n")              
                except Exception as e:                    
                    current_user = None
                                
                if not current_user:                
                    return create_response_format(msg="No user found!", status=404)

                if not current_user.is_active:
                    return create_response_format(msg='Please activate your account first.', status=401)  
                
                self.current_user = current_user                                    
            else:
                return create_response_format(msg=resp, status=401)                    
        else:
            return create_response_format(msg="Provide a valid auth token.", status=401)                

        return f(self,*args, **kwargs)
    
    return decorator

def is_superuser(f):
    @wraps(f)
    def decorator(self,*args, **kwargs):
        
        # get the auth token        
        auth_header = request.headers.get('Authorization')    
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:                
                return create_response_format(msg="Bearer token malformed.", status=401)                
        else:
            auth_token = ''

        if auth_token:
            token_status, resp = User.decode_auth_token(auth_token)      
            if token_status:
                try:
                    current_user = User.query.get(resp)  

                    print("\n---------------------------------------------------------------------------\n")
                    print("Request coming from: '{0}'".format(current_user.email))
                    print("\n---------------------------------------------------------------------------\n")              
                except:
                    current_user = None

                if not current_user:                
                    return create_response_format(msg="No user found!", status=404)

                if not current_user.is_superuser:            
                    return create_response_format(msg="You do not have permission to view that page", status=403) 
                            
                if not current_user.is_active:
                    return create_response_format(msg='Please activate your account first.', status=401)  
                
                self.current_user = current_user  
                return f(self,*args, **kwargs)                
            else:
                return create_response_format(msg=resp, status=401)                    
        else:
            return create_response_format(msg="Provide a valid auth token.", status=401)                
    return decorator


def admin_login_required(f):
    def wrap(*args, **kwargs):
        # print(g.__dict__)
        # print(session)
        if session.get('_user_id'):
            user_id = session.get('_user_id')
            user = User.query.get(user_id)
            # user is available from @login_required
            if not user.is_superuser:
                return create_response_format(msg="You do not have permission to view that page", status=401) 
        else:
            return create_response_format(msg="You do not have permission to view that page", status=401) 
        # finally call f. f() now haves access to g.user
        return f(*args, **kwargs)
    return wrap