from app import app, mongo
import os   

def validate_author(author):
    _author = mongo.db.authors.find_one({'author': author})
    if not _author:
        return False
    return True

def validate_category(category):
    return True if mongo.db.books.find_one({'categories': category}) else False

def validate_bookName(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS_BOOKS']

def validate_bookFile(book):
    if book and validate_bookName(book.filename):
        filename = book.filename
        book.save(os.path.join(os.getcwd() + app.config['BOOKS_PATH'], filename))
        return filename