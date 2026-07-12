from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(role):
    def wrapper(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify({"message": "Unauthorized"}), 403
            return function(*args, **kwargs)
        return decorated_function
    return wrapper