from app import app
from users.users import users_blueprint

app.register_blueprint(users_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True,port=8000)