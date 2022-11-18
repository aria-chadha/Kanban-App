from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()
#<------------------------------------------MODELS------------------------------------------------>

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(100), primary_key=True, nullable="False") 
    username = db.Column(db.String(100),nullable="False")
    password = db.Column(db.String(100),nullable="False")

class List(db.Model):
    __tablename__ = 'list'
    
    list_id = db.Column(db.String(100),primary_key=True)
    list_name = db.Column(db.String(100))
    creator_id = db.Column(db.String(100), nullable=False)
    updated_on = db.Column(db.DateTime)


class Card(db.Model):
    __tablename__ = 'card'

    creator_id = db.Column(db.String(100), nullable=False)
    list_id = db.Column(db.String(100), nullable=False)
    card_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    created_on = db.Column(db.DateTime, nullable=True)
    complete_flag= db.Column(db.Boolean, default=False)
    completed_on = db.Column(db.DateTime, nullable=True)
    


