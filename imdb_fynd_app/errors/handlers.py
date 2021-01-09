from flask import render_template, request
from helpers import create_response_format

API_PATH_PREFIX = '/api'

def error_404(error):
    if request.path.startswith(API_PATH_PREFIX):        
        msg = 'API endpoint {!r} does not exist for method {} on this server'.format(request.path,request.method.upper())
        return create_response_format(msg = msg, status=error.code)    
    return render_template('errors/404.html'), 404

def error_403(error):
    if request.path.startswith(API_PATH_PREFIX):
        msg = 'You don\'t have permission to do that, for API endpoint {!r} - method - {} on this server'.format(request.path,request.method.upper())
        return create_response_format(msg = msg, status=error.code)
    return render_template('errors/403.html'), 403

def error_405(error):
    print(request.path, " - request.path")
    if request.path.startswith(API_PATH_PREFIX):
        msg = 'Method {} not allowed, for API endpoint {!r}'.format(request.method.upper(), request.path)
        return create_response_format(msg = msg, status=error.code)
    return render_template('errors/403.html'), 405

def error_500(error):    
    # We're experiencing some trouble on our end. Please try again in the near future
    if request.path.startswith(API_PATH_PREFIX):
        msg = 'Something went wrong, for API endpoint {!r} - method - {} on this server'.format(request.path,request.method.upper())
        return create_response_format(msg = msg, status=error.code)
    return render_template('errors/500.html'), 500