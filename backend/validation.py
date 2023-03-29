from urllib import response
from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self, status_code, message=''):
        self.response = make_response(message, status_code)

class BusinessValidationError(HTTPException):
    def __init__(self,status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message }
        self.response = make_response(json.dumps(message), status_code)