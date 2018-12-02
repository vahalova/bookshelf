import os
import fnmatch
import datetime
import collections
import json
from pathlib import Path

from flask import Flask, render_template, url_for, abort, send_from_directory, jsonify
from flask_frozen import Freezer
from elsa import cli
import yaml
import jinja2
import markdown

app = Flask(__name__)
MISSING = object()

base = Path(app.root_path) / "covers"


@app.route('/data/')
def data():
    books = read_yaml('books.yml')
    tags = set()
    language = set()
    today = datetime.date.today()
    for key, value in books.items():
        value['img_url'] = '/img/' + str(key) + ".jpg"
        value['book_url'] = '/' + str(key)
        for book in value['copies']:
            if 'borrowed' in book:
                book['days'] = (today - book['borrowed']).days
        tags.update(value['tags'])
        language.update(value['language'])
    return jsonify({'books':books, 'tags':sorted(tags), 'language':sorted(language)})


@app.route('/')
def index():
    books = read_yaml('books.yml')
    if books is None:
        abort(404)
    today = datetime.date.today()
    return render_template('index.html', books=books,today=today,)


@app.route('/<book_slug>/')
def book(book_slug):
    books = read_yaml('books.yml')
    book = books.get(book_slug)
    if book is None:
        abort(404)
    today = datetime.date.today()
    return render_template(
        'book.html',
        book_slug=book_slug,
        book=book,
        today=today,
    )


@app.route('/info/')
def info():
    return render_template('info.html')


@app.route('/img/<book_slug>.jpg')
def image(book_slug):
    name = find_photo(book_slug)
    return send_from_directory(base, name)


def find_photo(book_slug):
    name = book_slug + '.jpg'
    path = base/name
    if path.exists():
        return name
    return "python.png"


def pathto(name, static=False):
    if static:
        prefix = '_static/'
        if name.startswith(prefix):
            return url_for('static', filename=name[len(prefix):])
        return name
    return url_for(name)


def read_yaml(filename, default=MISSING):
    try:
        file = open(filename, encoding='utf-8')
    except FileNotFoundError:
        if default is MISSING:
            raise
        return default
    with file:
        data = yaml.safe_load(file)
    return data


@app.context_processor
def inject_context():
    return {'pathto': pathto, 'today': datetime.date.today(),}


if __name__ == '__main__':
    cli(app, base_url='')