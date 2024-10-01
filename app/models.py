from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, default=0)

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    resources = db.Column(db.String(150), nullable=False)  # e.g., "2 CPU, 4GB RAM"
    cost = db.Column(db.Integer, nullable=False)  # Cost in credits
    cpus = db.Column(db.Integer, nullable=False)  # Number of CPU cores
    ram = db.Column(db.Integer, nullable=False)  # Amount of RAM in MB


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
