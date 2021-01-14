import json
import logging

from flask import request, Response
from flask_restful import Resource
from imdb_fynd_app.core.http import crossdomain, request_data
from helpers import create_response_format

log = logging.getLogger(__name__)

class BaseView(Resource):
    uri = None
    endpoint = None

    def __init__(self):
        self.request_data = {}
        
    @crossdomain(origin='*')
    def dispatch_request(self, *args, **kwargs):
        if request.method == 'OPTIONS':             
            return super().dispatch_request(*args, **kwargs)

        self.request_data = request_data()        
    
        try:
            return super().dispatch_request(*args, **kwargs)
        except Exception as e:
            log.info('{0} was sent {1} which raised a Error : {2}'.format(request.base_url, self.request_data, str(e)))
            error_location = '{0} {1}'.format(request.path, request.method.upper())
            log.info(error_location)
            return create_response_format(msg="Invalid Request")            

    def options(self, **kwargs):        
        return Response(status=200)
