import cerberus

schema = {
    'username': {'type': 'string', 'required': False},
    'password': {'type': 'string', 'required': False},
    'email': {'type': 'string', 'required': False}
}

def validate_user(user):
    return cerberus.Validator(schema).validate(user)
