from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify
from http import HTTPStatus
def staff_required(fn):
    # since the wrapped  function might  have  its own  metadata like (like __name__, __doc__, etc. or the doc sting)  in order to preserve  those that  we use @wraps which is a decorator  that wraps a function  allowing us  to add  metadata to  the function  without  modifying  the function  itself
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # Ensure JWT is valid
        claims = get_jwt()
        print(f"the claims we get ",claims)
        
        # user_id = claims.get('user_id')  just in case you want  to access other claims  which migh have kept intokenn  during creation
        # is_staff = claims.get('is_staff')
        if not claims.get('is_staff', False):  # Check if user is staff roled  inthis case
            return {"message": "Staff access required"}, HTTPStatus.FORBIDDEN
        return fn(*args, **kwargs)
    return wrapper
