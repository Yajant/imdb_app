from functools import wraps
from helpers import create_response_format
from imdb_fynd_app.models import User
from flask import request, g, session
import logging
import os
import datetime

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):            
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

            print(token_status, resp, " - token_status, respv")    
            if token_status:
                try:
                    current_user = User.query.get(resp)  

                    print("\n---------------------------------------------------------------------------\n")
                    print("Request coming from user: '{0}'".format(current_user.email))
                    print("\n---------------------------------------------------------------------------\n")              
                except Exception as e:
                    print(e,"######################")
                    current_user = None
                                
                if not current_user:                
                    return create_response_format(msg="No user found!", status=404)

                if not current_user.is_active:
                    return create_response_format(msg='Please activate your account first.', status=401)  
                                                              
            else:
                return create_response_format(msg=resp, status=401)                    
        else:
            return create_response_format(msg="Provide a valid auth token.", status=401)                

        return f(current_user,*args, **kwargs)
    
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
                    current_user = User.query.get(id=resp)  

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
                
                return f(current_user,*args, **kwargs)                
            else:
                return create_response_format(msg=resp, status=401)                    
        else:
            return create_response_format(msg="Provide a valid auth token.", status=401)                
    return decorator