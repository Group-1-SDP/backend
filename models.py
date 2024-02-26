from flask_sqlalchemy import SQLAlchemy
import random 
import string 

db = SQLAlchemy()

def generateString():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=5))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(5), default=generateString, unique=True, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    # tasks completed total
    total_tasks_completed = db.Column(db.Integer, default=0, nullable=False)
    # phone in box time (seconds?)
    phone_in_box_time = db.Column(db.Integer, default=0, nullable=False)
    # phone currently in box
    phone_in_box_rn = db.Column(db.Boolean, default=False, nullable=False)
    # friends (array of ids)
    friends = db.Column(db.String(200), default="", nullable=False)


class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.String(5), default=generateString, nullable=False, unique=True, primary_key=True)
    user_with_task = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    # completion time
    contents = db.Column(db.String(200), nullable=False)
