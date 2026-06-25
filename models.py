from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(14), nullable = False)
    role = db.Column(db.String(50), nullable = False)
    is_approved = db.Column(db.Boolean, default = True)
    is_blacklisted = db.Column(db.Boolean, default = False)



class Bootcamp(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    difficulty = db.Column(db.String(50))
    slots_available = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String(100), default = 'Open')
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = True)
    mentor  = db.relationship('User', foreign_keys = [mentor_id])
    bookings = db.relationship('Booking', backref='bootcamp', lazy = True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bootcamp_id = db.Column(db.Integer, db.ForeignKey('bootcamp.id'))
    status = db.Column(db.String(50), default = 'Booked') 
    user = db.relationship('User', foreign_keys = [user_id])