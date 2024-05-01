from flask import Blueprint, jsonify, request
from app import mongo
from flask_pymongo import ObjectId
from schemas.books import validate_book
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import user_access_required
from utils.users import get_user_id, get_username, validate_admin
from utils.books import validate_author, validate_category, validate_bookFile, get_epub_cover

books_blueprint = Blueprint('books', __name__)


@books_blueprint.route('/books', methods=['POST'])
@jwt_required()
@user_access_required('create', 'not_created', pass_user_id=True)
def createBook(user_id):
    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401
    
    book = request.json.get('book')
    if not book:
        return jsonify({'msg': 'No book provided',
                        'status': {
                            'name': 'not_created',
                            'action': 'create',
                            'create': False
                        }
                        }), 400

    if not validate_book(book):
        return jsonify({'msg': 'Invalid book',
                        'status': {
                            'name': 'not_created',
                            'action': 'create',
                            'create': False
                        }
                        }), 403

    id = mongo.db.books.insert_one({
        'name': book.get('name'),
        'description': book.get('description'),
        'author': book.get('author'),
        'author_id': None,
        'categories': book.get('categories'),
        'filename': "default.epub",
        'cover_image': 'default.png',
        'score': 0.0
    })

    author = mongo.db.authors.find_one_and_update(
        {'author': book.get('author')},
        {'$addToSet': {'books': id.inserted_id}},
        upsert=True,
        return_document=True
    )

    mongo.db.books.update_one(
        {'_id': id.inserted_id},
        {'$set': {'author_id': author['_id']}}
    )

    return jsonify({'msg': 'Book created',
                    'status': {
                        'name': 'created',
                        'action': 'create',
                        'create': True
                    },
                    'data': {
                        'id': str(id.inserted_id),
                    }
                    }), 201

@books_blueprint.route('/uploadbook/<id>', methods=['POST'])
@jwt_required()
@user_access_required('create', 'not_created', pass_user_id=True)
def uploadBook(id, user_id):
    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401
    
    book = request.files.get('fileBook')
    if not book:
        return jsonify({'msg': 'No book provided',
                        'status': {
                            'name': 'not_created',
                            'action': 'create',
                            'create': False
                        }
                        }), 400

    if not validate_bookFile(book):
        return jsonify({'msg': 'Invalid book',
                        'status': {
                            'name': 'not_created',
                            'action': 'create',
                            'create': False
                        }
                        }), 403
    
    cover_image = get_epub_cover(book)

    idUpload = mongo.db.books.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'filename': book.filename,
                  'cover_image': cover_image}}
    )

    return jsonify({'msg': 'Book uploaded',
                    'status': {
                        'name': 'uploaded',
                        'action': 'create',
                        'create': True
                    }
                    }), 202

@books_blueprint.route('/books', methods=['GET'])
def getBooks(): 
    Filter = request.args.get('filter')
    if not Filter:
        books = mongo.db.books.find({})
    else:
        if Filter.startswith('@'):
            Filter = Filter.replace('@', '')
            if not validate_author(Filter):
                return jsonify({'msg': f'invalid author "{Filter}"',
                                'status': {
                                    'name': 'bad_request',
                                    'action': 'get',
                                    'get': False
                                }
                                }), 400
            author_id = mongo.db.authors.find_one({'author': Filter}).get('_id')
            books = mongo.db.books.find({'author_id': author_id})

        elif Filter.startswith('%'):
            category = Filter[1:]
            if not validate_category(category):
                return jsonify({'msg': f'invalid category "{category}"',
                                'status': {
                                    'name': 'bad_request',
                                    'action': 'get',
                                    'get': False
                                }
                            }), 400
            books = mongo.db.books.find({'categories': {'$elemMatch': {'$eq': category}}})

        elif Filter.startswith('!'):
            Filter = Filter.replace('!', '')
            mongo.db.books.create_index({ "name": "text", "description": "text", "author" : "text" })
            books = mongo.db.books.find({'$text': {'$search': Filter}})

    books = list(books)
    return jsonify({
        'msg': 'Books retrieved',
        'status': {
            'name': 'retrieved',
            'action': 'get',
            'get': True
        },
        'data': list(map(lambda book: {
            'id': str(book.get('_id')),
            'name': book.get('name'),
            'description': book.get('description'),
            'author': book.get('author'),
            'categories': book.get('categories')
        }, books))
    }), 200


@books_blueprint.route('/books/<id>', methods=['GET'])
@jwt_required(optional=True)
def getBook(id):
    book = mongo.db.books.find_one({'_id': ObjectId(id)})
    if not book:
        return jsonify({'msg': 'Book not found',
                        'status': {
                            'name': 'not_found',
                            'action': 'get',
                            'get': False
                        }
                        }), 400

    return jsonify({
        'msg': 'Book retrieved',
        'status': {
            'name': 'retrieved',
            'action': 'get',
            'get': True
        },
        'data': {
            '_id': str(ObjectId(book['_id'])),
            'name': book.get('name'),
            'description': book.get('description'),
            'author': book.get('author'),
            'categories': book.get('categories')
        }
    }), 200


@books_blueprint.route('/books/<id>', methods=['DELETE'])
@jwt_required()
@user_access_required(action='delete', name='not_found', pass_user_id=True)
def deleteBook(id, user_id):
    book = mongo.db.books.find_one({'_id': ObjectId(id)})
    if not book:
        return jsonify({'msg': 'Book not found',
                        'status': {
                            'name': 'not_found',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 400

    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401

    mongo.db.books.delete_one({'user_id': user_id, '_id': ObjectId(id)})
    return jsonify({'msg': 'Book deleted',
                    'status': {
                        'name': 'deleted',
                        'action': 'delete',
                        'delete': True
                    }
                    }), 202


@books_blueprint.route('/books/<id>', methods=['PUT'])
@jwt_required()
@user_access_required(action='update', name='not_updated', pass_user_id=True)
def updateBook(id, user_id):
    book = request.json.get('book')
    if not book:
        return jsonify({'msg': 'No book provided',
                        'status': {
                            'name': 'not_updated',
                            'action': 'update',
                            'update': False
                        }
                        }), 400

    db_book = mongo.db.books.find_one({'_id': ObjectId(id)})
    if not db_book:
        return jsonify({'msg': 'Book not found',
                        'status': {
                            'name': 'not_found',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 400
    
    if not validate_admin(user_id):
        return jsonify({'msg': 'You are not administrator',
                        'status': {
                            'name': 'not_authorized',
                            'action': 'delete',
                            'delete': False
                        }
                        }), 401

    if not validate_book(book):
        return jsonify({'msg': 'Invalid book',
                        'status': {
                            'name': 'not_updated',
                            'action': 'update',
                            'update': False
                        }
                        }), 400

    mongo.db.books.update_one({'_id': ObjectId(id)},
                              {'$set': book})
    return jsonify({'msg': 'Book updated',
                    'status': {
                        'name': 'updated',
                        'action': 'update',
                        'update': True
                    }
                    }), 202