from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from utils.users import validate_user, get_user_id

def user_access_required(action, name, pass_user_id = False):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            username = get_jwt_identity()
            if not validate_user(username):
                return jsonify({'msg': 'Invalid user','status': {
                    'name': name,
                    'action': action,
                    action: False
                }}), 401
            if pass_user_id:
                user_id = get_user_id(username)
                return func(*args, **kwargs, user_id = user_id)
            return func(*args, **kwargs)
        return decorated_function
    return decorator