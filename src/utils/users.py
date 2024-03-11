from app import mongo
from flask_pymongo import ObjectId
import re

def validate_user(username):
    user = mongo.db.users.find_one({'username': username})
    if not user:
        return False
    return True

def validate_email(email):
    user = mongo.db.users.find_one({'email': email})
    if not user:
        return False
    return True

def validate_user_by_id(user_id):
    if isinstance(user_id, ObjectId):
        user = mongo.db.users.find_one({'_id': user_id})
    else:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return False
    return True

def get_user_id(username):
    if not validate_user(username):
        return None
    user = mongo.db.users.find_one({'username': username})
    return user.get('_id')

def get_username(user_id):
    user = mongo.db.users.find_one({'_id': user_id})
    if not user:
        return None
    return user.get('username')

def validate_username(username):
    username_re = re.compile(r'^[a-zA-Z0-9_]{3,}$')
    return username_re.findall(username) != []

def validate_admin(user_id):
    user = mongo.db.users.find_one({'_id': user_id})
    if not user.get(3):
        return False
    return True