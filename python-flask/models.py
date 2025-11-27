from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="Demo User")
    lat = db.Column(db.Float, default=21.1702)
    lon = db.Column(db.Float, default=72.8311)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    service_radius_km = db.Column(db.Float, default=5.0)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Drone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    battery_percent = db.Column(db.Float, default=100)
    status = db.Column(db.String(20), default='idle')  # idle, delivering

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    restaurant_id = db.Column(db.Integer)
    menu_json = db.Column(db.String(500))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    assigned_drone_id = db.Column(db.Integer, default=None)
    eta_minutes = db.Column(db.Float, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
