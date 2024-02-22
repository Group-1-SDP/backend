from flask_login import UserMixin
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

import random

from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Int(5), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, email, password, username):
        self.id = self.generate_random_id()
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.username = username

    def generate_random_id(self):
        # Currently doesn't check for duplicates
        return random.randint(10000, 99999)