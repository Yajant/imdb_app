import os,sys,re,base64,json      
from flask import Response, jsonify, make_response,url_for  
import datetime

def print_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("\n\n")
    print("\nEXC_TYPE -",exc_type,"\nFILENAME -",fname, "\nLINE-NO- ",exc_tb.tb_lineno, "\nEXCEPTION -",e)                    
    print("\n\n")

def isValidEmail(email):
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',email) != None:
        return True
    return False
 
def create_response_format(msg='something went wrong',data={},status=200,is_valid=False,headers={},permission_status=None,return_context=False,**kwargs):
    context = {}
             
    context['is_valid'] = is_valid 
    if data:
        context['data'] = data     
    if headers:
        context['headers'] = headers                    
    if msg:
        context['message'] = msg    
    if permission_status:
        context['permission_status'] = permission_status

    if not return_context:    
        response = make_response(jsonify(context), status)
        return response
    else:
        context['status_code'] = status
        return context

