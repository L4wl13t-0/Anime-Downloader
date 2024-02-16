from werkzeug.security import generate_password_hash, check_password_hash

def get_password(password):
	return generate_password_hash(password, method='scrypt')
    
def check_password(password, password_hash):
    return check_password_hash(password_hash, password)

