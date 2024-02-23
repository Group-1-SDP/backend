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
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.String(10), primary_key=True)
    task_id = db.Column(db.String(5), default=generateString, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    contents = db.Column(db.String(200), nullable=False)
