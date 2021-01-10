import base64
import hashlib
import hmac
import json
import logging
from imdb_fynd_app.core.exceptions import RequestDataValidationError
from datetime import timedelta
from flask import Response, request
from functools import wraps

log = logging.getLogger(__name__)


NULL_STRINGS = ['None', 'null', 'undefined']


def request_data():
    request_data_dicts = (
        request.json,
        request.form,
        request.args,
    )

    request_data = {}
    for rdd in request_data_dicts:
        if isinstance(rdd, dict):
            for key in rdd.keys():
                request_data[key] = rdd[key]
    return request_data


def parse_args(arg_list, request_data, json_string_fields=False):
    if not request_data:
        log.debug('No request data supplied')
        if [arg for arg in arg_list if arg[2] == True]:            
            raise RequestDataValidationError('No request data supplied')
        else:
            return {arg[0]: None for arg in arg_list}

    validated_request_data = {}
    for ali in arg_list:
        nullable = False
        spec = None

        if len(ali) == 3:
            arg, arg_type, required = ali
        elif len(ali) == 4:
            arg, arg_type, required, spec = ali
        else:
            error_message = 'Missing parameters in arg definition: {}'.format(ali)
            log.debug(error_message)
            raise RequestDataValidationError(error_message)

        if isinstance(arg_type, tuple):
            arg_type, nullable = arg_type

        try:
            value = request_data.get(arg, None)
            if json_string_fields:
                value = json.loads(value) if value else None
        except AttributeError:
            value = None

        if isinstance(value, str) and value in NULL_STRINGS:
            value = None

        if required and value is None and not nullable:
            error_message = "Missing required parameter `{0}`, from arg list: {1} and data: {2}.".format(
                arg, arg_list, request_data)
            log.debug(error_message)
            raise RequestDataValidationError(error_message)

        if value is not None:
            try:
                if arg_type == bool and isinstance(value, str) and value.lower() == 'false':
                    # to avoid {bool('False') = True}
                    value = False
                if (arg_type == dict or arg_type == list) and isinstance(value, str):
                    try:
                        value = json.loads(value)
                        if type(value) != arg_type:
                            raise TypeError()
                    except:
                        message = 'Parameter {0} invalid json.'.format(arg)
                        log.debug(message)
                        raise RequestDataValidationError(message)

                value = arg_type(value)
                if spec:
                    if arg_type is list:
                        if spec in (int, float, str):
                            value = [spec(x) for x in value]
                        else:
                            value = [parse_args(spec, x) for x in value]
                    if arg_type is dict:
                        value = parse_args(spec, value)
            except (TypeError, ValueError):
                message = "Parameter {0} is not the correct type.".format(arg)
                log.debug(message)
                raise RequestDataValidationError(message)

        validated_request_data.update({arg: value})

    return validated_request_data


def crossdomain(origin=None, methods=None, headers=None, max_age=21600):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    else:
        methods = ", ".join(['HEAD', 'GET', 'POST', 'PUT', 'DELETE'])
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def decorator(f):
        @wraps(f)
        def wrapped_function(self, *args, **kwargs):            
            resp = f(self, *args, **kwargs)
            # h = resp.headers
            
            # CIS
            if hasattr(resp, 'headers'):
                h = resp.headers 
            else:
                h= {} 
            # If the Content-Disposition header exists it likely means we're sending a specific type of content,
            # therefore we don't enforce the mimetype.

            if 'Content-Disposition' not in h:
                h['Content-Type'] = 'application/json'
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = methods
            h['Access-Control-Allow-Headers'] = "Access-Control-Allow-Headers, Authorization, Access-Control-Allow-Origin, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"

            # h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            
            return resp
        f.provide_automatic_options = False
        return wrapped_function
    return decorator
