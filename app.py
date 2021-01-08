from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'qwertyuiop'
DB_NAME = 'IMDB'
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}.db'.format(DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

@app.route('/', methods=['GET'])
def test():
    return 'Hello world'

if __name__ == '__main__':
    app.run(debug=True)