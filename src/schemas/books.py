import cerberus

book_schema = {
    'name': {'type': 'string', 'required': False},
    'description': {'type': 'string', 'required': False},
    'author': {'type': 'string', 'required': False},
    'categories': {'type': 'list', 'minlength': 1, 'schema': {'type': 'string'}, 'required': False}
}

def validate_book(book):
    return cerberus.Validator(book_schema).validate(book)

