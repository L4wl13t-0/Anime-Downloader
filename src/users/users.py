from flask import request, jsonify, blueprints
from app import mongo, app
from flask_pymongo import ObjectId
from flask_jwt_extended import create_access_token
from utils.users import validate_username, validate_user, get_username, validate_user_by_id, get_user_id, validate_admin, validate_email
from utils.passwords import check_password, get_password
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import user_access_required
from schemas.users import validate_user as validate_user_schema
import datetime

users_blueprint = blueprints.Blueprint('users', __name__)

@users_blueprint.route('/users', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    if not username or not password or not email:
        return jsonify({'msg': 'Username, email or password missing',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'register',
                            'register': False
                        }
                        }), 400

    if validate_user(username):
        return jsonify({'msg': 'Username already exists',
                        'status': {
                            'name': 'data_conflict',
                            'action': 'register',
                            'register': False
                        }
                        }), 400
    
    if validate_email(email):
        return jsonify({'msg': 'Email already exists',
                        'status': {
                            'name': 'data_conflict',
                            'action': 'register',
                            'register': False
                        }
                        }), 400

    if not validate_username(username):
        return jsonify({'msg': 'Invalid username',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'register',
                            'register': False
                        }
                        }), 400

    user = {'username': username,
            'password_hash': get_password(password),
            'email': email,
            'admin': False,
            'created_at': datetime.datetime.utcnow(),
            }

    mongo.db.users.insert_one(user)

    return jsonify({'msg': 'User created succesfully',
                    'status': {
                        'name': 'created',
                        'action': 'register',
                        'register': True
                    }
                    }), 201


@users_blueprint.route('/users', methods=['GET'])
def login():
    auth = request.authorization
    user = mongo.db.users.find_one({'username': auth.username})

    stay_loged_in = request.args.get('stay_loged_in')

    if stay_loged_in == "true":
        expires_delta = datetime.timedelta(days=7)
    else:
        expires_delta = app.config['JWT_ACCESS_TOKEN_EXPIRES']

    if not user:
        return jsonify({'msg': 'User does not exist',
                        'status': {
                            'name': 'not_found',
                            'action': 'login',
                            'login': False
                        }
                        }), 401

    if auth and check_password(auth.password, user['password_hash']):
        token = create_access_token(
            identity=auth.username, expires_delta=expires_delta)

        return jsonify({'msg': 'User logged in successfully',
                        'status': {
                            'name': 'logged_in',
                            'action': 'login',
                            'login': True
                        },
                        'data': {
                            'token': token
                        }
                        })
    

@users_blueprint.route('/users/<user>', methods=['DELETE'])
@jwt_required()
@user_access_required('delete', 'not_deleted', pass_user_id=True)
def deleteUser(user, user_id):
    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401
        
    if not validate_user_by_id(user):
        return jsonify({'msg': 'User does not exist',
                        'status': {
                            'name': 'not_found',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401

    mongo.db.users.delete_one({'_id': ObjectId(user)})
    return jsonify({'msg': 'User deleted successfully',
                    'status': {
                        'name': 'deleted',
                        'action': 'delete',
                        'delete': True
                    }})


@users_blueprint.route('/users', methods=['PUT'])
@jwt_required()
@user_access_required('update', 'not_updated', pass_user_id=True)
def updateUser(user_id):
    if not validate_user_by_id(user_id):
        return jsonify({'msg': 'User does not exist',
                        'status': {
                            'name': 'not_found',
                            'action': 'update',
                            'update': False
                        }
                        }), 401

    data = request.json.get('data')
    if not data:
        return jsonify({'msg': 'Missing data',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'update',
                            'update': False
                        }}), 400

    if not validate_user_schema(data):
        return jsonify({'msg': 'Invalid data',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'update',
                        }}), 400

    set_data = {}
    set_data['username'] = data.get('username') if data.get('username') else get_username(user_id)
    if data.get('password'):
        set_data['password_hash'] = get_password(data.get('password'))
    if data.get('email'):
        set_data['email'] = get_password(data.get('email'))
    mongo.db.users.update_one({'_id': user_id}, {'$set': set_data})

    return jsonify({'msg': 'User updated successfully',
                    'status': {
                        'name': 'updated',
                        'action': 'update',
                        'update': True
                    }
                    })


@users_blueprint.route('/users/<user>', methods=['PUT'])
@jwt_required()
@user_access_required('update', 'not_updated', pass_user_id=True)
def updateUserAdmin(user, user_id):
    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401

    if not validate_user_by_id(user):
        return jsonify({'msg': 'User does not exist',
                        'status': {
                            'name': 'not_found',
                            'action': 'update',
                            'update': False
                        }
                        }), 401

    data = request.json.get('data')
    if not data:
        return jsonify({'msg': 'Missing data',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'update',
                            'update': False
                        }}), 400

    if not validate_user_schema(data):
        return jsonify({'msg': 'Invalid data',
                        'status': {
                            'name': 'invalid_data',
                            'action': 'update',
                        }}), 400

    set_data = {}
    set_data['username'] = data.get('username') if data.get('username') else get_username(user)
    if data.get('password'):
        set_data['password_hash'] = get_password(data.get('password'))
    if data.get('email'):
        set_data['email'] = get_password(data.get('email'))
    mongo.db.users.update_one({'_id': ObjectId(user)}, {'$set': set_data})

    return jsonify({'msg': 'User updated successfully',
                    'status': {
                        'name': 'updated',
                        'action': 'update',
                        'update': True
                    }
                    })