from app import mongo
from flask_pymongo import ObjectId

def validate_author(author):
    _author = mongo.db.authors.find_one({'author': author})
    if not _author:
        return False
    return True

def validate_category(category):
    return True if mongo.db.books.find_one({'categories': category}) else False