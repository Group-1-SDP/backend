from flask_sqlalchemy import SQLAlchemy
import random 
import string 

db = SQLAlchemy()

def generateString():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=5))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(5), default=generateString, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
