from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)