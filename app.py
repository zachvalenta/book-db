import json

from flask import Flask, jsonify, request, Response

# TODO: swap out `jsonify()`
# TODO: add PATCH
# TODO: add DELETE
# TODO: 研究 Location header, sets, mimetype

app = Flask(__name__)


# UTIL

books = []


def check_keys_present(req):
    required_keys = {'isbn', 'name', 'price'}
    request_keys = set(req.keys())
    overlap = required_keys.intersection(request_keys) == required_keys
    return True if overlap else False


def handle_extraneous_keys(book):
    return {
        'name': book['name'],
        'price': book['price'],
        'isbn': book['isbn'],
    }


def lookup_by_isbn(lookup):
    for book in books:
        if book['isbn'] == lookup:
            return book

# ROUTES


@app.route('/books')
def get_books():
    return jsonify({'books': books})


@app.route('/books/count')
def get_books_count():
    return jsonify({'book_count': len(books)})


@app.route('/books/<string:isbn>')
def get_book(isbn):
    book_found = lookup_by_isbn(isbn)
    if book_found:
        return jsonify({'book': book_found})
    else:
        res = Response('no book found', 404)
        return res


@app.route('/books', methods=['POST'])
def post_book():
    new_book = request.get_json()
    if lookup_by_isbn(new_book['isbn']):
        return Response('book already exists', 400)
    if not check_keys_present(new_book):
        return Response('keys missing', 400)
    validated_book = handle_extraneous_keys(new_book)
    books.insert(0, validated_book)
    res = Response(json.dumps(new_book), 201, mimetype='application/json')
    res.headers['Location'] = '{}{}'.format('/books/', str(validated_book['isbn']))
    return res


@app.route('/books/<string:isbn>', methods=['PUT'])
def put_book(isbn):
    new_book = request.get_json()
    book_to_update = lookup_by_isbn(isbn)
    if not book_to_update:
        return Response('no book to update', 404)
    if not check_keys_present(new_book):
        return Response('keys missing', 400)
    else:
        validated_book = handle_extraneous_keys(new_book)
        books[books.index(book_to_update)] = validated_book
        return Response(json.dumps(validated_book), 200, mimetype='application/json')


@app.route('/books/clear', methods=['DELETE'])
def delete_books():
    books.clear()
    return Response('', 204)
