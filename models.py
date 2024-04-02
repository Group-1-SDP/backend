from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

import random 
import string 
from datetime import datetime

db = SQLAlchemy()

def generateString():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=15))

friendship_association = Table(
    'friendship',
    db.Model.metadata,
    Column('user_id', String(15), ForeignKey('user.id')),
    Column('friend_id', String(15), ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.String(15), default=generateString, unique=True, primary_key=True)

    # user info
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255), default='koala.jpg')

    # social
    level = db.Column(db.Integer, default=1)
    current_xp = db.Column(db.Integer, default=0)
    leagues = db.relationship('LeagueMembership', backref='user', lazy=True)
    friends = db.relationship(
        'User', 
        secondary=friendship_association,
        primaryjoin=id==friendship_association.c.user_id,
        secondaryjoin=id==friendship_association.c.friend_id,
        backref='friend_of',
        lazy='dynamic'
    )

    # study
    progress_today = db.Column(db.Float, default=0.0)
    study_hours_today = db.Column(db.Float, default=0.0)
    study_hours_last_5 = db.Column(db.String(255), default='0,0,0,0,0')

    study_goal_daily = db.Column(db.Float, default=50)
    study_goal_session = db.Column(db.Float, default=25)

    tasks = db.relationship('Task', backref='user', lazy=True)

    # time tracking phone
    phone_in_box_current = db.Column(db.Boolean, default=False)
    last_phone_in_box_time = db.Column(db.DateTime, nullable=True)

    # settings
    notification_detection_enabled = db.Column(db.Boolean, default=False)
    tickagotchi_enabled = db.Column(db.Boolean, default=False)
    scheduling_enabled = db.Column(db.Boolean, default=False)
    custom_words_list = db.Column(db.String, default="")
    
    
class Task(db.Model):
    id = db.Column(db.String(15), default=generateString, unique=True, primary_key=True)
    user_id = db.Column(db.String(15), db.ForeignKey('user.id'), nullable=False)

    # content
    content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

class League(db.Model):
    id = db.Column(db.String(15), default=generateString, unique=True, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('LeagueMembership', backref='league', lazy=True)

class LeagueMembership(db.Model):
    id = db.Column(db.String(15), default=generateString, primary_key=True)
    league_id = db.Column(db.String(15), db.ForeignKey('league.id'), nullable=False)
    user_id = db.Column(db.String(15), db.ForeignKey('user.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)



