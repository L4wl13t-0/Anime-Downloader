from flask import Flask, request, jsonify
import datetime
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
from os import getenv
from flask_jwt_extended import JWTManager
load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = getenv('MONGO_URI')
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['ALLOWED_EXTENSIONS_BOOKS'] = getenv('ALLOWED_EXTENSIONS_BOOKS')
app.config['BOOKS_PATH'] = getenv('BOOKS_PATH')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
mongo = PyMongo(app)
jwt = JWTManager(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "DELETE", "PUT", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

cors.init_app(app)